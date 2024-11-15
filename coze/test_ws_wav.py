import json
import wave
import asyncio
import websockets
import binascii

# 音频参数
CHANNELS = 1            # 单声道
SAMPLE_WIDTH = 2        # 16-bit 音频
FRAME_RATE = 16000      # 采样率
OUTPUT_FILE = 'output.wav'  # 输出文件名

async def audio_handler(websocket, path):
    print("WebSocket connection established")
    # 打开 wav 文件用于写入音频数据
    with wave.open(OUTPUT_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(FRAME_RATE)

        try:
            async for message in websocket:
                # 解析 JSON 数据
                data = json.loads(message)
                if data.get('type') == 'audio':
                    # 获取音频数据，并转换回字节格式
                    hex_audio_data = data['audio']
                    audio_data = binascii.unhexlify(hex_audio_data)
                    # 将音频数据写入到 .wav 文件
                    wf.writeframes(audio_data)
                    print(f"Received and wrote {len(audio_data)} bytes of audio data")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            print("WebSocket connection closed")

# 启动 WebSocket 服务器
async def main():
    server = await websockets.serve(audio_handler, '0.0.0.0', 8000)
    print("Server listening on port 8000...")
    await server.wait_closed()

# 运行服务器
if __name__ == "__main__":
    asyncio.run(main())
