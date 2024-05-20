import autogen
from autogen import AssistantAgent, UserProxyAgent
import os

llm_config = {"model": "gpt-3.5-turbo", "api_key": os.environ["OPENAI_API_KEY"]}
assistant = AssistantAgent("assistant", llm_config=llm_config)

user_proxy = UserProxyAgent(
    "user_proxy", code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")}
)

# Start the chat
result = user_proxy.initiate_chat(
    assistant,
    message="Plot a chart of NVDA and TESLA stock price change YTD.",
)

print(result)

## https://microsoft.github.io/autogen/docs/Getting-Started