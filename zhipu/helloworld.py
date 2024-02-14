
import requests
import json
import os
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

zhipu_api_key = os.getenv('ZHIPU_AI_API_KEY') # 设置百度千帆AK

from zhipuai import ZhipuAI

def test():
    client = ZhipuAI(api_key=zhipu_api_key) # 填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
            {"role": "user", "content": "作为一名营销专家，请为我的产品创作一个吸引人的slogan"},
            {"role": "assistant", "content": "当然，为了创作一个吸引人的slogan，请告诉我一些关于您产品的信息"},
            {"role": "user", "content": "智谱AI开放平台"},
            {"role": "assistant", "content": "智启未来，谱绘无限一智谱AI，让创新触手可及!"},
            {"role": "user", "content": "创造一个更精准、吸引人的slogan"}
        ],
    )
    print(response.choices[0].message)
    
def function_calling_test():
    from zhipuai import ZhipuAI

    client = ZhipuAI(api_key=zhipu_api_key) # 请填写您自己的APIKey

    response = client.chat.completions.create(
        model="glm-4", # 填写需要调用的模型名称
        messages = [
            {
                "role": "user",
                "content": "你能帮我查询2024年1月1日从北京南站到上海的火车票吗？"
            }
        ],
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "query_train_info",
                    "description": "根据用户提供的信息，查询对应的车次",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "departure": {
                                "type": "string",
                                "description": "出发城市或车站",
                            },
                            "destination": {
                                "type": "string",
                                "description": "目的地城市或车站",
                            },
                            "date": {
                                "type": "string",
                                "description": "要查询的车次日期",
                            },
                        },
                        "required": ["departure", "destination", "date"],
                    },
                }
            }
        ],
        tool_choice="auto",
    )
    print(response.choices[0].message)
    
def image_test():
    from zhipuai import ZhipuAI
    client = ZhipuAI(api_key=zhipu_api_key) # 请填写您自己的APIKey

    response = client.images.generations(
        model="cogview-3", #填写需要调用的模型名称
        prompt="过年了，画一条东方巨龙，喜庆，可爱",
    )
    print(response.data[0].url)
    
image_test()