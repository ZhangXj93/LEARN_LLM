# import os
# os.environ["LANGCHAIN_TRACING_V2"]="true"
# os.environ["LANGCHAIN_PROJECT"]="test-langchain-rag"

from langchain_community.retrievers import WikipediaRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
wiki = WikipediaRetriever(top_k_results=3, doc_content_chars_max=2000)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You're a helpful AI assistant. Given a user question and some Wikipedia article snippets, answer the user question. If none of the articles answer the question, just say you don't know.\n\nHere are the Wikipedia articles:{context}",
        ),
        ("human", "{question}"),
    ]
)
# prompt.pretty_print()

from operator import itemgetter
from typing import List

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)


def format_docs(docs: List[Document]) -> str:
    """Convert Documents to a single string.:"""
    formatted = [
        f"Article Title: {doc.metadata['title']}\nArticle Snippet: {doc.page_content}"
        for doc in docs
    ]
    return "\n\n" + "\n\n".join(formatted)


format = itemgetter("docs") | RunnableLambda(format_docs)
# subchain for generating an answer once we've done retrieval
answer = prompt | llm | StrOutputParser()
# complete chain that calls wiki -> formats docs to string -> runs answer subchain -> returns just the answer and retrieved docs.
chain = (
    RunnableParallel(question=RunnablePassthrough(), docs=wiki)
    .assign(context=format)
    .assign(answer=answer)
    .pick(["answer", "docs"])
)

response = chain.invoke("How fast are cheetahs?")

print(response)