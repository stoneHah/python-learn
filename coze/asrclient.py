import aiohttp
import os

# 添加新的辅助函数
async def call_audio_to_text_api(audio_file_path: str):
    """调用语音转文字 API"""
    api_url = "http://localhost:9188/api/v1/asr"  # 根据实际部署情况修改URL
    
    # 确保文件存在
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"音频文件不存在: {audio_file_path}")
    
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        
        # 读取整个文件内容到内存中
        file_content = open(audio_file_path, 'rb').read()
        
        # 使用文件内容而不是文件对象
        data.add_field('files', 
                      file_content,
                      filename=os.path.basename(audio_file_path),
                      content_type='audio/wav')
        
        data.add_field('keys', os.path.basename(audio_file_path))
        data.add_field('lang', 'auto')
        
        try:
            async with session.post(api_url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"API调用失败: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"调用语音转文字API时出错: {str(e)}")
            raise

# import asyncio

# # 创建主函数
# async def main():
#     # 使用绝对路径
#     audio_path = "G:\\pyproject\\python-learn\\audio_files\\recording_20241110_150020.wav"
#     result = await call_audio_to_text_api(audio_path)
#     print(result)

# # 运行主函数
# asyncio.run(main())
