import os
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]="test-001"

def test_langsimth():
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
    response = chain.invoke({'name': '同学小张', 'description': '热爱AI，持续学习，持续干货输出'})
    print(response)

def test_data_upload():    
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
            
    from langsmith import Client

    client = Client()

    dataset_name = "assistant-001"

    dataset = client.create_dataset(
        dataset_name, #数据集名称
        description="AGI课堂的标注数据", #数据集描述
    )

    client.create_examples(
        inputs=[{"input":item["input"]} for item in data[:50]], 
        outputs=[{"output":item["expected_output"]} for item in data[:50]], 
        dataset_id=dataset.id
    )

import asyncio
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import HumanMessage
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.evaluation import StringEvaluator
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import re
from typing import Optional, Any

class AccuracyEvaluator(StringEvaluator):

    def __init__(self):
        pass

    def _evaluate_strings(
        self,
        prediction: str,
        input: Optional[str] = None,
        reference: Optional[str] = None,
        **kwargs: Any
    ) -> dict:
        return {"score": int(prediction==reference)}
    
from langchain.evaluation import EvaluatorType
from langchain.smith import RunEvalConfig

evaluation_config = RunEvalConfig(
    # 自定义评估标准
    custom_evaluators=[AccuracyEvaluator()],
)

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
    {
        "outlines":lambda x: x["input"]["outlines"],
        "user_input":lambda x: x["input"]["user_input"],
    }
    | need_answer
    | model
    | parser
)

from langchain.smith import (
    arun_on_dataset,
    run_on_dataset,
)

from langsmith import Client

client = Client()

async def test_run():
    dataset_name = "assistant-001"
    results = await arun_on_dataset(
        dataset_name=dataset_name,
        llm_or_chain_factory=chain_v1,
        evaluation=evaluation_config,
        verbose=True,
        client=client,
        project_name="test-003",
        tags=[
            "prompt_v1",
        ],  # 可选，自定义的标识
    )
    print(results)
    
asyncio.run(test_run())