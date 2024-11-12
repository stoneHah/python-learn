# coding=utf-8
#
# Installation instructions for pyaudio:
# APPLE Mac OS X
#   brew install portaudio
#   pip install pyaudio
# Debian/Ubuntu
#   sudo apt-get install python-pyaudio python3-pyaudio
#   or
#   pip install pyaudio
# CentOS
#   sudo yum install -y portaudio portaudio-devel && pip install pyaudio
# Microsoft Windows
#   python -m pip install pyaudio

import time
import pyaudio
import dashscope
from dashscope.api_entities.dashscope_response import SpeechSynthesisResponse
from dashscope.audio.tts_v2 import *
import asyncio

# 将your-dashscope-api-key替换成您自己的API-KEY
dashscope.api_key = "sk-699d29a865824dd8a56d427fe45b7413"
model = "cosyvoice-v1"
voice = "longxiaochun"


class Callback(ResultCallback):
    def __init__(self, on_data_callback=None):
        self._player = None
        self._stream = None
        # 允许自定义数据处理回调
        self._on_data_callback = on_data_callback or self._default_audio_handler
        # 添加事件循环引用
        self._loop = asyncio.get_event_loop()

    def on_open(self):
        print("cosyvoice websocket is open.")
        self._player = pyaudio.PyAudio()
        self._stream = self._player.open(
            format=pyaudio.paInt16, channels=1, rate=16000, output=True
        )

    def _default_audio_handler(self, data: bytes) -> None:
        """默认的音频数据处理方法"""
        print("audio result length:", len(data))
        self._stream.write(data)

    def on_data(self, data: bytes) -> None:
        """处理音频数据"""
        # self._default_audio_handler(data)
        if asyncio.iscoroutinefunction(self._on_data_callback):
            # 如果是异步回调，使用事件循环运行它
            future = asyncio.run_coroutine_threadsafe(
                self._on_data_callback(data), 
                self._loop
            )
            future.result()  # 等待异步操作完成
        else:
            # 如果是同步回调，直接调用
            self._on_data_callback(data)

    def on_complete(self):
        print("speech synthesis task complete successfully.")

    def on_error(self, message: str):
        print(f"speech synthesis task failed, {message}")

    def on_close(self):
        print("cosyvoice websocket is closed.")
        # 安全地关闭播放器
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self._player:
            self._player.terminate()

    def on_event(self, message):
        print(f"recv speech synthsis message {message}")


class CosyVoiceTTS:
    def __init__(self, api_key: str, model: str = "cosyvoice-v1", 
                 voice: str = "longxiaochun", on_data_callback=None):
        self.api_key = api_key
        dashscope.api_key = api_key
        self.model = model
        self.voice = voice
        self.callback = None
        self.synthesizer = None
        self._on_data_callback = on_data_callback
        self._setup_callback()
        self._setup_synthesizer()
    
    def _setup_callback(self):
        """初始化回调对象"""
        self.callback = Callback(on_data_callback=self._on_data_callback)
    
    def _setup_synthesizer(self):
        """初始化语音合成器"""
        self.synthesizer = SpeechSynthesizer(
            model=self.model,
            voice=self.voice,
            format=AudioFormat.WAV_16000HZ_MONO_16BIT,
            callback=self.callback
        )
        
    def synthesize_text(self, text: str):
        """
        合成单个文本片段
        
        Args:
            text: 要合成的文本
        """
        try:
            self.synthesizer.streaming_call(text)
        except Exception as e:
            print(f"语音合成过程中发生错误: {str(e)}")
    
    def async_stream_complete(self) -> str:
        """
        完成流式合成并返回请求ID
        
        Returns:
            str: 最后的请求ID
        """
        try:
            self.synthesizer.async_streaming_complete()
            return self.synthesizer.get_last_request_id()
        except Exception as e:
            print(f"完成流式合成时发生错误: {str(e)}")
            return ""

# 使用示例:
def main():
    # 自定义音频数据处理函数
    def custom_audio_handler(data: bytes):
        # 例如，保存到文件
        print("send audio data")
        print("audio hex:", data.hex())

    # 创建 TTS 实例时指定自定义处理函数
    tts = CosyVoiceTTS(
        api_key="sk-699d29a865824dd8a56d427fe45b7413",
        # on_data_callback=custom_audio_handler
    )

    test_text = [
        "流式文本语音合成SDK，",
        "可以将输入的文本",
        "合成为语音二进制数据，",
        "相比于非流式语音合成，",
        "流式合成的优势在于实时性",
        "更强。用户在输入文本的同时",
        "可以听到接近同步的语音输出，",
        "极大地提升了交互体验，",
        "减少了用户等待时间。",
        "适用于调用大规模",
        "语言模型（LLM），以",
        "流式输入文本的方式",
        "进行语音合成的场景。",
    ]

    for text in test_text:
        tts.synthesize_text(text)
        time.sleep(0.5)  # 可选的延迟

    # 完成流式合成
    request_id = tts.async_stream_complete()
    print('requestId: ', request_id)

if __name__ == "__main__":
    main()