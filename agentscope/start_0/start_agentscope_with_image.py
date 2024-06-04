import agentscope
from agentscope.message import Msg

def main() -> None:
  # 一次性初始化多个模型配置
  openai_cfg_dict = {
      "config_name": "openai_cfg", # A unique name for the model config.
      "model_type": "openai",         # Choose from "openai", "openai_dall_e", or "openai_embedding".

      "model_name": "gpt-4o",   # The model identifier used in the OpenAI API, such as "gpt-3.5-turbo", "gpt-4", or "text-embedding-ada-002".
      # "api_key": openai_api_key,       # Your OpenAI API key. If unset, the environment variable OPENAI_API_KEY is used.
  }

  agentscope.init(model_configs=[openai_cfg_dict], logger_level="INFO")

  from agentscope.agents import DialogAgent, UserAgent

  # 创建一个对话智能体和一个用户智能体
  dialogAgent = DialogAgent(name="assistant", model_config_name="openai_cfg", sys_prompt="You are a helpful ai assistant")
  
  x = Msg(name="user", content="图片里有什么？", role="user", url=["c:/Users/zhangxinjie01/Pictures/Saved Pictures/微信图片_20240405184354.jpg"])
  response = dialogAgent(x)
  print(response)
  
  
if __name__ == "__main__":
    main()