import re
from langchain.tools import StructuredTool
from langchain_core.output_parsers import BaseOutputParser

from Utils.PrintUtils import color_print, CODE_COLOR
from Utils.PromptTemplateBuilder import PromptTemplateBuilder
# from Utils.PythonExecUtil import execute_python_code
from langchain_openai import ChatOpenAI
from .ExcelTool import get_first_n_rows, get_column_names
from langchain_experimental.utilities import PythonREPL


class PythonCodeParser(BaseOutputParser):
    """从OpenAI返回的文本中提取Python代码。"""

    def _remove_marked_lines(self, input_str: str) -> str:
        lines = input_str.strip().split('\n')
        if lines and lines[0].strip().startswith('```'):
            del lines[0]
        if lines and lines[-1].strip().startswith('```'):
            del lines[-1]

        ans = '\n'.join(lines)
        return ans

    def parse(self, text: str) -> str:
        # 使用正则表达式找到所有的Python代码块
        python_code_blocks = re.findall(r'```python\n(.*?)\n```', text, re.DOTALL)
        # 从re返回结果提取出Python代码文本
        python_code = None
        if len(python_code_blocks) > 0:
            python_code = python_code_blocks[0]
            python_code = self._remove_marked_lines(python_code)
        return python_code


class ExcelAnalyser:

    def __init__(self, prompts_path, prompt_file="excel_analyser.json", verbose=False):
        self.prompt = PromptTemplateBuilder(prompts_path, prompt_file).build()
        self.verbose = verbose

    def analyse(self, query, filename):

        """分析一个结构化文件（例如excel文件）的内容。"""

        # columns = get_column_names(filename)
        inspections = get_first_n_rows(filename, 3)

        llm = ChatOpenAI(
            model="gpt-4-1106-preview",
            temperature=0,
            model_kwargs={
                "seed": 42
            },
        )

        chain = self.prompt | llm | PythonCodeParser()

        code = ""

        if self.verbose:
            color_print("\n#!/usr/bin/env python", CODE_COLOR, end="\n")

        for c in chain.stream({
            "query": query,
            "filename": filename,
            "inspections": inspections
        }):
            if self.verbose:
                color_print(c, CODE_COLOR, end="")
            code += c

        if code:
            ans = PythonREPL().run(code)
            return ans
        else:
            return "没有找到可执行的Python代码"

    def as_tool(self):
        return StructuredTool.from_function(
            func=self.analyse,
            name="AnalyseExcel",
            description="通过程序脚本分析一个结构化文件（例如excel文件）的内容。输人中必须包含文件的完整路径和具体分析方式和分析依据，阈值常量等。如果输入信息不完整，你可以拒绝回答。",
        )


if __name__ == "__main__":
    print(ExcelAnalyser(
        prompts_path="../prompts"
    ).analyse(
        query="8月销售额",
        filename="../data/2023年8月-9月销售记录.xlsx"
    ))
