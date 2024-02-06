

def langfuse_test_openai():
    from datetime import datetime
    from langfuse.openai import openai
    from langfuse import Langfuse 
    import os

    trace = Langfuse().trace(
        name = "hello-world",
        user_id = "同学小张",
        release = "v0.0.1"
    )

    completion = openai.chat.completions.create(
    name="hello-world",
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "对我说'Hello, World!'"}
    ],
    temperature=0,
    trace_id=trace.id,
    )

    print(completion.choices[0].message.content)
    
    
from langfuse.callback import CallbackHandler

handler = CallbackHandler(
    trace_name="SayHello",
    user_id="同学小张",
)

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import HumanMessage
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate

model = ChatOpenAI(model="gpt-3.5-turbo-0613")

prompt_template = """
我的名字叫【{name}】，我的个人介绍是【{description}】。
请根据我的名字和介绍，帮我想一段有吸引力的自我介绍的句子，以此来吸引读者关注和点赞我的账号。
"""
prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(prompt_template)
])

# 定义输出解析器
parser = StrOutputParser()

chain = (
    prompt
    | model
    | parser
)

## invoke的第一个参数，传入json格式的参数，key与prompt中的参数名一致
response = chain.invoke({'name': '同学小张', 'description': '热爱AI，持续学习，持续干货输出'}, config={"callbacks":[handler]})
print(response)