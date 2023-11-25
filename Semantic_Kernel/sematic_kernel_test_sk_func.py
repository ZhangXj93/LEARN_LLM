# semantic_kernel只能使用 openai < 1.0 版本，23-11-25

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
import os
import asyncio

# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 创建 sk kernel
kernel = sk.Kernel()

# 配置openai服务
api_key = os.getenv('OPENAI_API_KEY')
end_point = os.getenv('OPENAI_API_BASE')
model = OpenAIChatCompletion(
    "gpt-3.5-turbo",
    api_key=api_key,
    endpoint=end_point
)

# 把 LLM 服务加入 kernel
# 可以加多个。第一个加入的会被默认使用，非默认的要被指定使用
kernel.add_text_completion_service("my_gpt35", model)

sk_funcs = kernel.import_semantic_skill_from_directory(
    "./Semantic_Kernel", "sk_samples"
)

async def async_func():
    result = await kernel.run_async(
            sk_funcs["GenerateCommand2"],
            # input_str="查看当前目录下的文件"
            input_str="删除当前目录"
        )

    print(f"结果：{result}")
    
asyncio.run(async_func())

