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

# 定义 semantic function
# 参数由{{ }}标识
tell_joke_about = kernel.create_semantic_function("给我讲个关于{{$input}}的笑话吧")

# result = await kernel.run_async(
#     tell_joke_about,
#     input_str="hello world"
# )

print(tell_joke_about("hello world"))
    
# 加载 semantic function。注意目录结构
my_skill = kernel.import_semantic_skill_from_directory(
    "./Semantic_Kernel/", "sk_samples")

# 运行 skill 看结果
# result = await kernel.run_async(
#         my_skill["GenerateCommand"],
#         input_str="将系统日期设为2023-04-01",
#     )
sk_func = my_skill["GenerateCommand"]
result = sk_func("更改系统时间为2020年1月1日")
print(result.result)

from sk_samples.sample_plugin import CommandVerifier
verify_skill = kernel.import_skill(CommandVerifier(), "Verifier")
# 看结果
verify_func = verify_skill["verifyCommand"],
print(verify_func[0]('date -s "2023-04-01"'))

async def async_func():
    result = await kernel.run_async(
            verify_skill["verifyCommand"],
            input_str='date -s "2023-04-01"',
        )

    print(result)
    
asyncio.run(async_func())

