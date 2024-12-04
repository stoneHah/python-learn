import socket
import time


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 8632))

    try:
        while True:
            data, addr = server_socket.recvfrom(1024)
            print(f"收到来自 {addr} 的数据: {data}")

            with open("test_query.wav", 'rb') as f:
                while chunk := f.read(1024):  # 每次读取 1024 字节
                     # 添加1字节的消息类型(1表示音频数据)和2字节的序列号
                    message_type = (1).to_bytes(1, 'big')  # 1 byte for audio type
                    
                    # 组合消息类型、序列号和音频数据
                    packet = message_type + chunk
                    server_socket.sendto(packet, addr)
                    time.sleep(0.01)  # 控制发送速率，避免 ESP32 缓冲区溢出
                    
            # 发送结束标志
            server_socket.sendto(b'END', addr)
            print("音频发送完成")
    finally:
        sock.close()
