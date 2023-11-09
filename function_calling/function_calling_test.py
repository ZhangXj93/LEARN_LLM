import json
import os
from math import *
import openai
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 配置 OpenAI 服务
openai.api_key = os.getenv('OPENAI_API_KEY') # 设置 OpenAI 的 key
# openai.api_base = os.getenv('OPENAI_API_BASE') # 指定代理地址

def get_completion(messages, model="gpt-3.5-turbo-1106"):
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=1024,
        tools=[{ # 用 JSON 描述函数。可以定义多个。由大模型决定调用谁
            "type": "function",
            "function": {
                "name": "sum",
                "description": "计算一组数的和",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "numbers": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            }
                        }
                    }
                }
            }
        }]
    )
    return response.choices[0].message

# prompt = "Tell me the sum of 1, 2, 3, 4, 5, 6, 7, 8, 9, 10."
# prompt = "桌上有 2 个苹果，四个桃子和 3 本书，一共有几个水果？"
prompt = "1+2+3...+99+100"

messages = [
    {"role": "system", "content": "你是一个小学数学老师，你要教学生加法"},
    {"role": "user", "content": prompt}
]
response = get_completion(messages)
# 把大模型的回复加入到对话历史中
if (response.content is None):  # 解决 OpenAI 的一个 400 bug
    response.content = ""
messages.append(response)
print("=====GPT回复=====")
print(response)

# 如果返回的是函数调用结果，则打印出来
if (response.tool_calls is not None):
    tool_call = response.tool_calls[0]
    print(f"调用 {tool_call.function.name} 函数，参数是 {tool_call.function.arguments}")
    if tool_call.function.name == "sum":
        # 调用 sum 函数（本地函数或库函数，非chatgpt），打印结果
        args = json.loads(tool_call.function.arguments)
        result = sum(args["numbers"])
        print("=====函数返回=====")
        print(result)

        # 把函数调用结果加入到对话历史中
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "sum",
                "content": str(result)  # 数值result 必须转成字符串
            }
        )

        # 再次调用大模型
        print("=====最终回复=====")
        print(get_completion(messages).content)