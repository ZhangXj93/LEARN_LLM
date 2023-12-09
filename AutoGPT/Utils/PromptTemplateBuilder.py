from langchain.prompts import PromptTemplate
from typing import List, Optional
from langchain.tools.base import BaseTool
from langchain.schema.output_parser import BaseOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import load_prompt
import os, json
import tempfile 

class PromptTemplateBuilder():
    def __init__(self, prompt_path: str, prompt_file: str):
        self.prompt_path = prompt_path
        self.prompt_file = prompt_file
        
    
        
        
        