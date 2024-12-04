import wave

filepath = "test_query.wav"
with wave.open(filepath, 'rb') as wav_file:
    print(f"WAV文件信息:")
    print(f"通道数: {wav_file.getnchannels()}")
    print(f"采样宽度: {wav_file.getsampwidth()}")
    print(f"采样率: {wav_file.getframerate()}")
    print(f"总帧数: {wav_file.getnframes()}")
    print(f"总时长: {wav_file.getnframes() / wav_file.getframerate():.2f}秒") 

    # 跳过WAV文件头部44字节
    # wav_file.setpos(44)
    
    # # 按1024字节步长读取数据
    # chunk_size = 1024
    # while True:
    #     data = wav_file.readframes(chunk_size)
    #     if not data:
    #         break
        # 这里可以对data进行处理

    
