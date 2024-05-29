from agentscope.agents.react_agent import ReActAgent

import agentscope
from agentscope.message import Msg
import os

from agentscope.service import (
    ServiceToolkit,
    ServiceResponse,
    ServiceExecStatus,
)

openai_api_key = os.getenv('OPENAI_API_KEY')

# 此Agent的模型配置，按需修改
OPENAI_CFG_DICT = {
    "config_name": "openai_cfg",    # 此配置的名称，必须保证唯一
    "model_type": "openai",         # 模型类型
    "model_name": "gpt-3.5-turbo",  # 模型名称
    "api_key": openai_api_key,      # OpenAI API key. 如果没有设置，将使用环境变量中的 OPENAI_API_KEY
}

def sum_num(a: int, b: int) -> int:
    """计算两个数的和

    Args:
        a (int): 参数1
        b (int): 参数2

    Returns:
        int: 结果
    """
    output = a + b
    status = ServiceExecStatus.SUCCESS
    return ServiceResponse(status, output)


class ToolDemo:
    def __init__(self):
        # Prepare the tools for the agent
        service_toolkit = ServiceToolkit()
        service_toolkit.add(sum_num)
        
        print(service_toolkit.tools_instruction)
        
        print("=========================\n")
        
        print(service_toolkit.json_schemas)
        
        print("=========================\n")
        
        print(service_toolkit.tools_calling_format)
        
        print("=========================\n")
        
        


        agentscope.init(model_configs=[OPENAI_CFG_DICT])

        self.agent = ReActAgent(
            name="assistant",
            model_config_name="openai_cfg",
            verbose=True,
            service_toolkit=service_toolkit,
            max_iters=1,
        )
        
    def invoke(self, query):
        msg = Msg("user", query, role="user")
        return self.agent(msg)
    
if __name__ == '__main__':
    tool_demo = ToolDemo()
    response = tool_demo.invoke("你是谁？")
    print(response)