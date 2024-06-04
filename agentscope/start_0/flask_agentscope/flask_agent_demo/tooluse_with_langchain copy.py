
import calendar
import dateutil.parser as parser
from datetime import date
from langchain.tools import Tool, tool
import json
# 自定义工具
@tool("weekday")
def weekday(date_str: str) -> str:
    """Convert date to weekday name"""
    d = parser.parse(date_str)
    return calendar.day_name[d.weekday()]

@tool("sum_number")
def sum_number(a: int, b: int) -> int:
    """Sum two numbers"""
    return a + b


from langchain_openai import ChatOpenAI
from langchain.tools.render import format_tool_to_openai_function
from langchain_core.messages import FunctionMessage

class ToolDemo:
    def __init__(self):
        tools = [weekday, sum_number]
        model = ChatOpenAI(temperature=0)
        functions = [format_tool_to_openai_function(t) for t in tools]
        self.model = model.bind_functions(functions)

    def invoke(self, query):
        response = self.model.invoke(query)
        print("0000: ", response)

        
        if "function_call" in response.additional_kwargs:
            function_calls = response.additional_kwargs["function_call"]
            args = json.loads(function_calls["arguments"])
            print("args: ", args)
            function_name = function_calls["name"]
            if function_name == "weekday":
                response = weekday(**args)
            elif function_name == "sum_number":
                response = sum_number(**args)

            print("2222: ", response)

            function_message = FunctionMessage(content=str(response), name=function_name)
            response = self.model.invoke(function_message)
            print("1111: ", response)
        return response

   

if __name__ == "__main__":
    tool_demo = ToolDemo()
    response = tool_demo.invoke("2+2=?")
    print("response=====================>")
    print(response)