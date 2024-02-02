import gradio as gr
from rag import RAG_Bot ## 引入前面我们实现的rag文件和类

chat_bot = RAG_Bot() ## 实例化一个chat_bot

def process_inputs(input_file, chat_input):
    outputs = ["", ""]
    if input_file is not None:  # 处理文件上传
        chat_bot.createVectorDB(input_file) ## 创建向量库，灌入数据
        outputs[0] = f"你上传的文件内容是：\n{str(input_file)}"
    if chat_input != "":  # 处理聊天输入
        outputs[1] = chat_bot.chat(chat_input) ## 将聊天输入当作query，进行对话
    return tuple(outputs)

# 输入类型为文件上传和文本框
inputs = [gr.File(), gr.Textbox(label="聊天输入")]

# 输出类型为文件内容和聊天输出
outputs = [gr.Textbox(label="文件内容"), gr.Textbox(label="聊天输出")]

iface = gr.Interface(process_inputs, 
                     inputs=inputs,
                     outputs=outputs,
                     title="文件上传和聊天窗口",
                     description="请在适当的输入框中上传文件或进行聊天。",
                     allow_flagging=False)
iface.launch()
