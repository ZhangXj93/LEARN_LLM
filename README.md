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

### 1.1 第一步 prompt_test.py
将 openai 的prompt, messages等传入参数抽离成单独的一个函数 get_chat_completion

### 1.2 第二步 prompt_test_nlu.py
自己实现一个NLU（语义理解）模块

### 1.3 第三步 自己实现NLU和DST多轮对话 prompt_test_nlu.py
- 步骤
    - 调用NLU获得语义解析：调用了openai API，理解用户输入，约定好输出格式便于后续程序处理
    - 调用DST更新多轮状态
    - 根据状态检索DB，获得满足条件的候选产品
    - 拼装prompt调用chatgpt：根据上面选出的字段组装prompt，让chatgpt生成自然语言
    - 将当前用户输入和系统回复维护入chatgpt的session：多轮对话的上下文
- 这里只是用chatgpt识别了用户意思和生成了筛选出的产品介绍。产品的筛选靠的是程序

### 1.4 第四步 纯用openai API实现第三步的内容 prompt_test_nlu_openai.py
- 这里用openai直接回答用户问题。用户意图理解nlu，状态跟踪dst和产品筛选这中间的多个步骤都是在大模型中完成
> 优缺点：方便，但中间过程更加不可控，黑盒。第三步中dst和产品筛选都是可控的，会更加准确
