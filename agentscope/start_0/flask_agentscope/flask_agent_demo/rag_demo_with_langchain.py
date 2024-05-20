##################################  基于向量检索的 RAG ##################
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class RAGDemo:
    def __init__(self, persistence_directory):
        self.persist_directory = persistence_directory
        self.vector_db = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory=self.persist_directory) # 创建一个向量数据库对象]
        self.text_spliter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True,
        )

    def createVectorDB(self, file):
        print("当前加载的文件：", file)
        if (file.endswith('.pdf')):
            paragraphs = self.__load_pdf(file)
        # elif (file.endswith('.doc') or file.endswith('.docx')):
        #     paragraphs = self.__load_word(file)
            
        print("开始写入向量数据库", file)
        self.vector_db = Chroma.from_documents(paragraphs, OpenAIEmbeddings(), persist_directory=self.persist_directory) # 向向量数据库中添加文档，灌入数据

    def search(self, user_query, n_results=3):
        """根据用户问题，检索知识库相关片段
        Args:
            user_query (_type_): 用户问题
            n_results (int, optional): 检索最相关的n条知识库片段. 默认 3.
        """
        retriever = self.vector_db.as_retriever()
        search_results = retriever.get_relevant_documents(user_query)
        docs=""
        for doc in search_results:
            print(f"{doc.page_content}\n-------\n")
            docs += f"{doc.page_content}\n"
        return docs
    
    def __load_pdf(self, file):
        ## 1. 文档加载
        loader = PyPDFLoader(file)
        pages = loader.load_and_split()
        
        ## 2. 文档切分
        print("开始切分文档", file)
        paragraphs = []
        for page in pages:
            paragraphs.extend(self.text_spliter.create_documents([page.page_content]))
        return paragraphs


# if __name__ == "__main__":
#     rag_bot = RAG_Bot()
#     rag_bot.createVectorDB("D:\GitHub\LEARN_LLM\RAG\如何向 ChatGPT 提问以获得高质量答案：提示技巧工程完全指南.pdf")
#     response = rag_bot.chat("什么是角色提示？")
#     print("response=====================>")
#     print(response)