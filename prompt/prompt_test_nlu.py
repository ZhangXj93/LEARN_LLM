########### Prompt 的典型构成 ##############
# 角色：给 AI 定义一个最匹配任务的角色，比如：「你是一位软件工程师」「你是一位小学老师」
# 指示：对任务进行描述
# 上下文：给出与任务相关的其它背景信息（尤其在多轮交互中）
# 例子：必要时给出举例，学术中称为 one-shot learning, few-shot learning 或 in-context learning；实践证明其对输出正确性有帮助
# 输入：任务的输入信息；在提示词中明确的标识出输入
# 输出：输出的格式描述，以便后继模块自动解析模型的输出结果，比如（JSON、XML）

## !!!!!!!!!! 大模型对 prompt 开头和结尾的内容更敏感 !!!!!!!!!!
###########################################


import os
from urllib import response
import openai
import json
import copy
# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 配置 OpenAI 服务
openai.api_key = os.getenv('OPENAI_API_KEY') # 设置 OpenAI 的 key
# openai.api_base = os.getenv('OPENAI_API_BASE') # 指定代理地址

# 任务描述
instruction = """
你的任务是识别用户对手机流量套餐产品的选择条件。
每种流量套餐产品包含三个属性：名称(name)，月费价格(price)，月流量(data)。
根据用户输入，识别用户在上述三种属性上的倾向。
"""

# 用户输入
input_text = """
有没有100块以下的套餐
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
DO NOT OUTPUT NULL-VALUED FIELD! 确保输出能被json.loads加载。
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

class NLU:
    def __init__(self) -> None:
        self.prompt_template = f"{instruction}\n\n{output_format}\n\n例如:{examples}\n\n用户输入:\n __INPUT__"

    def _get_chat_completion(self, prompt, model = "gpt-3.5-turbo-1106"):
        messages = [{
            "role": "user",
            "content": prompt
        }]

        response = openai.chat.completions.create(
            model = model,
            messages = messages,
            temperature = 0,
        )
        semantics = json.loads(response.choices[0].message.content)
        return {k: v for k, v in semantics.items() if v}

    def parse(self, user_input):
        prompt = self.prompt_template.replace("__INPUT__", user_input)
        return self._get_chat_completion(prompt)

class DST:
    def __init__(self) -> None:
        pass

    def update(self, state, nlu_semantics):
        print("state before: ", state)
        if "name" in nlu_semantics:
            state.clear()
        if "sort" in nlu_semantics:
            slot = nlu_semantics["sort"]["value"]
            if slot in state and state[slot]["operator"] == "==":
                del state[slot]
        
        for k, v in nlu_semantics.items():
            state[k] = v
            print("state after: ", state)

        return state

class MockedDB:
    def __init__(self) -> None:
        self.data = [
            {"name": "经济套餐", "price": 50, "data": 10, "requirement": None},
            {"name": "畅游套餐", "price": 180, "data": 100, "requirement": None},
            {"name": "无限套餐", "price": 300, "data": 1000, "requirement": None},
            {"name": "校园套餐", "price": 150, "data": 200, "requirement": "在校生"},
        ]

    def retrieve(self, **kwargs):
        records = []
        for r in self.data:
            select = True
            if r["requirement"]:
                if "status" not in kwargs or kwargs["status"] != r["requirement"]:
                    continue
            for k, v in kwargs.items():
                if k == "sort":
                    continue
                if k == "data" and v["value"] == "无上限":
                    if r[k] != 1000:
                        select = False
                        break
                if "operator" in v:
                    if not eval(str(r[k])+v["operator"]+str(v["value"])):
                        select = False
                        break
                elif str(r[k]) != str(v):
                    select = False
                    break
            if select:
                records.append(r)
        if len(records) <= 1:
            return records
        key = "price"
        reverse = False
        if "sort" in kwargs:
            key = kwargs["sort"]["value"]
            reverse = kwargs["sort"]["ordering"] == "descend"
        return sorted(records, key=lambda x: x[key], reverse=reverse)

class DialogManager:
    def __init__(self, prompt_templates) -> None:
        self.state = {}
        self.session = [
            {
                "role": "system",
                "content": "你是一个手机流量套餐的客服代表，你叫小瓜。可以帮助用户选择最合适的流量套餐产品。"
            }
        ]
        self.nlu = NLU()
        self.dst = DST()
        self.db = MockedDB()
        self.prompt_templates = prompt_templates

    def _wrap(self, user_input, records):
        if records:
            prompt = self.prompt_templates["recommand"].replace(
                "__INPUT__", user_input)
            r = records[0]
            for k, v in r.items():
                print(k, v)
                prompt = prompt.replace(f"__{k.upper()}__", str(v))
        else:
            prompt = self.prompt_templates["not_found"].replace(
                "__INPUT__", user_input)
            for k, v in self.state.items():
                if "operator" in v:
                    prompt = prompt.replace(
                        f"__{k.upper()}__", v["operator"]+str(v["value"]))
                else:
                    prompt = prompt.replace(f"__{k.upper()}__", str(v))
        return prompt
    
    def _call_chatgpt(self, prompt, model="gpt-3.5-turbo-1106"):
        session = copy.deepcopy(self.session)
        session.append({"role": "user", "content": prompt})
        print("session: ", session)
        response = openai.chat.completions.create(
            model=model,
            messages=session,
            temperature=0,
        )
        return response.choices[0].message.content
    
    def run(self, user_input):
        # 调用NLU获得语义解析
        semantics = self.nlu.parse(user_input)
        print("===semantics===")
        print(semantics)

        # 调用DST更新多轮状态
        self.state = self.dst.update(self.state, semantics)
        print("===state===")
        print(self.state)

        # 根据状态检索DB，获得满足条件的候选
        records = self.db.retrieve(**self.state)
        print("===records===")
        print(records)

        # 拼装prompt调用chatgpt
        prompt_for_chatgpt = self._wrap(user_input, records)
        print("===gpt-prompt===")
        print(prompt_for_chatgpt)
        
        # 调用chatgpt获得回复
        response = self._call_chatgpt(prompt_for_chatgpt)

        # 将当前用户输入和系统回复维护入chatgpt的session
        self.session.append({"role": "user", "content": user_input})
        self.session.append({"role": "assistant", "content": response})
        return response


if __name__ == "__main__":
    prompt_templates = {
        "recommand": "用户说：__INPUT__ \n\n向用户介绍如下产品：__NAME__，月费__PRICE__元，每月流量__DATA__G。",
        "not_found": "用户说：__INPUT__ \n\n没有找到满足__PRICE__元价位__DATA__G流量的产品，询问用户是否有其他选择倾向。"
    }

    dm = DialogManager(prompt_templates)
    response = dm.run("流量大的")
    print("===response===")
    print(response)
    
    # 增加约束：改变语气、口吻
    ext = "很口语，亲切一些。不用说“抱歉”。直接给出回答，不用在前面加“小瓜说：”。NO COMMENTS. NO ACKNOWLEDGEMENTS."
    prompt_templates = {k: v+ext for k, v in prompt_templates.items()}
    dm = DialogManager(prompt_templates)
    response = dm.run("300太贵了，200元以内有吗")
    print("===response===")
    print(response)
    
    # 用例子实现统一口径
    ext = "\n\n遇到类似问题，请参照以下回答：\n问：流量包太贵了\n答：亲，我们都是全省统一价哦。"
    prompt_templates = {k: v+ext for k, v in prompt_templates.items()}
    dm = DialogManager(prompt_templates)
    response = dm.run("这流量包太贵了")
    print("===response===")
    print(response)
