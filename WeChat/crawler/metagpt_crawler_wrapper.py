import asyncio
from metagpt.actions.action import Action
from metagpt.schema import Message
from metagpt.tools.web_browser_engine import WebBrowserEngine
from metagpt.utils.common import CodeParser
from metagpt.utils.parse_html import _get_soup
from uuid import uuid4
import sys
from metagpt.logs import logger

def get_outline(page):
    soup = _get_soup(page.html)
    outline = []

    def process_element(element, depth):
        name = element.name
        if not name:
            return
        if name in ["script", "style"]:
            return

        element_info = {"name": element.name, "depth": depth}

        if name in ["svg"]:
            element_info["text"] = None
            outline.append(element_info)
            return

        element_info["text"] = element.string
        # Check if the element has an "id" attribute
        if "id" in element.attrs:
            element_info["id"] = element["id"]

        if "class" in element.attrs:
            element_info["class"] = element["class"]
        outline.append(element_info)
        for child in element.children:
            process_element(child, depth + 1)

    try:
        for element in soup.body.children:
            process_element(element, 1)
    except:
        logger.error("get outline error")
        outline = []
    return outline

PROMPT_TEMPLATE = """Please complete the web page crawler parse function to achieve the User Requirement. The parse \
function should take a BeautifulSoup object as input, which corresponds to the HTML outline provided in the Context.

```python
from bs4 import BeautifulSoup

# only complete the parse function
def parse(soup: BeautifulSoup):
    ...
    # Return the object that the user wants to retrieve, don't use print
```

## User Requirement
{requirement}

## Context

The outline of html page to scrabe is show like below:

```tree
{outline}
```
"""

class WriteCrawlerCode(Action):
    async def run(self, url, requirement):
        codes = {}
        codes[url] = await self._write_code(url, requirement)
        if codes[url] == None:
            return None
        return "\n".join(f"# {url}\n{code}" for url, code in codes.items()) ## 返回固定格式的url + 相应爬虫代码

    async def _write_code(self, url, query):
        page = await WebBrowserEngine().run(url)
        outline = get_outline(page)
        if len(outline) == 0:
            return None
        outline = "\n".join(
            f"{' '*i['depth']}{'.'.join([i['name'], *i.get('class', [])])}: {i['text'] if i['text'] else ''}"
            for i in outline
        )
        code_rsp = await self._aask(PROMPT_TEMPLATE.format(outline=outline, requirement=query))
        code = CodeParser.parse_code(block="", text=code_rsp)
        return code
    
# 运行订阅智能体的Action
class RunCrawlerCode(Action):
    async def run(self, url, codes):
        code, current = codes.rsplit(f"# {url}", maxsplit=1)
        name = uuid4().hex
        module = type(sys)(name)
        exec(current, module.__dict__)
        page = await WebBrowserEngine().run(url)
        data = getattr(module, "parse")(page.soup)
        print(data)
        return str(data)  # 以字符串形式返回

    
# 定义爬虫工程师角色
from metagpt.roles import Role
class CrawlerEngineer(Role):
    name: str = "同学小张的专属爬虫工程师"
    profile: str = "Crawling Engineer"
    goal: str = "Write elegant, readable, extensible, efficient code"
    constraints: str = "The code should conform to standards like PEP8 and be modular and maintainable"
    
    url: str = ""
    requirement: str = ""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_actions([WriteCrawlerCode, RunCrawlerCode])
        
    async def _think(self) -> None:
        """Determine the next action to be taken by the role."""
        logger.info(self.rc.state)
        logger.info(self,)
        if self.rc.todo is None:
            self._set_state(0)
            return

        if self.rc.state + 1 < len(self.states):
            self._set_state(self.rc.state + 1)
        else:
            self.rc.todo = None

    async def _act(self) -> Message:
        """Perform an action as determined by the role.

        Returns:
            A message containing the result of the action.
        """
        todo = self.rc.todo
        if type(todo) is WriteCrawlerCode:
            resp = await todo.run(url=self.url, requirement=self.requirement)
            logger.info(resp)
            if (resp == None):
                return None
            self.rc.memory.add(Message(content=resp, role=self.profile))
            return resp
        msg = self.rc.memory.get(k=1)[0]
        resp = await todo.run(url=self.url, codes=msg.content) # 返回必须是字符串
        logger.info(resp)
        return Message(content=resp, role=self.profile) # resp必须是字符串，MetaGPT中限制的

    async def _react(self) -> Message:
        """Execute the assistant's think and actions.

        Returns:
            A message containing the final result of the assistant's actions.
        """
        while True:
            await self._think()
            if self.rc.todo is None:
                break
            msg = await self._act()
            if msg == None:
                break
        return msg

class CrawlerDataProvider():
    def __init__(self) -> None:
        pass
    
    async def run(self, url, requirement="获取正文中的所有文字内容，如果正文有code，将code也作为文字内容"):
        msg = "start"
        role = CrawlerEngineer(url = url, requirement = requirement)
        logger.info(msg)
        result = await role.run(msg)
        logger.info("\n=========================================\n")
        logger.info(result)
        return result
        
if __name__ == "__main__":
    url="https://mp.weixin.qq.com/s/2m8MrsCxf5boiH4Dzpphrg"
    requirement="获取标题，正文中的所有文字内容，如果正文有code，将code也作为文字内容"
    data_provider = CrawlerDataProvider()
    asyncio.run(data_provider.run(url, requirement))