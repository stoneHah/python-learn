from fastapi import FastAPI, WebSocket
import asyncio
import wave
import io
import base64
import json
import os
import numpy as np
from datetime import datetime
from asrclient import call_audio_to_text_api
from coze_client import chat_stream
from tts_cosyvoice import CosyVoiceTTS
from dotenv import load_dotenv
from tts_doubao import TTSClient

load_dotenv()
app = FastAPI()
COSYVOICE_API_KEY = os.getenv("COSYVOICE_API_KEY")
TTS_CLIENT = TTSClient()

class AudioHandler:
    def __init__(self):
        self.audio_buffer:bytearray = bytearray()  # 存储音频数据
        self.sample_rate = 8000  # 修改为32000Hz，是I2S配置的2倍
        self.channels = 1
        self.sample_width = 2  # 16位音频
        self.total_bytes = 0  # 添加计数器
        
    def reset_buffer(self):
        """重置音频缓冲区"""
        self.audio_buffer = bytearray()

    def process_audio_data(self, audio_data: bytes) -> bytes:
        """处理音频数据，确保格式正确"""
        # 将音频数据转换为16位有符号整数的numpy数组
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # 如果需要，这里可以添加外的音频处理
        # 例如：降噪、音量归一化等
        
        return audio_array.tobytes()
        
    def add_audio_data(self, audio_data: bytes):
        """添加音频数据到缓冲区"""
        self.audio_buffer.extend(audio_data)
        self.total_bytes += len(audio_data)
        print(f"接收数据块大小: {len(audio_data)} bytes")
        print(f"累计接收: {self.total_bytes} bytes") # 调试信息
        
    def save_wav(self, filename: str) -> str:
        """将缓冲区数据保存为WAV文件"""
        if not self.audio_buffer:
            return None
            
        print(f"总数据量: {self.total_bytes} bytes")  # 调试信息
        print(f"预计时长: {self.total_bytes / (self.sample_rate * self.channels * self.sample_width):.2f} 秒")
        
        # 确保目录存在
        os.makedirs("audio_files", exist_ok=True)
        filepath = os.path.join("audio_files", filename)
        
        # 创建WAV文件
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.sample_width)
            wav_file.setframerate(self.sample_rate)

            # 计算总帧数
            total_frames = len(self.audio_buffer) // 2  # 16位 = 2字节
            
            # 写入音频数据
            wav_file.setnframes(total_frames)
            wav_file.writeframes(self.audio_buffer)

        # 验证生成的文件
        with wave.open(filepath, 'rb') as wav_file:
            print(f"WAV文件信息:")
            print(f"通道数: {wav_file.getnchannels()}")
            print(f"采样宽度: {wav_file.getsampwidth()}")
            print(f"采样率: {wav_file.getframerate()}")
            print(f"总帧数: {wav_file.getnframes()}")
            print(f"总时长: {wav_file.getnframes() / wav_file.getframerate():.2f}秒")    
        return filepath



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_handler = AudioHandler()
    
    
    try:
        # 创建一个异步队列
        tts_queue = asyncio.Queue()
        
        # 创建一个异步处理器
        async def tts_processor():
            while True:
                sentence = await tts_queue.get()
                await TTS_CLIENT.query_tts(sentence, custom_audio_handler)
                tts_queue.task_done()
        
        # 启动处理器
        asyncio.create_task(tts_processor())

        while True:
            # 接收WebSocket消息
            message = await websocket.receive_json()
            
            if message['type'] == 'audio':
                # 解码音频数据
                audio_data = bytes.fromhex(message['audio'])
                processed_data = audio_handler.process_audio_data(audio_data)
                audio_handler.add_audio_data(processed_data)
                
                # 发送确认消息
                # await websocket.send_json({
                #     "type": "status",
                #     "message": "received_chunk",
                #     "size": len(audio_data)
                # })
                
            elif message['type'] == 'end_recording':
                # 生成唯一文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recording_{timestamp}.wav"
                
                # 保存音频文件
                filepath = audio_handler.save_wav(filename)
                
                if filepath:
                    # 调用语音转文字 API
                    try:
                        # 这里需要实现调用 API 的具体逻辑
                        response = await call_audio_to_text_api(filepath)
                        print(response)

                        # 修改为分块发送的异步音频处理函数
                        async def custom_audio_handler(data: bytes):
                            chunk_size = 1024  # 设置更小的块大小，可以根据ESP32的内存情况调整
                            print("Total audio data length:", len(data))
                            
                            # 将数据分块发送
                            for i in range(0, len(data), chunk_size):
                                chunk = data[i:i + chunk_size]
                                print(f"Sending chunk {i//chunk_size + 1}, size: {len(chunk)}")
                                await websocket.send_json({
                                    "type": "audio",
                                    "audio": chunk.hex()
                                })
                                # await asyncio.sleep(0.01)  # 添加小延迟，给ESP32处理时间

                        # 创建 TTS 实例
                        # tts = CosyVoiceTTS(
                        #     api_key=COSYVOICE_API_KEY,
                        #     on_data_callback=custom_audio_handler
                        # )

                        # 调用对话流式响应
                        current_sentence = ""
                        sentence_endings = ["，", "。", "！", "？", ",", ".", "!", "?"]  # 定义句子结束标记
                        min_sentence_length = 5
                        
                        for message in chat_stream(bot_id="7435549735148273679", user_id="1", message=response["result"][0]["text"]):
                            print(message)
                            current_sentence += message
                            
                            # 检查是否遇到句子结束标记
                            if len(current_sentence) >= min_sentence_length and any(current_sentence.endswith(ending) for ending in sentence_endings):
                                print(f"合成语音: {current_sentence}")
                                # 不等待，直接放入队列
                                await tts_queue.put(current_sentence)
                                current_sentence = ""  # 重置当前句子
                        
                        # 处理最后可能剩余的文本
                        if current_sentence.strip():
                            print(f"合成剩余语音: {current_sentence}")
                            # 这里也需要添加 await
                            await tts_queue.put(current_sentence)

                    except Exception as e:
                        print(f"Error: {e}")
                    
                # 重置缓冲区，准备接收新的录音
                audio_handler.reset_buffer()
                
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        
    finally:
        # 清理队列中的所有剩余项目
        while not tts_queue.empty():
            try:
                tts_queue.get_nowait()
                tts_queue.task_done()
            except asyncio.QueueEmpty:
                break

        try:
            await websocket.close()
        except:
            pass

# 添加普通的HTTP端点用于健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}





# 启动服务器的命令（需要在终端中运行）：
# uvicorn server:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 