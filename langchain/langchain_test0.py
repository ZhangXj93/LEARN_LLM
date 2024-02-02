import os
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

from langchain_openai import ChatOpenAI
 
llm = ChatOpenAI() # 默认是gpt-3.5-turbo

def llm_test():
    response = llm.invoke("你是谁")
    print(response.content)

########################### 多轮对话session封装 ################################
def llm_test2():
    from langchain.schema import (
        AIMessage, #等价于OpenAI接口中的assistant role
        HumanMessage, #等价于OpenAI接口中的user role
        SystemMessage #等价于OpenAI接口中的system role
    )

    messages = [
        SystemMessage(content="你是[同学小张]的个人助理。你叫[小明]"), 
        HumanMessage(content="我叫[同学小张]"), 
        AIMessage(content="好的老板，你有什么吩咐？"),
        HumanMessage(content="我是谁") 
    ]
    response = llm.invoke(messages)
    print(response.content)

############################ prompt模板封装 ####################################
def prompt_template_test():
    prompt_template = """
    我的名字叫【{name}】，我的个人介绍是【{description}】。
    请根据我的名字和介绍，帮我想一段有吸引力的自我介绍的句子，以此来吸引读者关注和点赞我的账号。
    """

    from langchain.prompts import PromptTemplate
    template = PromptTemplate.from_template(prompt_template)
    print(template.input_variables)
    prompt = template.format(name='同学小张', description='热爱AI，持续学习，持续干货输出')
    print(prompt)
    response = llm.invoke(prompt)
    print(response.content)


############################## chatprompt封装 ###################################
def chat_prompt_template_test():
    from langchain.prompts import ChatPromptTemplate
    from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
    template = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template("你是【{name}】的个人助手，你需要根据用户输入，来替用户生成一段有吸引力的自我介绍的句子，以此来吸引读者关注和点赞用户的账号。"),
            HumanMessagePromptTemplate.from_template("{description}"),
        ]
    )
    prompt = template.format(name="同学小张", description="热爱AI，持续学习，持续干货输出")
    
    print(prompt)
    response = llm.invoke(prompt)
    print(response.content)

######################### fewshot prompt template ########################
def few_shot_prompt_template_test():
    from langchain.prompts import PromptTemplate
    from langchain.prompts.few_shot import FewShotPromptTemplate
    #例子(few-shot)
    examples = [
        {
            "input": "北京天气怎么样",
            "output" : "北京市"
        },
        {
            "input": "南京下雨吗",
            "output" : "南京市"
        },
        {
            "input": "江城热吗",
            "output" : "武汉市"
        }
    ]

    #例子拼装的格式
    example_prompt = PromptTemplate(input_variables=["input", "output"], template="Input: {input}\nOutput: {output}")

    #Prompt模板
    prompt = FewShotPromptTemplate(
        examples=examples, 
        example_prompt=example_prompt, 
        suffix="Input: {input}\nOutput:", 
        input_variables=["input"]
    )

    prompt = prompt.format(input="羊城多少度")

    print("===Prompt===")
    print(prompt)

    response = llm.invoke(prompt)

    print("===Response===")
    print(response)

# few_shot_prompt_template_test()

def prompt_file_test():
    from langchain.prompts import load_prompt
    prompt = load_prompt("D:\GitHub\LEARN_LLM\langchain\langchain_prompt_file_test.json")
    prompt_str = prompt.format(name="同学小张", description="热爱AI，持续学习，持续干货输出")
    print(prompt_str)
    
    response = llm.invoke(prompt_str)
    print(f"\n{response}")
    
# prompt_file_test()

def output_parse_test():
    from langchain.output_parsers import PydanticOutputParser
    from langchain_core.pydantic_v1 import BaseModel, Field, validator
    from langchain.prompts import PromptTemplate
    
    # 定义你期望的数据结构
    class Joke(BaseModel):
        setup: str = Field(description="question to set up a joke")
        punchline: str = Field(description="answer to resolve the joke")

        # 使用Pydantic添加自定义的校验逻辑，如下为检测内容最后一个字符是否为问号，不为问号则提示错误.
        @validator("setup")
        def question_ends_with_question_mark(cls, field):
            if field[-1] != "?":
                raise ValueError("Badly formed question!")
            return field
        
    # 生成一个解析器的实例
    parser = PydanticOutputParser(pydantic_object=Joke)
    
    # 生成 Prompt 模板
    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    print(f"\n{parser.get_format_instructions()}")
    prompt_str = prompt.format(query="Tell me a joke.")
    print(prompt_str)
    response = llm.invoke(prompt_str)
    print(f"\n{response.content}")
    # response.content = response.content.replace("?", "") ## 认为改错结果，测试后面的OutputFixingParser
    try:
        parser_result = parser.invoke(response)
        print(f"\n{parser_result}")
    except Exception as e:
        print("===出现异常===")
        print(e)
        ## 1. 引入OutputFixingParser
        from langchain.output_parsers import OutputFixingParser
        ## 2. 使用之前的parser和llm，构建一个OutputFixingParser实例
        new_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
        ## 3. 用OutputFixingParser自动修复并解析
        parser_result = new_parser.parse(response.content)
        print("===重新解析结果===")
        print(parser_result)
    
    

    
    
output_parse_test()
    