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

### 用 SKContext 实现多参数 Functions
## 多参数 Semantic Function 的写法
# Prompt 模板
sk_prompt = """
讲一个{{$topic1}}和{{$topic2}}的一句话笑话
"""

# 创建 Semantic Function
joke = kernel.create_semantic_function(sk_prompt)

# 创建 SKContext
context = kernel.create_new_context()

# 变量赋值
context["topic1"] = "农夫"
context["topic2"] = "狼"

async def async_func():
    result = await kernel.run_async(
            joke,
            input_context=context
        )

    print(result)
    
asyncio.run(async_func())

## 多参数 Native Function 的写法
from sk_samples.math_func import Math
math_skill = kernel.import_skill(Math(), "Math")
context = kernel.create_new_context()
context["number1"] = 1024
context["number2"] = 65536

async def async_func2():
    result = await kernel.run_async(
            math_skill["add"],
            input_context=context
        )

    print(f"加法计算结果：{result}")
    
asyncio.run(async_func2())

async def async_func3():
    result = await kernel.run_async(
            math_skill["minus"],
            input_context=context
        )

    print(f"减法计算结果：{result}")
    
asyncio.run(async_func3())

