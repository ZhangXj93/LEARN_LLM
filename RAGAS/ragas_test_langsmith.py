import os
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]="test-ragas2"

from langchain_community.document_loaders import WebBaseLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI

# load the Wikipedia page and create index
loader = WebBaseLoader("https://baike.baidu.com/item/%E7%BA%BD%E7%BA%A6/6230")
loader.requests_kwargs = {'verify':False}
index = VectorstoreIndexCreator().from_loaders([loader])

# create the QA chain
llm = ChatOpenAI()
qa_chain = RetrievalQA.from_chain_type(
    llm, retriever=index.vectorstore.as_retriever(), return_source_documents=True
)

from ragas.metrics import faithfulness, answer_relevancy, context_relevancy, context_recall
from ragas.langchain.evalchain import RagasEvaluatorChain

# create evaluation chains
faithfulness_chain = RagasEvaluatorChain(metric=faithfulness)
answer_rel_chain = RagasEvaluatorChain(metric=answer_relevancy)
context_rel_chain = RagasEvaluatorChain(metric=context_relevancy)
context_recall_chain = RagasEvaluatorChain(metric=context_recall)

# 测试数据集
eval_questions = [
    "纽约市的名字是怎么得来的?",
]

eval_answers = [
    "纽约市的名字“纽约”来源于荷兰战败后将新阿姆斯特丹割让给英国的事件。",
]

examples = [{"query": q, "ground_truths": [eval_answers[i]]} for i, q in enumerate(eval_questions)]

# dataset creation
from langsmith import Client
from langsmith.utils import LangSmithError

client = Client()
dataset_name = "ragas test data"

try:
    # check if dataset exists
    dataset = client.read_dataset(dataset_name=dataset_name)
    print("using existing dataset: ", dataset.name)
except LangSmithError:
    # if not create a new one with the generated query examples
    dataset = client.create_dataset(
        dataset_name=dataset_name, description="NYC test dataset"
    )
    for e in examples:
        client.create_example(
            inputs={"query": e["query"]},
            outputs={"ground_truths": e["ground_truths"]},
            dataset_id=dataset.id,
        )

    print("Created a new dataset: ", dataset.name)
    
from langchain.smith import RunEvalConfig, run_on_dataset

evaluation_config = RunEvalConfig(
    custom_evaluators=[
        faithfulness_chain,
        answer_rel_chain,
        context_rel_chain,
        context_recall_chain,
    ],
    prediction_key="result",
)

result = run_on_dataset(
    client,
    dataset_name,
    qa_chain,
    evaluation=evaluation_config,
    input_mapper=lambda x: x,
)

