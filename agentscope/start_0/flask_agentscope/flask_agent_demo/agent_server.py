from flask import Flask, render_template, request, jsonify
from agent_demo import DialogAgentWrapper
from agent_demo_with_image import DialogAgentWithImageWrapper
from tooluse_demo_reactagent import ToolDemo
# from rag_demo import RAGDemo
from rag_demo_with_langchain import RAGDemo
import os
import speech_recognition as sr

app = Flask(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) # 获取当前文件的目录路径
RAG_DEMO = RAGDemo(CURRENT_DIR + "/vector_db_path") # RAG 实例
DIALOG_AGENT = DialogAgentWrapper(name="myAgent", rag_demo=RAG_DEMO) # agentscope agent实例
DIALOG_AGENT_WITH_IMAGE = DialogAgentWithImageWrapper(name="myAgent2")
TOOL_DEMO = ToolDemo()


####### 知识库文件上传准备工作 ########
KN_FOLDER = CURRENT_DIR + "/upload_foler" # 上传知识库保存目录
try:
    os.mkdir(KN_FOLDER) # 创建单个文件夹
except FileExistsError:
    pass # 文件夹已经存在
app.config['UPLOAD_FOLDER'] = KN_FOLDER

app.config['ALLOWED_EXTENSIONS_FILE'] = {'pdf', 'doc', 'docx'}  # 允许的文件格式
def allowed_file(filename):
    # return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS_FILE']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # 允许的图片格式
def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    """上传PDF文件到服务端，同时会将该文件进行切分和向量化，存入向量数据库"""
    
    # 检查是否有文件在请求中
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # 如果用户没有选择文件，浏览器也会提交一个没有文件名的空部分
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = file.filename # 文件名
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) # 文件绝对路径
        file.save(filepath)

        # 写入向量数据库
        RAG_DEMO.createVectorDB(filepath)

        # 这里可以处理pdf_content，例如提取文本等
        return jsonify({'message': 'File uploaded successfully', 'filename': filename})

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/upload_image', methods=['POST'])
def upload_image():
    """上传一张图片到服务端"""
    
    # 检查是否有图片在请求中
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']

    # 如果用户没有选择文件，浏览器也会提交一个没有文件名的空部分
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_image(file.filename):
        filename = file.filename # 文件名
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) # 文件绝对路径
        file.save(filepath)
        return jsonify({'message': 'Image uploaded successfully', 'filename': filename})

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/user_query_with_image', methods=['POST'])
def user_query_with_image():
    """用户根据图片进行提问，输入为query和一张图片"""
    
    query = request.args.get('query')
    query = request.form.get('query')
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']
    
    # 如果用户没有选择文件，浏览器也会提交一个没有文件名的空部分
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_image(file.filename):
        filename = file.filename # 文件名
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) # 文件绝对路径
        file.save(filepath) # 图片保存服务器上
        response = DIALOG_AGENT_WITH_IMAGE.invoke_with_image(query=query, image_file=filepath)
        return jsonify(response)

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/user_query', methods=['GET'])
def user_query():
    print(request.args)
    query = request.args.get('query')
    result = DIALOG_AGENT.invoke(query, with_rag=False)
    return jsonify(result)

@app.route('/user_query_with_rag', methods=['GET'])
def user_query_with_rag():
    print(request.args)
    query = request.args.get('query')
    result = DIALOG_AGENT.invoke(query, with_rag=True)
    return jsonify(result)

@app.route('/user_query_with_tools', methods=['GET'])
def user_query_with_tools():
    print(request.args)
    query = request.args.get('query')
    result = TOOL_DEMO.invoke(query)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8017, debug=False)