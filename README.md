# LLM_LEARN
## 1. prompt工程
> 代码：\prompt\
- Prompt 的典型构成
    - 角色：给 AI 定义一个最匹配任务的角色，比如：「你是一位软件工程师」「你是一位小学老师」
    - 指示：对任务进行描述
    - 上下文：给出与任务相关的其它背景信息（尤其在多轮交互中）
    - 例子：必要时给出举例，学术中称为 one-shot learning, few-shot learning 或 in-context learning；实践证明其对输出正确性有帮助
    - 输入：任务的输入信息；在提示词中明确的标识出输入
    - 输出：输出的格式描述，以便后继模块自动解析模型的输出结果，比如（JSON、XML）
大模型对 prompt 开头和结尾的内容更敏感

### 1.1 第一个 prompt_test.py
将 openai 的prompt, messages等传入参数抽离成单独的一个函数 get_chat_completion

### 1.2 第二步 prompt_test_nlu.py
自己实现一个NLU（语义理解）模块