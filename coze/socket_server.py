# UDP 服务器
import socket
from audio_handler import AudioHandler

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('0.0.0.0', 8765))

END_MARKER = b'END_OF_AUDIO'

buffer_size = 1500  # UDP推荐的缓冲区大小
audio_handler = AudioHandler()
while True:
    try:
        data, addr = server_socket.recvfrom(buffer_size)
        if len(data) >= 2:  # 确保至少有序号
            sequence = int.from_bytes(data[:2], 'big')
            audio_data = data[2:]
            print(f"收到来自 {addr} 的数据包 #{sequence}, 大小: {len(audio_data)} bytes")
            # 处理音频数据...
            audio_handler.add_audio_data(audio_data)
    except Exception as e:
        print(f"错误: {e}")