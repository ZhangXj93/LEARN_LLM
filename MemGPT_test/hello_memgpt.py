# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

from memgpt import create_client

# Connect to the server as a user
client = create_client()

# Create an agent
agent_info = client.create_agent(
  name="my_agent1", 
  persona="You are a friendly agent.", 
  human="Bob is a friendly human."
)

# Send a message to the agent
messages = client.user_message(agent_id=agent_info.id, message="Hello, agent!")

print(messages)