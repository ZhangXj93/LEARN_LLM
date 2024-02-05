import requests

response = requests.post(
    "http://localhost:9999/self_introduction/invoke",
    json={'input': {'name': '同学小张', 'description': '热爱AI，持续学习，持续干货输出'}}
)
print(response.json())