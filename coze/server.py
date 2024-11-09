from fastapi import FastAPI, WebSocket
import asyncio
import wave
import io
import base64
import json
import os
from datetime import datetime

app = FastAPI()

class AudioHandler:
    def __init__(self):
        self.audio_buffer = []  # 存储音频数据
        self.sample_rate = 16000  # 修改为32000Hz，是I2S配置的2倍
        self.channels = 1
        self.sample_width = 2  # 16位音频
        self.total_bytes = 0  # 添加计数器
        
    def reset_buffer(self):
        """重置音频缓冲区"""
        self.audio_buffer = []
        
    def add_audio_data(self, audio_data: bytes):
        """添加音频数据到缓冲区"""
        self.audio_buffer.append(audio_data)
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
            for audio_data in self.audio_buffer:
                wav_file.writeframes(audio_data)
                
        return filepath

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_handler = AudioHandler()
    
    try:
        while True:
            # 接收WebSocket消息
            message = await websocket.receive_json()
            
            if message['type'] == 'audio':
                # 解码音频数据
                audio_data = bytes.fromhex(message['audio'])
                audio_handler.add_audio_data(audio_data)
                
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
                    # 这里可以添加与LLM的交互代码
                    
                    # 发送处理完成消息
                    await websocket.send_json({
                        "type": "status",
                        "message": "processing_complete",
                        "filepath": filepath
                    })
                    
                # 重置缓冲区，准备接收新的录音
                audio_handler.reset_buffer()
                
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        
    finally:
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
