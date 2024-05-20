import os
moonshot_api_key = os.getenv('MOONSHOT_API_KEY') 
moonshot_base_url = os.getenv('MOONSHOT_BASE_URL') 
moonshot_model = "moonshot-v1-128k"

from langchain_community.tools.tavily_search import TavilySearchResults
tools = [TavilySearchResults(max_results=1)]

# from langchain.tools import Tool, tool
# @tool("CodeRunner")
# def CodeRunner(language: str, code: str) -> str:
#     """代码执行器，支持运行 python 和 javascript 代码"""
    
#     print(f"执行代码：{code}")
# tools = [CodeRunner]

from langgraph.prebuilt import ToolExecutor
tool_executor = ToolExecutor(tools)

from langchain_openai.chat_models import ChatOpenAI
model = ChatOpenAI(api_key=moonshot_api_key, base_url=moonshot_base_url, model=moonshot_model, temperature=0)

# from langchain_community.chat_models.moonshot import MoonshotChat
# model = MoonshotChat(api_key=moonshot_api_key, base_url=moonshot_base_url, model="moonshot-v1-128k")

from langchain.tools.render import format_tool_to_openai_function
functions = [format_tool_to_openai_function(t) for t in tools]
model = model.bind_tools(tools=tools)

from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
from langgraph.prebuilt import ToolInvocation
import json
from langchain_core.messages import FunctionMessage

def should_continue(state):
    messages = state['messages']
    last_message = messages[-1]
    if "function_call" not in last_message.additional_kwargs:
        return "end"
    else:
        return "continue"

def call_model(state):
    messages = state['messages']
    response = model.invoke(messages)
    print(response)
    print("===========================\n")
    return {"messages": [response]}

def call_tool(state):
    messages = state['messages']
    last_message = messages[-1]
    action = ToolInvocation(
        tool=last_message.additional_kwargs["function_call"]["name"],
        tool_input=json.loads(last_message.additional_kwargs["function_call"]["arguments"]),
    )
    response = tool_executor.invoke(action)
    function_message = FunctionMessage(content=str(response), name=action.tool)
    return {"messages": [function_message]}

from langgraph.graph import StateGraph, END
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)
workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        # If `tools`, then we call the tool node.
        "continue": "action",
        # Otherwise we finish.
        "end": END
    }
)

workflow.add_edge('action', 'agent')
app = workflow.compile()

from langchain_core.messages import HumanMessage
inputs = {"messages": [HumanMessage(content="北京今天的天气怎么样？")]}
response = app.invoke(inputs)

print(response)