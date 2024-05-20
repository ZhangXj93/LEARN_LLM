import base64
from PIL import Image
import os
import io
from openai import OpenAI

openai_api_key = os.getenv('OPENAI_API_KEY')

# 此Agent的模型配置，按需修改
OPENAI_CFG_DICT_WITH_IMAGE = {
    "config_name": "openai_cfg_with_image",     # 此配置的名称，必须保证唯一
    "model_type": "openai",                     # 模型类型
    "model_name": "gpt-4o",                     # 模型名称
    "api_key": openai_api_key,                  # OpenAI API key. 如果没有设置，将使用环境变量中的 OPENAI_API_KEY
}

class DialogAgentWithImageWrapper:
    def __init__(self, name, sys_prompt="you are a helpful ai assistant"):
        self.client = OpenAI()
    
    def invoke_with_image(self, query, image_file=None):
        messages = [{"role": "user", "content": [{"type": "text", "text": query}]}]
        
        if image_file is not None:
            image = Image.open(image_file)
            base64_image = self.__encode_image_to_base64(image)
            image_message = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            }
            messages[0]["content"].append(image_message)

        response = self.client.chat.completions.create(
            model=OPENAI_CFG_DICT_WITH_IMAGE["model_name"],
            messages=messages,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    
    def __encode_image_to_base64(self, image):
        buffered = io.BytesIO()
        image.save(buffered, format=image.format)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

if __name__ == "__main__":
    result = DialogAgentWithImageWrapper(name="test").invoke_with_image(query="图片里有什么？", \
        image_file="D:\\GitHub\\LEARN_LLM\\agentscope\\start_0\\flask_agentscope\\AI_search copy\\upload_foler\\流程图-202405151812.png")
    print(result)