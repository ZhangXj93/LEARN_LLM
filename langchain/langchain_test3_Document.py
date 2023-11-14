import os
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
from langcodes import Language
_ = load_dotenv(find_dotenv())

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["SERPAPI_API_KEY"] = os.getenv('SERPAPI_API_KEY')

################### 文档加载器 ###################
from langchain.document_loaders import PyPDFLoader
loader = PyPDFLoader("D:\Learn\AGI\langchain\llama2.pdf")
pages = loader.load_and_split()

print("total page: ", len(pages), "\nthe first page content: ", \
    pages[0].page_content, "\nlast page content: ", pages[-1].page_content, "\n\n")

################### 文档处理器 ###################
###### TextSplitter #######

import re, wordninja

#预处理字符全都连在一起的行
def preprocess(text):
    def split(line):
        tokens = re.findall(r'\w+|[.,!?;%$-+=@#*/]', line)
        return [
            ' '.join(wordninja.split(token)) if token.isalnum() else token
            for token in tokens
        ]

    lines = text.split('\n')
    for i,line in enumerate(lines):
        if len(max(line.split(' '), key = len)) >= 20: 
            lines[i] = ' '.join(split(line))
    return ' '.join(lines) #按行组织，返回数组

from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=50,
    length_function=len,
    add_start_index=True,
)
paragraphs = text_splitter.create_documents([preprocess(pages[3].page_content)])
for para in paragraphs:
    print(para.page_content)
    print('-------')

# ####### document_transformers ####### #TODO: await错误
# from langchain.document_transformers import DoctranTextTranslator
# translator = DoctranTextTranslator(
#     openai_api_model = "gpt-3.5-turbo-1106",
#     language = "Chinese"
# )

# translated_document = await translator.atransform_documents([pages[3]])
# print(translated_document[0].page_content)

######## 检索与回答 ########
from langchain.retrievers import TFIDFRetriever  # 最传统的关键字加权检索
from langchain.text_splitter import RecursiveCharacterTextSplitter
import wordninja, re

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=60,  
    length_function=len,
    add_start_index=True,
)

# 取一个有信息量的章节（Introduction: 第2-3页）
paragraphs = text_splitter.create_documents(
    [preprocess(d.page_content) for d in pages]
)

user_query = "Does llama 2 have a dialogue version?"

retriever = TFIDFRetriever.from_documents(paragraphs)
docs = retriever.get_relevant_documents(user_query)

print(docs[0].page_content)

### 检索与回答2 通过ChatOpenAI ###
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI

template = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "你是问答机器人，你根据以下信息回答用户问题。\n" +
            "已知信息：\n{information}\n\nBe brief, and do not make up information."),
        HumanMessagePromptTemplate.from_template("{query}"),
    ]
)

llm = ChatOpenAI(temperature=0)
response = llm(
            template.format_messages(
                information=docs[0].page_content,
                query=user_query
            )
        )
print(response.content)

########## 向量检索初探 ###########
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

embeddings = OpenAIEmbeddings() 
db = FAISS.from_documents(paragraphs, embeddings) #Facebook的开源向量检索引擎

user_query = "llama 2有对话式的版本吗"

docs = db.similarity_search(user_query)
print("===检索结果===")
print(docs[0].page_content)

response = llm(
            template.format_messages(
                information=docs[0].page_content,
                query=user_query
            )
        )

print("===回答===")
print(response.content)



