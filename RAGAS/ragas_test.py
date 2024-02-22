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

# # testing it out
question = "纽约市的名字是怎么得来的?"
result = qa_chain({"query": question})
# result["result"]
print("========= chain result ==========")
print(result)

result['ground_truths'] = "纽约市的名字“纽约”来源于荷兰战败后将新阿姆斯特丹割让给英国的事件。"

from ragas.metrics import faithfulness, answer_relevancy, context_relevancy, context_recall
from ragas.langchain.evalchain import RagasEvaluatorChain

# make eval chains
eval_chains = {
    m.name: RagasEvaluatorChain(metric=m) 
    for m in [faithfulness, answer_relevancy, context_relevancy, context_recall]
}

# evaluate
for name, eval_chain in eval_chains.items():
    score_name = f"{name}_score"
    print(f"{score_name}: {eval_chain(result)[score_name]}")

