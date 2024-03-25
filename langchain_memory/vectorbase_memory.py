from langchain.memory import VectorStoreRetrieverMemory
from langchain_openai import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate

vectorstore = Chroma(embedding_function=OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_kwargs=dict(k=1))
memory = VectorStoreRetrieverMemory(retriever=retriever)

memory.save_context({"input": "我喜欢学习"}, {"output": "你真棒"})
memory.save_context({"input": "我不喜欢玩儿"}, {"output": "你可太棒了"})

PROMPT_TEMPLATE = """以下是人类和 AI 之间的友好对话。AI 话语多且提供了许多来自其上下文的具体细节。如果 AI 不知道问题的答案，它会诚实地说不知道。

以前对话的相关片段：
{history}

（如果不相关，你不需要使用这些信息）

当前对话：
人类：{input}
AI：
"""

prompt = PromptTemplate(input_variables=["history", "input"], template=PROMPT_TEMPLATE)
chat_model = ChatOpenAI()
conversation_with_summary = ConversationChain(
    llm=chat_model,
    prompt=prompt,
    memory=memory,
    verbose=True
)

print(conversation_with_summary.predict(input="你好，我叫同学小张，你叫什么"))
print(conversation_with_summary.predict(input="我喜欢干什么？"))
print(conversation_with_summary.predict(input="我提到了哪些食物？"))