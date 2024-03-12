from openai import OpenAI
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

client = OpenAI()

###### 这里封装成函数 #######
def get_openai_chat_completion(messages, temperature, model = "gpt-3.5-turbo-1106"):
    response = client.chat.completions.create(
        model = model,
        messages = messages,
        temperature = temperature,
        stream=True,    # 启动流式输出
    )
    return response

SYSTEM_PROMPT = """
你是一名资深教师，你叫“同学小张”，用户会给你一个提示，你根据用户给的提示，来为用户设计关于此课程的学习大纲。
你必须遵循以下原则：
1. 你有足够的时间思考，确保在得出答案之前，你已经足够理解用户需求中的所有关键概念，并给出关键概念的解释。
2. 输出格式请使用Markdown格式, 并保证输出内容清晰易懂。
3. 至少输出10章的内容, 每章至少有5个小节

不要回答任何与课程内容无关的问题。
"""

if __name__ == "__main__":
    user_input = "大模型应用开发"
    
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_input,
        }   
    ]
    response = get_openai_chat_completion(messages, 0.5)
    
    text = ""

    print("====Streaming====")

    # 需要把 stream 里的 token 拼起来，才能得到完整的 call
    for msg in response:
        delta = msg.choices[0].delta
        if delta.content:
            text_delta = delta.content
            print(text_delta)
            text = text + text_delta

    print("====done!====")

    if text:
        print(text)