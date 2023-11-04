########### Prompt 的典型构成 ##############
# 角色：给 AI 定义一个最匹配任务的角色，比如：「你是一位软件工程师」「你是一位小学老师」
# 指示：对任务进行描述
# 上下文：给出与任务相关的其它背景信息（尤其在多轮交互中）
# 例子：必要时给出举例，学术中称为 one-shot learning, few-shot learning 或 in-context learning；实践证明其对输出正确性有帮助
# 输入：任务的输入信息；在提示词中明确的标识出输入
# 输出：输出的格式描述，以便后继模块自动解析模型的输出结果，比如（JSON、XML）

## !!!!!!!!!! 大模型对 prompt 开头和结尾的内容更敏感 !!!!!!!!!!
###########################################


from dis import Instruction
import os
import openai
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 配置 OpenAI 服务
openai.api_key = os.getenv('OPENAI_API_KEY') # 设置 OpenAI 的 key
# openai.api_base = os.getenv('OPENAI_API_BASE') # 指定代理地址

def get_chat_completion(prompt, model = "gpt-3.5-turbo"):
    messages = [{
        "role": "user",
        "content": prompt
    }]

    response = openai.ChatCompletion.create(
        model = model,
        messages = messages,
        temperature = 0,
    )
    return response.choices[0].message["content"]

## ================== 自己实现一个NLU（语义理解）模块 begin ================== ##
# 任务描述
instruction = """
你的任务是识别用户对手机流量套餐产品的选择条件。
每种流量套餐产品包含三个属性：名称(name)，月费价格(price)，月流量(data)。
根据用户输入，识别用户在上述三种属性上的倾向。
"""

# 用户输入
input_text = """
有没有便宜的套餐
"""

# 约定输出格式
output_format = """
以JSON格式输出
1. name字段的取值为string类型，取值必须为以下之一：经济套餐、畅游套餐、无限套餐、校园套餐 或 null；

2. price字段的取值为一个结构体 或 null，包含两个字段：
(1) operator, string类型，取值范围：'<='（小于等于）, '>=' (大于等于), '=='（等于）
(2) value, int类型

3. data字段的取值为取值为一个结构体 或 null，包含两个字段：
(1) operator, string类型，取值范围：'<='（小于等于）, '>=' (大于等于), '=='（等于）
(2) value, int类型或string类型，string类型只能是'无上限'

4. 用户的意图可以包含按price或data排序，以sort字段标识，取值为一个结构体：
(1) 结构体中以"ordering"="descend"表示按降序排序，以"value"字段存储待排序的字段
(2) 结构体中以"ordering"="ascend"表示按升序排序，以"value"字段存储待排序的字段

输出中只包含用户提及的字段，不要猜测任何用户未直接提及的字段，不输出值为null的字段。
"""

# 例子让输出更稳定
examples = """
便宜的套餐：{"sort":{"ordering"="ascend","value"="price"}}
有没有不限流量的：{"data":{"operator":"==","value":"无上限"}}
流量大的：{"sort":{"ordering"="descend","value"="data"}}
100G以上流量的套餐最便宜的是哪个：{"sort":{"ordering"="ascend","value"="price"},"data":{"operator":">=","value":100}}
月费不超过200的：{"price":{"operator":"<=","value":200}}
就要月费180那个套餐：{"price":{"operator":"==","value":180}}
经济套餐：{"name":"经济套餐"}
"""


# prompt 模板
prompt = f"""
{instruction}

{output_format}

例如：
{examples}

用户输入:
{input_text}

""" 

## ================== 自己实现一个NLU（语义理解）模块 end ================== ##

if __name__ == "__main__":
    response = get_chat_completion(prompt)
    print(response)