
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

neo4j_url = os.getenv('NEO4J_URI')
neo4j_username = os.getenv('NEO4J_USERNAME')
neo4j_password = os.getenv('NEO4J_PASSWORD')

graph = Neo4jGraph(url=neo4j_url, username=neo4j_username, password=neo4j_password)

result = graph.query(
    """
MERGE (m:Movie {name:"Top Gun", runtime: 120})
WITH m
UNWIND ["Tom Cruise", "Val Kilmer", "Anthony Edwards", "Meg Ryan"] AS actor
MERGE (a:Actor {name:actor})
MERGE (a)-[:ACTED_IN]->(m)
"""
)

print(result)

# graph.refresh_schema()
# print(graph.schema)

chain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0), graph=graph, verbose=True
)

result = chain.invoke({"query": "Who played in Top Gun?"})
print(result)

