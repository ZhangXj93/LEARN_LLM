

# 文件结构及内容

agent_server.py ： flask接口，服务入口，运行此文件

agent_demo.py ： 对话agent，支持RAG和非RAG

rag_demo.py ： RAG原生代码，参考，没启用

rag_demo_with_langchain.py ： 使用LangChain实现的RAG代码，与RAG原生代码相同功能

agent_demo_with_image.py ：支持传入一张图片和一个问题，根据图片回答问题

# 安装依赖 pip install 

```bash
pypdf 
pdfminer.six
openai
langchain
langchain_openai
agentscope
Chroma
unstructured
python-docx
chromadb
SpeechRecognition
```

# 其它说明

1. RAG知识库只支持上传PDF文件
2. 图片无法RAG
3. 语音不支持传入大模型，上层可先语音转文字，然后使用文字接口