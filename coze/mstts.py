import azure.cognitiveservices.speech as speechsdk

def text_to_speech(text: str) -> bytes:
    """
    将文本转换为语音数据
    
    Args:
        text: 要转换的文本
        
    Returns:
        bytes: 音频数据的字节流
    """
    # 配置语音服务
    speech_key = "b159a9eb87364374b0358c36f000d1f3"
    service_region = "eastus"
    
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = "zh-CN-XiaoxiaoMultilingualNeural"
    
    # 使用 PullAudioOutputStream 来获取音频数据
    pull_stream = speechsdk.audio.PullAudioOutputStream()
    audio_config = speechsdk.audio.AudioOutputConfig(stream=pull_stream)
    
    # 创建语音合成器
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    # 合成语音
    result = speech_synthesizer.speak_text_async(text).get()
    
    # 检查合成结果
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        # 读取音频数据
        audio_data = bytes()
        audio_buffer = bytes(32000)
        
        # 读取所有音频数据
        filled_size = pull_stream.read(audio_buffer)
        while filled_size > 0:
            audio_data += audio_buffer[:filled_size]
            filled_size = pull_stream.read(audio_buffer)
            
        pull_stream.close()
        return audio_data
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        raise Exception(f"语音合成失败: {cancellation_details.reason}")


try:
    audio_data = text_to_speech("你好，世界")
    # 转换为hex字符串传输
    hex_data = audio_data.hex()
    # 播放音频
    play_audio(hex_data)
except Exception as e:
    print(f"错误: {e}")