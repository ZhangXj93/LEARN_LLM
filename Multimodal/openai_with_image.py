import base64
from PIL import Image
import os
import io
from openai import OpenAI

client = OpenAI()

def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format=image.format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def invoke_with_image(query, image_file=None):
    messages = [{"role": "user", "content": [{"type": "text", "text": query}]}]
    
    if image_file is not None:
        image = Image.open(image_file)
        base64_image = encode_image_to_base64(image)
        image_message = {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        }
        messages[0]["content"].append(image_message)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    result = invoke_with_image(query="图片里有什么？", \
        image_file="c:\\Users\\zhangxinjie01\\Pictures\\Saved Pictures\\微信图片_20240405184354.jpg")
    print(result)