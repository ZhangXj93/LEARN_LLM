from agentscope.agents.react_agent import ReActAgent

import agentscope
from agentscope.message import Msg
import os

from agentscope.service import (
    ServiceToolkit,
    ServiceResponse,
    ServiceExecStatus,
)

openai_api_key = os.getenv('OPENAI_API_KEY')

# 此Agent的模型配置，按需修改
OPENAI_CFG_DICT = {
    "config_name": "openai_cfg",    # 此配置的名称，必须保证唯一
    "model_type": "openai",         # 模型类型
    "model_name": "gpt-3.5-turbo",  # 模型名称
    "api_key": openai_api_key,      # OpenAI API key. 如果没有设置，将使用环境变量中的 OPENAI_API_KEY
}

# Prepare a new tool function
def execute_python_code(code: str) -> ServiceResponse:  # pylint: disable=C0301
    """
    Execute Python code and capture the output. Note you must `print` the output to get the result.
    Args:
        code (`str`):
            The Python code to be executed.
    """  # noqa

    # Create a StringIO object to capture the output
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    try:
        # Using `exec` to execute code
        exec(code)
    except Exception as e:
        # If an exception occurs, capture the exception information
        output = str(e)
        status = ServiceExecStatus.ERROR
    else:
        # If the execution is successful, capture the output
        output = new_stdout.getvalue()
        status = ServiceExecStatus.SUCCESS
    finally:
        # Recover the standard output
        sys.stdout = old_stdout

    # Wrap the output and status into a ServiceResponse object
    return ServiceResponse(status, output)

def sum_num(a: int, b: int) -> int:
    """计算两个数的和

    Args:
        a (int): 参数1
        b (int): 参数2

    Returns:
        int: 结果
    """
    output = a + b
    status = ServiceExecStatus.SUCCESS
    return ServiceResponse(status, output)


class ToolDemo:
    def __init__(self):
        # Prepare the tools for the agent
        service_toolkit = ServiceToolkit()
        service_toolkit.add(sum_num)

        agentscope.init(model_configs=[OPENAI_CFG_DICT])

        self.agent = ToolUseAgent(
            name="assistant",
            model_config_name="openai_cfg",
            verbose=True,
            service_toolkit=service_toolkit,
            max_iters=1,
        )
        
    def invoke(self, query):
        msg = Msg("user", query, role="user")
        return self.agent(msg)
    

from typing import Any
from loguru import logger
from agentscope.exception import ResponseParsingError, FunctionCallError
from agentscope.agents import AgentBase
from agentscope.message import Msg
from agentscope.parsers import MarkdownJsonDictParser
from agentscope.service import ServiceToolkit
from agentscope.service.service_toolkit import ServiceFunction

class ToolUseAgent(AgentBase):

    def __init__(
        self,
        name: str,
        model_config_name: str,
        service_toolkit: ServiceToolkit = None,
        sys_prompt: str = "You're a helpful assistant. 你的名字是 {name}. 所有回复请使用中文回答",
        verbose: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the Tool use agent with the given name, model config name
        and tools.

        Args:
            name (`str`):
                The name of the agent.
            sys_prompt (`str`):
                The system prompt of the agent.
            model_config_name (`str`):
                The name of the model config, which is used to load model from
                configuration.
            service_toolkit (`ServiceToolkit`):
                A `ServiceToolkit` object that contains the tool functions.
            verbose (`bool`, defaults to `True`):
                Whether to print the detailed information during reasoning and
                acting steps. If `False`, only the content in speak field will
                be print out.
        """
        super().__init__(
            name=name,
            sys_prompt=sys_prompt,
            model_config_name=model_config_name,
        )
        self.max_iters = 1
        if service_toolkit is None:
            raise ValueError(
                "The argument `service_toolkit` is required to initialize "
                "the ReActAgent.",
            )

        self.service_toolkit = service_toolkit
        self.verbose = verbose

        if not sys_prompt.endswith("\n"):
            sys_prompt = sys_prompt + "\n"

        self.sys_prompt = "\n".join(
            [
                sys_prompt.format(name=self.name),
                self.service_toolkit.tools_instruction,
                # INSTRUCTION_PROMPT,
            ],
        )

        # Put sys prompt into memory
        self.memory.add(Msg("system", self.sys_prompt, role="system"))

        # Initialize a parser object to formulate the response from the model
        self.parser = MarkdownJsonDictParser(
            content_hint={
                "thought": "what you thought",
                "speak": "what you speak",
                "function": service_toolkit.tools_calling_format,
            },
            required_keys=["thought", "speak", "function"],
            # Only print the speak field when verbose is False
            keys_to_content=True if self.verbose else "speak",
        )

    def reply(self, x: dict = None) -> dict:

        self.memory.add(x)

        for _ in range(self.max_iters):
            # Step 1: Thought
            if self.verbose:
                self.speak(f" ITER {_+1}, STEP 1: REASONING ".center(70, "#"))

            # Prepare hint to remind model what the response format is
            # Won't be recorded in memory to save tokens
            hint_msg = Msg(
                "system",
                self.parser.format_instruction,
                role="system",
                echo=self.verbose,
            )

            # Prepare prompt for the model
            prompt = self.model.format(self.memory.get_memory(), hint_msg)

            # Generate and parse the response
            try:
                res = self.model(
                    prompt,
                    parse_func=self.parser.parse,
                    max_retries=1,
                )

                # Record the response in memory
                self.memory.add(
                    Msg(
                        self.name,
                        self.parser.to_memory(res.parsed),
                        "assistant",
                    ),
                )

                # Print out the response
                msg_returned = Msg(
                    self.name,
                    self.parser.to_content(res.parsed),
                    "assistant",
                )
                self.speak(msg_returned)

                # Skip the next steps if no need to call tools
                # The parsed field is a dictionary
                arg_function = res.parsed["function"]
                if (
                    isinstance(arg_function, str)
                    and arg_function in ["[]", ""]
                    or isinstance(arg_function, list)
                    and len(arg_function) == 0
                ):
                    # Only the speak field is exposed to users or other agents
                    return msg_returned

            # Only catch the response parsing error and expose runtime
            # errors to developers for debugging
            except ResponseParsingError as e:
                # Print out raw response from models for developers to debug
                response_msg = Msg(self.name, e.raw_response, "assistant")
                self.speak(response_msg)

                # Re-correct by model itself
                error_msg = Msg("system", str(e), "system")
                self.speak(error_msg)

                self.memory.add([response_msg, error_msg])

                # Skip acting step to re-correct the response
                continue

            # Step 2: Acting
            if self.verbose:
                self.speak(f" ITER {_+1}, STEP 2: ACTING ".center(70, "#"))

            # Parse, check and execute the tool functions in service toolkit
            try:
                execute_results = self.service_toolkit.parse_and_call_func(
                    res.parsed["function"],
                )

                # Note: Observing the execution results and generate response
                # are finished in the next reasoning step. We just put the
                # execution results into memory, and wait for the next loop
                # to generate response.

                # Record execution results into memory as system message
                msg_res = Msg("system", execute_results, "system")
                self.speak(msg_res)
                self.memory.add(msg_res)

            except FunctionCallError as e:
                # Catch the function calling error that can be handled by
                # the model
                error_msg = Msg("system", str(e), "system")
                self.speak(error_msg)
                self.memory.add(error_msg)

        # Exceed the maximum iterations
        hint_msg = Msg(
            "system",
            "You have failed to generate a response in the maximum "
            "iterations. Now generate a reply by summarizing the current "
            "situation.",
            role="system",
            echo=self.verbose,
        )

        # Generate a reply by summarizing the current situation
        prompt = self.model.format(self.memory.get_memory(), hint_msg)
        res = self.model(prompt)
        res_msg = Msg(self.name, res.text, "assistant")
        self.speak(res_msg)

        return res_msg

    
    
if __name__ == '__main__':
    tool_demo = ToolDemo()
    response = tool_demo.invoke("1+1=?")
    print(response)
