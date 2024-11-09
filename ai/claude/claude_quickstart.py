import anthropic
import base64
import httpx
from PIL import Image
import io

client = anthropic.Anthropic(api_key='stone-claudeai',
                             base_url='https://claudeai.stonezq.workers.dev/')

def image_to_bytes(image_path):
    # 打开图片文件
    with Image.open(image_path) as img:
        # 创建一个字节流对象
        byte_array = io.BytesIO()
        # 将图片保存到字节流中
        img.save(byte_array, format=img.format)
        # 获取字节数据
        byte_data = byte_array.getvalue()
    return byte_data

image1_path = "images/image-1.png"
image1_media_type = "image/png"
image1_data = base64.b64encode(image_to_bytes(image1_path)).decode("utf-8")

image2_path = "images/image-2.png"
image2_media_type = "image/png"
image2_data = base64.b64encode(image_to_bytes(image2_path)).decode("utf-8")


message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Image 1:"
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image1_media_type,
                        "data": image1_data,
                    },
                },
                {
                    "type": "text",
                    "text": "Image 2:"
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image2_media_type,
                        "data": image2_data,
                    },
                },
                {
                    "type": "text",
                    "text": "解读下这个小说片段"
                }
            ],
        }
    ],
)

print(message.content)
