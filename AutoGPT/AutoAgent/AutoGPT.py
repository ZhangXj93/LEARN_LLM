from typing import List, Optional, Tuple

from langchain.chat_models.base import BaseChatModel
from langchain.llms import BaseLLM
from langchain.memory import ConversationTokenBufferMemory, VectorStoreRetrieverMemory
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.schema.output_parser import StrOutputParser
from langchain.tools.base import BaseTool
from langchain.vectorstores.base import VectorStoreRetriever
from pydantic import ValidationError

from AutoAgent.Action import Action
from Utils.PromptTemplateBuilder import PromptTemplateBuilder
from Utils.PrintUtils import *

class AutoGPT:
    """AutoGPT：基于Langchain实现"""

    def __init__(
            self,
            llm: BaseLLM,
            prompts_path: str,
            tools: List[BaseTool],
            work_dir: str = "./data",
            main_prompt_file: str = "main.json",
            final_prompt_file: str = "final_step.json",
            agent_name: Optional[str] = "瓜瓜",
            agent_role: Optional[str] = "强大的AI助手，可以使用工具与指令自动化解决问题",
            max_thought_steps: Optional[int] = 10,
            memery_retriever: Optional[VectorStoreRetriever] = None,
    ):
        self.llm = llm
        self.prompts_path = prompts_path
        self.tools = tools
        self.work_dir = work_dir
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.max_thought_steps = max_thought_steps
        self.memery_retriever = memery_retriever

        # OutputFixingParser： 如果输出格式不正确，尝试修复
        self.output_parser = PydanticOutputParser(pydantic_object=Action)
        self.robust_parser = OutputFixingParser.from_llm(parser=self.output_parser, llm=self.llm)

        self.main_prompt_file = main_prompt_file
        self.final_prompt_file = final_prompt_file

    def _find_tool(self, tool_name: str) -> Optional[BaseTool]:
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None

    def _step(self,
              reason_chain,
              task_description,
              short_term_memory,
              long_term_memory,
              verbose=False
        ) -> Tuple[Action, str]:

        """执行一步思考"""

        response = ""
        for s in reason_chain.stream({
                "short_term_memory": short_term_memory.load_memory_variables({})["history"],
                "long_term_memory" : long_term_memory.load_memory_variables(
                    {"prompt": task_description}
                )["history"] if long_term_memory is not None else "",
            }):
            if verbose:
                color_print(s, THOUGHT_COLOR, end="")
            response += s

        action = self.robust_parser.parse(response)
        return (action, response)

    def _final_step(self, short_term_memory, task_description) -> str:
        """最后一步, 生成最终的输出"""
        finish_prompt = PromptTemplateBuilder(
            self.prompts_path,
            self.final_prompt_file,
        ).build().partial(
            ai_name=self.agent_name,
            ai_role=self.agent_role,
            task_description=task_description,
            short_term_memory=short_term_memory.load_memory_variables({})["history"],
        )
        chain = ( finish_prompt | self.llm | StrOutputParser() )
        response = chain.invoke({})
        return response

    def _exec_action(self, action: Action) -> str:
        # 查找工具
        tool = self._find_tool(action.name)
        #action_expr = format_action(action)
        if tool is None:
            observation = (
                f"Error: 找不到工具或指令 '{action.name}'. "
                f"请从提供的工具/指令列表中选择，请确保按对顶格式输出。"
            )

        else:
            try:
                # 执行工具
                observation = tool.run(action.args)
            except ValidationError as e:
                # 工具的入参异常
                observation = (
                    f"Validation Error in args: {str(e)}, args: {action.args}"
                )
            except Exception as e:
                # 工具执行异常
                observation = f"Error: {str(e)}, {type(e).__name__}, args: {action.args}"

        return observation


    def _format_plan(self,response):
        plan_start = response.find("计划:")
        if plan_start == -1:
            plan_start = 0
        plan = response[plan_start:]
        return plan

    def run(self, task_description, verbose=False) -> str:
        thought_step_count = 0 # 思考步数

        # 初始化模板
        prompt_template = PromptTemplateBuilder(
            self.prompts_path,
            self.main_prompt_file,
        ).build(
            tools=self.tools,
            output_parser=self.output_parser,
        ).partial(
            work_dir=self.work_dir,
            ai_name=self.agent_name,
            ai_role=self.agent_role,
            task_description=task_description,
        )

        short_term_memory = ConversationTokenBufferMemory(
            llm=self.llm,
            ai_prefix="",
            human_prefix="",
            max_token_limit=4000,
        )

        short_term_memory.save_context(
            {"input": "\n初始化"},
            {"output": "\n开始"}
        )

        # 初始化LLM链
        chain = ( prompt_template | self.llm | StrOutputParser() )

        # 如果有长时记忆，加载长时记忆
        if self.memery_retriever is not None:
            long_term_memory = VectorStoreRetrieverMemory(
                retriever=self.memery_retriever,
            )
        else:
            long_term_memory = None

        reply = ""

        while thought_step_count < self.max_thought_steps:
            if verbose:
                color_print(f">>>>Round: {thought_step_count}<<<<",ROUND_COLOR)

            action, response = self._step(
                chain,
                task_description=task_description,
                short_term_memory=short_term_memory,
                long_term_memory=long_term_memory,
                verbose=verbose,
            )

            if action.name == "FINISH":
                if verbose:
                    color_print(f"\n----\nFINISH",OBSERVATION_COLOR)

                reply = self._final_step(short_term_memory, task_description)
                break

            observation = self._exec_action(action)

            if verbose:
                color_print(f"\n----\n结果:\n{observation}",OBSERVATION_COLOR)

            # 保存到短时记忆
            short_term_memory.save_context(
                {"input": response},
                {"output": "返回结果:\n"+observation}
            )

            thought_step_count += 1

        if not reply:
            reply = "抱歉，我没能完成您的任务。"

        if long_term_memory is not None:
            # 保存到长时记忆
            long_term_memory.save_context(
                {"input": task_description},
                {"output": reply}
            )

        return reply

