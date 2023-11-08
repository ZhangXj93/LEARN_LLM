from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 配置 OpenAI 服务
openai.api_key = os.getenv('OPENAI_API_KEY') # 设置 OpenAI 的 key
openai.api_base = os.getenv('OPENAI_API_BASE') # 指定代理地址

@app.route('/process-prompt', methods=['POST'])
def process_prompt():
    # 从请求中获取用户输入的 prompt
    prompt = request.json['prompt']
    messages = [{
        "role": "user",
        "content": prompt
    }]
    # 调用 OpenAI API 获取结果
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages,
        temperature = 0,
    )

    # 从结果中提取生成的文本
    result = response.choices[0].message["content"]

    # 返回结果给前端
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run()