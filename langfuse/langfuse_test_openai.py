

def langfuse_test_openai():
    from datetime import datetime
    from langfuse.openai import openai
    from langfuse import Langfuse 
    import os

    trace = Langfuse().trace(
        name = "hello-world",
        user_id = "同学小张",
        release = "v0.0.1"
    )

    completion = openai.chat.completions.create(
    name="hello-world",
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "对我说'Hello, World!'"}
    ],
    temperature=0,
    trace_id=trace.id,
    )

    print(completion.choices[0].message.content)
    
def test_langfuse_langchain():   
    from langfuse.callback import CallbackHandler

    handler = CallbackHandler(
        trace_name="SayHello",
        user_id="同学小张",
    )

    from langchain_openai import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain.schema.output_parser import StrOutputParser
    from langchain.schema.runnable import RunnablePassthrough
    from langchain.schema import HumanMessage
    from langchain.prompts.chat import HumanMessagePromptTemplate
    from langchain.prompts import ChatPromptTemplate

    model = ChatOpenAI(model="gpt-3.5-turbo-0613")

    prompt_template = """
    我的名字叫【{name}】，我的个人介绍是【{description}】。
    请根据我的名字和介绍，帮我想一段有吸引力的自我介绍的句子，以此来吸引读者关注和点赞我的账号。
    """
    prompt = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template(prompt_template)
    ])

    # 定义输出解析器
    parser = StrOutputParser()

    chain = (
        prompt
        | model
        | parser
    )

    ## invoke的第一个参数，传入json格式的参数，key与prompt中的参数名一致
    response = chain.invoke({'name': '同学小张', 'description': '热爱AI，持续学习，持续干货输出'}, config={"callbacks":[handler]})
    print(response)

def dataset_upload():  
    import json

    data = []
    with open('D:\GitHub\LEARN_LLM\langsmith\my_annotations.jsonl','r',encoding='utf-8') as fp:
        for line in fp:
            example = json.loads(line.strip())
            item = {
                "input": {
                    "outlines": example["outlines"],
                    "user_input": example["user_input"]
                },
                "expected_output": example["label"]
            }
            data.append(item)
            
    from langfuse import Langfuse
    from langfuse.model import CreateDatasetRequest, CreateDatasetItemRequest
    from tqdm import tqdm

    # init
    langfuse = Langfuse()

    # 考虑演示运行速度，只上传前5条数据
    for item in tqdm(data[:5]):
        langfuse.create_dataset_item(
            dataset_name="assistant-data", ## 注意：这个dataset_name需要提前在Langfuse后台创建
            input=item["input"],
            expected_output=item["expected_output"]
        )

import uuid
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser        

def simple_evaluation(output, expected_output):
  return output == expected_output

from langchain.prompts import PromptTemplate

need_answer=PromptTemplate.from_template("""
*********
你是AIGC课程的助教，你的工作是从学员的课堂交流中选择出需要老师回答的问题，加以整理以交给老师回答。
 
课程内容:
{outlines}
*********
学员输入:
{user_input}
*********
如果这是一个需要老师答疑的问题，回复Y，否则回复N。
只回复Y或N，不要回复其他内容。""")

model = ChatOpenAI(temperature=0,model_kwargs={"seed":42})
parser = StrOutputParser()

chain_v1 = (
    need_answer
    | model
    | parser
)

from concurrent.futures import ThreadPoolExecutor
from functools import partial
from langfuse import Langfuse

langfuse = Langfuse()

def run_evaluation(chain, dataset_name, run_name):
    dataset = langfuse.get_dataset(dataset_name)

    def process_item(item):
        handler = item.get_langchain_handler(run_name=run_name)
        
        # Assuming chain.invoke is a synchronous function
        output = chain.invoke(item.input, config={"callbacks": [handler]})
        
        # Assuming handler.root_span.score is a synchronous function
        handler.root_span.score(
            name="accuracy",
            value=simple_evaluation(output, item.expected_output)
        )
        print('.', end='',flush=True)

    # Using ThreadPoolExecutor with a maximum of 10 workers
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Map the process_item function to each item in the dataset
        executor.map(process_item, dataset.items)
        
run_evaluation(chain_v1, "assistant-data", "v1-"+str(uuid.uuid4())[:8])