import os
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["SERPAPI_API_KEY"] = os.getenv('SERPAPI_API_KEY')

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

########################### 生成模型封装 #################################
llm = OpenAI()  # 默认是text-davinci-003模型
print("llm: ", llm.predict("你好，欢迎"))

############################ 对话模型封装 ####################################
chat_model = ChatOpenAI()  # 默认是gpt-3.5-turbo
print("chat_model: ", chat_model.predict("你好，欢迎"))

########################### 多轮对话session封装 ################################
from langchain.schema import (
    AIMessage, #等价于OpenAI接口中的assistant role
    HumanMessage, #等价于OpenAI接口中的user role
    SystemMessage #等价于OpenAI接口中的system role
)

messages = [
    SystemMessage(content="你是AGIClass的课程助理。"), 
    HumanMessage(content="我来上课了") 
]
print("多轮对话封装: ", chat_model(messages))

############################ prompt模板封装 ####################################
from langchain.prompts import PromptTemplate
template = PromptTemplate.from_template("给我讲个关于{subject}的笑话")
print(template.input_variables)
print(template.format(subject='小明'))

############################## chatprompt封装 ###################################
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
template = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template("你是{product}的客服助手。你的名字叫{name}"),
        HumanMessagePromptTemplate.from_template("{query}"),
    ]
)
response = chat_model(template.format_messages(
    product="AGIClass",
    name="某某某",
    query="你叫什么名字"
))

print("chatprompt封装: ", response)

######################### fewshot prompt template ########################
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

llm = OpenAI()
response = llm(prompt)

print("===Response===")
print(response)

