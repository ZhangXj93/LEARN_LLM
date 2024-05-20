import agentscope

from loguru import logger
from agentscope.message import Msg
from agentscope.agents import DialogAgent
from rag_demo import RAGDemo
import os

openai_api_key = os.getenv('OPENAI_API_KEY')

# 此Agent的模型配置，按需修改
OPENAI_CFG_DICT = {
    "config_name": "openai_cfg",    # 此配置的名称，必须保证唯一
    "model_type": "openai",         # 模型类型
    "model_name": "gpt-3.5-turbo",  # 模型名称
    "api_key": openai_api_key,      # OpenAI API key. 如果没有设置，将使用环境变量中的 OPENAI_API_KEY
}

# 此Agent的Prompt模板
SYSTEM_PROMPT = """
你是一个问答机器人。
"""

PROMPT_TEMPLATE = """
你的任务是根据下述给定的已知信息回答用户问题。
确保你的回复完全依据下述已知信息。不要编造答案。
如果下述已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。
已知信息:
{content}

用户问：
{query}

请用中文回答用户问题。
"""

class DialogAgentWrapper:
    def __init__(self, name, rag_demo=None, sys_prompt=SYSTEM_PROMPT):
        agentscope.init(model_configs=[OPENAI_CFG_DICT], logger_level="INFO")
        
        # 创建一个对话智能体
        self.dialog_agent = agentscope.agents.DialogAgent(name=name, model_config_name="openai_cfg", sys_prompt=sys_prompt)
        self.rag_demo = rag_demo
        
    def invoke(self, query, with_rag=False):
        # 使用智能体进行对话
        if (with_rag):
            content = self.rag_demo.search(query)
            user_prompt = PROMPT_TEMPLATE.format(query=query, content=content)
        else:
            user_prompt = query
        msg = Msg("user", user_prompt, role="user")
        print(msg)
        response = self.dialog_agent(msg)
        return response