import asyncio

import openai_wrapper
from metagpt_crawler_wrapper import CrawlerDataProvider

PROMPT_TEMPLATE = """简要总结下面文字的内容:
"{text}"
简要总结:"""

class SummaryArticle():
    def __init__(self) -> None:
        pass
    
    def run(self, text):
        prompt = PROMPT_TEMPLATE.format(text = text)
        response_content = openai_wrapper.get_chat_completion(prompt)
        print("response content: ", response_content)
        return response_content

async def summary_url(url):
    text_provider = CrawlerDataProvider()
    text = await text_provider.run(url = url)
    summary = SummaryArticle()
    response_content = summary.run(text = text)
    return response_content

if __name__ == "__main__":
    response = asyncio.run(summary_url(url = "https://mp.weixin.qq.com/s/L_gHW-_TIipmcyDcdQpZRA"))
    print(response)