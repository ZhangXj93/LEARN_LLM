import os
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

from langchain_openai import ChatOpenAI

llm = ChatOpenAI() # 默认是gpt-3.5-turbo

def test():
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    prompt_template = """
    我的名字叫【{name}】，我的个人介绍是【{description}】。
    请根据我的名字和介绍，帮我想一段有吸引力的自我介绍的句子，以此来吸引读者关注和点赞我的账号。
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    response = chain.invoke({"name": "同学小张", "description": "热爱AI，持续学习，持续干货输出"})
    print(response)
    
## 1. 文档加载
from langchain.document_loaders import PyPDFLoader
loader = PyPDFLoader("D:\GitHub\LEARN_LLM\RAG\如何向 ChatGPT 提问以获得高质量答案：提示技巧工程完全指南.pdf")
pages = loader.load_and_split()

## 2. 文档切分
from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=100,
    length_function=len,
    add_start_index=True,
)
paragraphs = []
for page in pages:
    paragraphs.extend(text_splitter.create_documents([page.page_content]))

## 3. 文档向量化，向量数据库存储
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
db = Chroma.from_documents(paragraphs, OpenAIEmbeddings())

## 4. 向量检索
retriever = db.as_retriever()

## 5. 组装Prompt模板
prompt_template = """
你是一个问答机器人。
你的任务是根据下述给定的已知信息回答用户问题。
确保你的回复完全依据下述已知信息。不要编造答案。
如果下述已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。

已知信息:
{info}

用户问：
{question}

请用中文回答用户问题。
"""

from langchain.prompts import PromptTemplate
template = PromptTemplate.from_template(prompt_template)

from langchain_core.runnables import RunnableParallel, RunnablePassthrough
setup_and_retrieval = RunnableParallel(
    {"question": RunnablePassthrough(), "info": retriever}
)

## 6. 执行chain
chain = setup_and_retrieval | template | llm
response = chain.invoke("什么是角色提示？")
print(response.content)
















    