########### Prompt 的典型构成 ##############
# 角色：给 AI 定义一个最匹配任务的角色，比如：「你是一位软件工程师」「你是一位小学老师」
# 指示：对任务进行描述
# 上下文：给出与任务相关的其它背景信息（尤其在多轮交互中）
# 例子：必要时给出举例，学术中称为 one-shot learning, few-shot learning 或 in-context learning；实践证明其对输出正确性有帮助
# 输入：任务的输入信息；在提示词中明确的标识出输入
# 输出：输出的格式描述，以便后继模块自动解析模型的输出结果，比如（JSON、XML）

## !!!!!!!!!! 大模型对 prompt 开头和结尾的内容更敏感 !!!!!!!!!!
###########################################


import os
import openai
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 配置 OpenAI 服务
openai.api_key = os.getenv('OPENAI_API_KEY') # 设置 OpenAI 的 key
# openai.api_base = os.getenv('OPENAI_API_BASE') # 指定代理地址

def get_chat_completion(prompt, model = "gpt-3.5-turbo-1106"):
    messages = [{
        "role": "user",
        "content": prompt
    }]

    response = openai.chat.completions.create(
        model = model,
        messages = messages,
        temperature = 0,
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    response = get_chat_completion("讲个笑话")
    print(response)