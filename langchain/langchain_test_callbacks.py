import os
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

def callback_test():
    from langchain.callbacks import StdOutCallbackHandler
    from langchain.chains import LLMChain
    from langchain_openai import OpenAI
    from langchain.prompts import PromptTemplate

    handler = StdOutCallbackHandler()
    llm = OpenAI()
    prompt = PromptTemplate.from_template("1 + {number} = ")

    # Constructor callback: First, let's explicitly set the StdOutCallbackHandler when initializing our chain
    chain = LLMChain(llm=llm, prompt=prompt, callbacks=[handler])
    chain.invoke({"number":2})

    # Use verbose flag: Then, let's use the `verbose` flag to achieve the same result
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    chain.invoke({"number":2})

    # Request callbacks: Finally, let's use the request `callbacks` to achieve the same result
    chain = LLMChain(llm=llm, prompt=prompt)
    chain.invoke({"number":2}, {"callbacks":[handler]})

def custom_callback_test():
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import HumanMessage
    from langchain_openai import ChatOpenAI


    class MyCustomHandler(BaseCallbackHandler):
        def on_llm_new_token(self, token: str, **kwargs) -> None:
            print(f"My custom handler, token: {token}")


    # To enable streaming, we pass in `streaming=True` to the ChatModel constructor
    # Additionally, we pass in a list with our custom handler
    chat = ChatOpenAI(max_tokens=25, streaming=True, callbacks=[MyCustomHandler()])

    chat([HumanMessage(content="Tell me a joke")])

def async_callback_test():
    import asyncio
    from typing import Any, Dict, List

    from langchain.callbacks.base import AsyncCallbackHandler, BaseCallbackHandler
    from langchain.schema import HumanMessage, LLMResult
    from langchain_openai import ChatOpenAI


    class MyCustomSyncHandler(BaseCallbackHandler):
        def on_llm_new_token(self, token: str, **kwargs) -> None:
            print(f"Sync handler being called in a `thread_pool_executor`: token: {token}")


    class MyCustomAsyncHandler(AsyncCallbackHandler):
        """Async callback handler that can be used to handle callbacks from langchain."""

        async def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
        ) -> None:
            """Run when chain starts running."""
            print("zzzz....")
            await asyncio.sleep(0.5)
            print("Hi! I just woke up. Your llm is starting")

        async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
            """Run when chain ends running."""
            print("zzzz....")
            await asyncio.sleep(0.3)
            print("Hi! I just woke up. Your llm is ending")


    # To enable streaming, we pass in `streaming=True` to the ChatModel constructor
    # Additionally, we pass in a list with our custom handler
    chat = ChatOpenAI(
        max_tokens=25,
        streaming=True,
        callbacks=[MyCustomSyncHandler(), MyCustomAsyncHandler()],
    )

    asyncio.run(chat.agenerate([[HumanMessage(content="Tell me a joke")]]))
    
    
def logger_callback_test():
    from langchain.callbacks import FileCallbackHandler
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain_openai import OpenAI
    # from loguru import logger

    logfile = "output.log"

    # logger.add(logfile, colorize=True, enqueue=True)
    handler = FileCallbackHandler(logfile)

    llm = OpenAI()
    prompt = PromptTemplate.from_template("1 + {number} = ")

    # this chain will both print to stdout (because verbose=True) and write to 'output.log'
    # if verbose=False, the FileCallbackHandler will still write to 'output.log'
    chain = LLMChain(llm=llm, prompt=prompt, callbacks=[handler], verbose=True)
    answer = chain.run(number=2)
    # logger.info(answer)
    from ansi2html import Ansi2HTMLConverter
    from IPython.display import HTML, display

    with open("D:\GitHub\LEARN_LLM\output.log", "r") as f:
        content = f.read()

    conv = Ansi2HTMLConverter()
    html = conv.convert(content, full=True)

    display(HTML(html))


def token_callback_test():
    from langchain.callbacks import get_openai_callback
    from langchain_openai import OpenAI

    llm = OpenAI(temperature=0)
    with get_openai_callback() as cb:
        llm("What is the square root of 4?")

    total_tokens = cb.total_tokens
    print("total_tokens: ", total_tokens)
    
token_callback_test()