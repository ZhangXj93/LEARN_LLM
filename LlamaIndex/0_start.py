
from llama_index.core import Document

doc = Document(text="text")

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

import os.path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

PERSIST_DIR = "D:\GitHub\LEARN_LLM\LlamaIndex\data2"
# check if storage already exists
if not os.path.exists(PERSIST_DIR):
    # load the documents and create the index
    documents = SimpleDirectoryReader("D:\\GitHub\\LEARN_LLM\\LlamaIndex\\data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    # store it for later
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    print("创建索引成功")
else:
    # load the existing index
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
    print("加载索引成功")

# Either way we can now query the index
query_engine = index.as_query_engine()
response = query_engine.query("什么是角色提示?")
print(response)

