import os
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

from langchain_openai import ChatOpenAI

llm = ChatOpenAI() # 默认是gpt-3.5-turbo

########## 对话上下文：ConversationBufferMemory
def ConversationBufferMemory_test1():
    from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory

    history = ConversationBufferMemory(memory_key="chat_history_with_同学小张", return_messages=True)
    history.save_context({"input": "你好啊"}, {"output": "你也好啊"})
    print(history.load_memory_variables({}))

    history.save_context({"input": "你再好啊"}, {"output": "你又好啊"})
    print(history.load_memory_variables({}))
    
    history.chat_memory.add_user_message("你在干嘛")
    history.chat_memory.add_ai_message("我在学习")
    print(history.load_memory_variables({}))
    
    # from langchain.memory import ChatMessageHistory
    # chat_history = ChatMessageHistory()
    # chat_history.add_user_message("你在干嘛")
    # chat_history.add_ai_message("我在学习")
    # print(history.load_memory_variables({}))
    
def ConversationBufferWindowMemory_test():
    from langchain.memory import ConversationBufferWindowMemory

    window = ConversationBufferWindowMemory(k=1)
    window.save_context({"input": "第一轮问"}, {"output": "第一轮答"})
    window.save_context({"input": "第二轮问"}, {"output": "第二轮答"})
    window.save_context({"input": "第三轮问"}, {"output": "第三轮答"})
    print(window.load_memory_variables({}))


def ConversationTokenBufferMemory_test():
    from langchain.memory import ConversationTokenBufferMemory
    memory = ConversationTokenBufferMemory(
        llm=llm,
        max_token_limit=45
    )
    memory.save_context(
        {"input": "你好啊"}, {"output": "你好，我是你的AI助手。"})
    memory.save_context(
        {"input": "你会干什么"}, {"output": "我什么都会"})
    print(memory.load_memory_variables({}))

ConversationBufferMemory_test1()    


















    