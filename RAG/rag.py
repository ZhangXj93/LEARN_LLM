from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


class PDFFileLoader():
    def __init__(self, file) -> None:
        self.paragraphs = self.extract_text_from_pdf(file, page_numbers=[0,3])
        i = 1
        for para in self.paragraphs:
            print(f"========= 第{i}段 ==========")
            print(para+"\n")
            i += 1
    
    def getParagraphs(self):
        return self.paragraphs

    ################################# 文档的加载与切割 ############################
    def extract_text_from_pdf(self, filename, page_numbers=None):
        '''从 PDF 文件中（按指定页码）提取文字'''
        paragraphs = []
        buffer = ''
        full_text = ''
        # 提取全部文本
        for i, page_layout in enumerate(extract_pages(filename)):
            # 如果指定了页码范围，跳过范围外的页
            if page_numbers is not None and i not in page_numbers:
                continue
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    full_text += element.get_text() + '\n'
        
        # 段落分割
        lines = full_text.split('。\n')
        for text in lines:
            buffer = text.strip(' ').replace('\n', ' ').replace('[', '').replace(']', '') ## 1. 去掉特殊字符
            if len(buffer) < 10: ## 2. 过滤掉长度小于 10 的段落，这可能会导致一些信息丢失，慎重使用，实际生产中不能用
                continue
            if buffer:
                paragraphs.append(buffer)
                buffer = ''
                row_count = 0
                
        if buffer and len(buffer) > 10: ## 3. 过滤掉长度小于 10 的段落，这可能会导致一些信息丢失，慎重使用，实际生产中不能用
            paragraphs.append(buffer)
        return paragraphs

# pdf_loader = PDFFileLoader("D:\GitHub\LEARN_LLM\RAG\如何向 ChatGPT 提问以获得高质量答案：提示技巧工程完全指南.pdf")

from openai import OpenAI
import os
# 加载环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())  # 读取本地 .env 文件，里面定义了 OPENAI_API_KEY

client = OpenAI()

def get_embeddings(texts, model="text-embedding-3-small"):
    '''封装 OpenAI 的 Embedding 模型接口'''
    data = client.embeddings.create(input=texts, model=model).data
    return [x.embedding for x in data]

import chromadb
from chromadb.config import Settings

class MyVectorDBConnector:
    def __init__(self, collection_name, embedding_fn):
        chroma_client = chromadb.Client(Settings(allow_reset=True))

        # 为了演示，实际不需要每次 reset()
        chroma_client.reset()

        # 创建一个 collection
        self.collection = chroma_client.get_or_create_collection(name=collection_name)
        self.embedding_fn = embedding_fn

    def add_documents(self, documents):
        '''向 collection 中添加文档与向量'''
        self.collection.add(
            embeddings=self.embedding_fn(documents),  # 每个文档的向量
            documents=documents,  # 文档的原文
            ids=[f"id{i}" for i in range(len(documents))]  # 每个文档的 id
        )

    def search(self, query, top_n):
        '''检索向量数据库'''
        results = self.collection.query(
            query_embeddings=self.embedding_fn([query]),
            n_results=top_n
        )
        return results

# # 创建一个向量数据库对象
# vector_db = MyVectorDBConnector("demo", get_embeddings)
# # 向向量数据库中添加文档
# vector_db.add_documents(pdf_loader.getParagraphs())

# user_query = "什么是角色提示？"
# results = vector_db.search(user_query, 3)
# for para in results['documents'][0]:
#     print(para+"\n\n")

def build_prompt(prompt_template, **kwargs):
    '''将 Prompt 模板赋值'''
    prompt = prompt_template
    for k, v in kwargs.items(): 
        if isinstance(v,str):
            val = v
        elif isinstance(v, list) and all(isinstance(elem, str) for elem in v):
            val = '\n'.join(v)
        else:
            val = str(v)
        prompt = prompt.replace(f"__{k.upper()}__",val)
    return prompt

prompt_template = """
你是一个问答机器人。
你的任务是根据下述给定的已知信息回答用户问题。
确保你的回复完全依据下述已知信息。不要编造答案。
如果下述已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。

已知信息:
__INFO__

用户问：
__QUERY__

请用中文回答用户问题。
"""

########################### 大模型接口封装 #############################

def get_completion(prompt, model="gpt-3.5-turbo-1106"):
    '''封装 openai 接口'''
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content

# prompt = build_prompt(prompt_template, info=results['documents'][0], query=user_query)
# print(prompt)

# response = get_completion(prompt)
# print(response)


##################################  基于向量检索的 RAG ##################
class RAG_Bot:
    def __init__(self, n_results=2):
        self.llm_api = get_completion
        self.n_results = n_results

    def createVectorDB(self, file):
        print(file)
        pdf_loader = PDFFileLoader(file)
        # 创建一个向量数据库对象
        self.vector_db = MyVectorDBConnector("demo", get_embeddings)
        # 向向量数据库中添加文档，灌入数据
        self.vector_db.add_documents(pdf_loader.getParagraphs())

    def chat(self, user_query):
        # 1. 检索
        search_results = self.vector_db.search(user_query,self.n_results)
        
        # 2. 构建 Prompt
        prompt = build_prompt(prompt_template, info=search_results['documents'][0], query=user_query)
        
        # 3. 调用 LLM
        response = self.llm_api(prompt)
        return response


rag_bot = RAG_Bot()
rag_bot.createVectorDB("D:\GitHub\LEARN_LLM\RAG\如何向 ChatGPT 提问以获得高质量答案：提示技巧工程完全指南.pdf")
response = rag_bot.chat("什么是角色提示？")
print(response)