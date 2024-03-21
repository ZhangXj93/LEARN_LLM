from openai import OpenAI
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

client = OpenAI()

def get_chat_completion(prompt, model = "gpt-3.5-turbo-1106"):
    if (len(prompt) > 16000):
        prompt = prompt[0:16000]
    messages = [{
        "role": "user",
        "content": prompt
    }]
    
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo-1106",
        messages=messages
    )

    return response.choices[0].message.content