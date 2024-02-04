def pdf_loader_test():
    from langchain_community.document_loaders import PyPDFLoader

    loader = PyPDFLoader("D:\GitHub\LEARN_LLM\RAG\如何向 ChatGPT 提问以获得高质量答案：提示技巧工程完全指南.pdf")
    pages = loader.load_and_split()

    print(f"第0页：\n{pages[0]}")
    print(f"第0页：\n{pages[0].page_content}")


def online_pdf_loader_test():
    from langchain_community.document_loaders import OnlinePDFLoader
    
    loader = OnlinePDFLoader("https://arxiv.org/pdf/2302.03803.pdf")
    data = loader.load()
    print(data)

# online_pdf_loader_test()

def recursive_text_split_test():
    from langchain_community.document_loaders import PyPDFLoader

    loader = PyPDFLoader("D:\GitHub\LEARN_LLM\RAG\如何向 ChatGPT 提问以获得高质量答案：提示技巧工程完全指南.pdf")
    pages = loader.load_and_split()
    print(f"第0页：\n{pages[0].page_content}")
    
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )

    paragraphs = text_splitter.create_documents([pages[0].page_content])
    for para in paragraphs:
        print(para.page_content)
        print('-------')

# recursive_text_split_test()

def langchain_RAG_test():
    
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
    # query = "什么是角色提示？"
    # docs = db.similarity_search(query)
    # for doc in docs:
    #     print(f"{doc.page_content}\n-------\n")
    
    retriever = db.as_retriever()
    docs = retriever.get_relevant_documents("什么是角色提示？")
    for doc in docs:
        print(f"{doc.page_content}\n-------\n")
    
    ## 5. 组装Prompt模板
    import os
    # 加载 .env 到环境变量
    from dotenv import load_dotenv, find_dotenv
    _ = load_dotenv(find_dotenv())

    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI() # 默认是gpt-3.5-turbo
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
    prompt = template.format(info=docs[0].page_content, question='什么是角色提示？')
    ## 6. 调用LLM
    response = llm.invoke(prompt)
    print(response.content)    
    
langchain_RAG_test()