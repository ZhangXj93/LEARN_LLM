# -*- coding: utf-8 -*-
"""A simple example for auto discussion: the agent builder automatically\
 set up the agents participating the discussion ."""
from tools import load_txt, extract_scenario_and_participants
import agentscope
from agentscope.agents import DialogAgent
from agentscope.pipelines.functional import sequentialpipeline
from agentscope.message import Msg

model_configs = [
    {
        "model_type": "openai",
        "config_name": "gpt-3.5-turbo",
        "model_name": "gpt-3.5-turbo",
        # "api_key": "xxx",  # Load from env if not provided
        # "organization": "xxx",  # Load from env if not provided
        "generate_args": {
            "temperature": 0.5,
        },
    },
]
agentscope.init(model_configs=model_configs)


# init the self-organizing conversation
agent_builder = DialogAgent(
    name="agent_builder",
    sys_prompt="You're a helpful assistant.",
    model_config_name="gpt-3.5-turbo",
)


max_round = 2
query = "假设你眼睛的瞳孔直径为5毫米，你有一台孔径为50厘米的望远镜。望远镜能比你的眼睛多收集多少光？"

# get the discussion scenario and participant agents
x = load_txt(
    "D:\\GitHub\\LEARN_LLM\\agentscope\\start_0\\conversation_self_organizing\\agent_builder_instruct.txt",
).format(
    question=query,
)

x = Msg("user", x, role="user")
settings = agent_builder(x)
scenario_participants = extract_scenario_and_participants(settings["content"])

# set the agents that participant the discussion
agents = [
    DialogAgent(
        name=key,
        sys_prompt=val,
        model_config_name="gpt-3.5-turbo",
    )
    for key, val in scenario_participants["Participants"].items()
]

# begin discussion
msg = Msg("user", f"let's discuss to solve the question with chinese: {query}", role="user")
for i in range(max_round):
    msg = sequentialpipeline(agents, msg)
