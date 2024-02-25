import os
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]="test-web-scraping"

urls = ["https://mp.weixin.qq.com/s/Zklc3p5uosXZ7XMHD1k2QA"]

def quick_start():

    from langchain_community.document_loaders import AsyncChromiumLoader
    from langchain_community.document_transformers import BeautifulSoupTransformer

    # Load HTML
    loader = AsyncChromiumLoader(urls)
    html = loader.load()

    print("============= html =====================")
    print(html)

    # Transform
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=["span", "code", "p"])

    print("================= doc_transformed ===============")
    print(docs_transformed)
    
# quick_start()
    

    
def learn_AsyncHtmlLoader():
    from langchain_community.document_loaders import AsyncHtmlLoader
    
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()
    print("============= docs =====================")
    print(docs)
    
    from langchain_community.document_transformers import Html2TextTransformer

    html2text = Html2TextTransformer()
    docs_transformed = html2text.transform_documents(docs)
    print("================= doc_transformed ===============")
    print(docs_transformed)
    
# learn_AsyncHtmlLoader()

def scraping_with_extraction():
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
    
    from langchain.chains import create_extraction_chain

    schema = {
        "properties": {
            "文章标题": {"type": "string", "description": "文章题目"},
            "文章正文全部内容": {"type": "string", "description": "文章的正文内容，不要包含Python代码，只输出文字"},
            "文章中的示例Python代码": {"type": "string", "description": "文章中的Python代码，只输出代码，用markdonw格式输出，可能存在多段代码，多段代码之间分开"},
        },
        "required": ["文章标题", "文章正文全部内容", "文章中的示例Python代码"],
    }

    def extract(content: str, schema: dict):
        print("=========== content ==============")
        print(content)
        return create_extraction_chain(schema=schema, llm=llm, verbose=True).run(content)
    
    import pprint

    from langchain.text_splitter import RecursiveCharacterTextSplitter


    def scrape_with_playwright(urls, schema):
        from langchain_community.document_loaders import AsyncChromiumLoader
        from langchain_community.document_transformers import BeautifulSoupTransformer
        loader = AsyncChromiumLoader(urls)
        docs = loader.load()
        bs_transformer = BeautifulSoupTransformer()
        docs_transformed = bs_transformer.transform_documents(
            docs, tags_to_extract=["span", "code", "p"]
        )
        print("Extracting content with LLM")

        # Grab the first 1000 tokens of the site
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000, chunk_overlap=0
        )
        splits = splitter.split_documents(docs_transformed)

        # Process the first split
        extracted_content = extract(schema=schema, content=docs_transformed)
        pprint.pprint(extracted_content)
        return extracted_content

    extracted_content = scrape_with_playwright(urls, schema=schema)
    
scraping_with_extraction()

import asyncio
import requests
url = "https://github.com/trending"
async def test(url):
    context = requests.get(url)
    print(context)
    import aiohttp
    async with aiohttp.ClientSession() as client:
        async with client.get(url) as response:
            response.raise_for_status()
            html = await response.text()
            print(html)
    
# asyncio.run(test(url))
    
                
                