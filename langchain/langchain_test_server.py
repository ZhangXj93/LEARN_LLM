import os
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

#!/usr/bin/env python
from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langserve import add_routes
import uvicorn

app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple api server using Langchain's Runnable interfaces",
)

prompt_template = """
我的名字叫【{name}】，我的个人介绍是【{description}】。
请根据我的名字和介绍，帮我想一段有吸引力的自我介绍的句子，以此来吸引读者关注和点赞我的账号。
"""

model = ChatOpenAI()
prompt = ChatPromptTemplate.from_template(prompt_template)
add_routes(
    app,
    prompt | model,
    path="/self_introduction",
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=9999)