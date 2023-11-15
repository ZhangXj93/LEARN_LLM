import gradio as gr
import random
from rag import RAG_Bot

CHAT_BOT = RAG_Bot()
# 定义一个处理函数，用于接收上传的文件并进行处理
def process_file(file):
    # 在这里进行文件处理，这里只是一个示例
    # 您可以在这里编写您的文件处理逻辑
    CHAT_BOT.createVectorDB(file)
    return file
    

def random_response(message, history):
    response = CHAT_BOT.chat(message)
    return response

with gr.Blocks() as demo:
    # 创建一个Gradio应用，包含上传文件的功能和处理函数
    bot = gr.Interface(fn=process_file, inputs="file", outputs="text")
    iface2 = gr.ChatInterface(random_response)

demo.launch()
