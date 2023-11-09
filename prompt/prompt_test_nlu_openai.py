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
from urllib import response
import openai
import json
import copy
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 配置 OpenAI 服务
openai.api_key = os.getenv('OPENAI_API_KEY') # 设置 OpenAI 的 key
# openai.api_base = os.getenv('OPENAI_API_BASE') # 指定代理地址

session = [
    {
        "role": "system",
        "content": """
你是一个手机流量套餐的客服代表，你叫小瓜。可以帮助用户选择最合适的流量套餐产品。可以选择的套餐包括：
经济套餐，月费50元，10G流量；
畅游套餐，月费180元，100G流量；
无限套餐，月费300元，1000G流量；
校园套餐，月费150元，200G流量，仅限在校生。
"""
    }
]

def get_completion(prompt, model="gpt-3.5-turbo-1106"):
    session.append({"role": "user", "content": prompt})
    response = openai.chat.completions.create(
        model=model,
        messages=session,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
    )
    msg = response.choices[0].message.content
    session.append({"role": "assistant", "content": msg})
    return msg

if __name__ == "__main__":
    get_completion("有没有土豪套餐？")
    get_completion("多少钱？")
    get_completion("给我办一个")
    print(json.dumps(session, indent=4, ensure_ascii=False))  # 用易读格式打印对话历史
