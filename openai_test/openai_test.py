import os
import openai
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 配置 OpenAI 服务
openai.api_key = os.getenv('OPENAI_API_KEY') # 设置 OpenAI 的 key
# openai.api_base = os.getenv('OPENAI_API_BASE') # 指定代理地址

response = openai.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        {
            "role": "user",
            "content": "讲个笑话"
        }
    ],
)

print(response.choices[0].message.content)