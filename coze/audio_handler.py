import os
import wave

import numpy as np


class AudioHandler:
    def __init__(self):
        self.audio_buffer:bytearray = bytearray()  # 存储音频数据
        self.sample_rate = 16000  # 修改为32000Hz，是I2S配置的2倍
        self.channels = 1
        self.sample_width = 2  # 16位音频
        self.total_bytes = 0  # 添加计数器
        
    def reset_buffer(self):
        """重置音频缓冲区和计数器"""
        self.audio_buffer = bytearray()
        self.total_bytes = 0  # 同时重置计数器

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