## 2. function calling

response.tool_calls 可能返回多个function，每个function都要处理，都要把函数调用结果加入到对话历史中，否则openai接口可能会报错