import json
import os
from anyio import sleep
from openai import OpenAI
import requests
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 配置 OpenAI 服务
# 初始化 OpenAI 服务
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

amap_key = os.getenv('AMAP_KEY')

def get_location_coordinate(location, city="北京"):
    url = f"https://restapi.amap.com/v5/place/text?key={amap_key}&keywords={location}&region={city}"
    print(url)
    r = requests.get(url)
    result = r.json()
    if "pois" in result and result["pois"]:
        return result["pois"][0]
    return None


def search_nearby_pois(longitude, latitude, keyword):
    url = f"https://restapi.amap.com/v5/place/around?key={amap_key}&keywords={keyword}&location={longitude},{latitude}"
    print(url)
    r = requests.get(url)
    result = r.json()
    ans = ""
    if "pois" in result and result["pois"]:
        for i in range(min(3, len(result["pois"]))):
            name = result["pois"][i]["name"]
            address = result["pois"][i]["address"]
            distance = result["pois"][i]["distance"]
            ans += f"{name}\n{address}\n距离：{distance}米\n\n"
    return ans

# 创建助手。此时不会做任何执行
assistant = client.beta.assistants.create(
    name="导游",
    description="你是一个地图通，你可以找到任何地址。",
    model="gpt-3.5-turbo-1106",
    tools=[{
        "type": "function",
        "function": {
            "name": "search_nearby_pois",
            "description": "搜索给定坐标附近的poi",
            "parameters": {
                "type": "object",
                "properties": {
                    "longitude": {
                        "type": "string",
                        "description": "中心点的经度",
                    },
                    "latitude": {
                        "type": "string",
                        "description": "中心点的纬度",
                    },
                    "keyword": {
                        "type": "string",
                        "description": "目标poi的关键字",
                    }
                },
                "required": ["longitude", "latitude", "keyword"],
            }
        }
    },
        {
        "type": "function",
        "function": {
            "name": "search_nearby_pois",
            "description": "搜索给定坐标附近的poi",
            "parameters": {
                "type": "object",
                "properties": {
                    "longitude": {
                        "type": "string",
                        "description": "中心点的经度",
                    },
                    "latitude": {
                        "type": "string",
                        "description": "中心点的纬度",
                    },
                    "keyword": {
                        "type": "string",
                        "description": "目标poi的关键字",
                    }
                },
                "required": ["longitude", "latitude", "keyword"],
            }
        }
    }],
)

print("----assistant----")
print(assistant)

# 创建对话
thread = client.beta.threads.create(
    messages=[{
        "role": "user",
        "content": "北京三里屯附近的咖啡"
    }]
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id)

print("----run----")
print(run)

while (True):
    print(run.status)
    if (run.status == "completed"):
        print("completed")
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        print(messages.data[0].content[0].text.value)
        break
    elif (run.status == "failed"):
        print("failed")
        break
    elif (run.status == "queued"):
        print("queued")
        sleep(1000)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id, run_id=run.id)
        continue
    elif (run.status == "requires_action"):
        require_action = run.required_action
        print(require_action)

        output = []

        for submit_tool in require_action.submit_tool_outputs.tool_calls:
            print("=======Submit Tool=======")
            print(submit_tool)
            if (submit_tool.function.name == "get_location_coordinate"):
                # )#["arguments"])
                args = json.loads(submit_tool.function.arguments)
                print("Call: get_location_coordinate")
                result = get_location_coordinate(**args)
                output.append(
                    {"output": result, "tool_call_id": submit_tool.id})
            elif (submit_tool.function.name == "search_nearby_pois"):
                # json.loads(response["function_call"]["arguments"])
                args = json.loads(submit_tool.function.arguments)
                print("Call: search_nearby_pois")
                result = search_nearby_pois(**args)
                output.append(
                    {"output": result, "tool_call_id": submit_tool.id})

            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id, run_id=run.id,
                tool_outputs=output
            )
    elif (run.status == "in_progress"):
        sleep(1000)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id, run_id=run.id)
        continue
    else:
        print("unknown status")
        break