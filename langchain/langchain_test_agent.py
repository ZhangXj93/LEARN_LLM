import os
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

from langchain_openai import ChatOpenAI

# 1. 准备 llm
llm = ChatOpenAI() # 默认是gpt-3.5-turbo

def agent_test():
    # 定义 tools
    from langchain.agents import load_tools
    tools = load_tools(["serpapi"])

    from langchain.agents import initialize_agent
    from langchain.agents import AgentType
    # 工具加载后都需要初始化，verbose 参数为 True，会打印全部的执行详情
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    # 运行 agent
    agent.run("今天的日期是什么? 历史上的今天发生了什么大事?用中文回答")


# 2. 定义 tools
from langchain import SerpAPIWrapper
from langchain.tools import Tool, tool

search = SerpAPIWrapper()
tools = [
    Tool.from_function(
        func=search.run,
        name="Search",
        description="useful for when you need to answer questions about current events"
    ),
]
    
import calendar
import dateutil.parser as parser
from datetime import date
from langchain.tools import Tool, tool
# 自定义工具
@tool("weekday")
def weekday(date_str: str) -> str:
    """Convert date to weekday name"""
    d = parser.parse(date_str)
    return calendar.day_name[d.weekday()]
tools += [weekday]

# 3. 准备 prompt 模板
# from langchain import hub
# import json
# # 下载一个现有的 Prompt 模板
# prompt = hub.pull("hwchase17/react")
# print(prompt.template)

from langchain_core.prompts import ChatPromptTemplate
prompt_template = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action，如果其中有日期，请确保只输入日期，格式为:YYYY-MM-DD，不要有任何其它字符
Observation: the result of the action，如果其中有日期，请确保输出的日期格式为:YYYY-MM-DD，不要有任何其它字符
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin! Let's think step by step. Take a deep breath.

Question: {input}
Thought:{agent_scratchpad}
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

 
# 4. 创建Agent
from langchain.agents import create_react_agent
agent = create_react_agent(llm, tools, prompt)

# 5. 创建Agent执行器
from langchain.agents import AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 6. 运行Agent
agent_executor.invoke({"input": "周杰伦生日那天是星期几"})