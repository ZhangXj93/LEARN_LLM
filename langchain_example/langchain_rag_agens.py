# import os
# os.environ["LANGCHAIN_TRACING_V2"]="true"
# os.environ["LANGCHAIN_PROJECT"]="test-langchain-rag"

import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load, chunk and index the contents of the blog.
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
# vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(), persist_directory="./chroma.db")

vectorstore = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory="./chroma.db")

# Retrieve and generate using the relevant snippets of the blog.
retriever = vectorstore.as_retriever()

from langchain.tools.retriever import create_retriever_tool

tool = create_retriever_tool(
    retriever,
    "search_agents_answer",
    "Searches and returns context from LLM Powered Autonomous Agents. Answering questions about the agents.",
)
tools = [tool]

from langchain import hub

prompt = hub.pull("hwchase17/openai-tools-agent")

prompt.pretty_print()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0)

from langchain.agents import AgentExecutor, create_openai_tools_agent

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = agent_executor.invoke({"input": "hi, 我是【同学小张】"})

print(result["output"])

result = agent_executor.invoke(
    {
        "input": "What is Task Decomposition?"
    }
)

print("output2: ", result["output"])