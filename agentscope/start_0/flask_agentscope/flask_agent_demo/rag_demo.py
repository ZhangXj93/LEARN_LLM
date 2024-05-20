from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from openai import OpenAI

client = OpenAI()

class PDFFileLoader():
    """ 加载PDF文件, 将PDF内容分割成段落 """
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

def get_embeddings(texts, model="text-embedding-3-small"):
    '''封装 OpenAI 的 Embedding 模型接口'''
    data = client.embeddings.create(input=texts, model=model).data
    return [x.embedding for x in data]

import chromadb
from chromadb.config import Settings

class MyVectorDBConnector:
    def __init__(self, collection_name, embedding_fn, persistence_directory):
        chroma_client = chromadb.Client(Settings(persist_directory=persistence_directory, is_persistent=True, allow_reset=True))
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


##################################  基于向量检索的 RAG ##################
class RAGDemo:
    def __init__(self, persistence_directory):
        self.vector_db = MyVectorDBConnector("demo", get_embeddings, persistence_directory) # 创建一个向量数据库对象

    def createVectorDB(self, file):
        print("当前加载的文件：", file)
        pdf_loader = PDFFileLoader(file) # 读取pdf文件并分段
        self.vector_db.add_documents(pdf_loader.getParagraphs()) # 向向量数据库中添加文档，灌入数据

    def search(self, user_query, n_results=3):
        """根据用户问题，检索知识库相关片段
        Args:
            user_query (_type_): 用户问题
            n_results (int, optional): 检索最相关的n条知识库片段. 默认 3.
        """
        search_results = self.vector_db.search(user_query, n_results)
        return search_results


# if __name__ == "__main__":
#     rag_bot = RAG_Bot()
#     rag_bot.createVectorDB("D:\GitHub\LEARN_LLM\RAG\如何向 ChatGPT 提问以获得高质量答案：提示技巧工程完全指南.pdf")
#     response = rag_bot.chat("什么是角色提示？")
#     print("response=====================>")
#     print(response)