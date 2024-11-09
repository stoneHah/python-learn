import socket

server_address = ('192.168.0.106', 12345)  # 替换为ESP32的IP地址

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while True:
        message = input("Enter command (ON, OFF, BREATHE) or 'exit' to quit: ").strip()
        if message.lower() == 'exit':
            break
        elif message in ['ON', 'OFF', 'BREATHE']:
            sock.sendto(message.encode(), server_address)
        else:
            print("Invalid command. Please enter 'ON', 'OFF', 'BREATHE' or 'exit'.")
finally:
    sock.close()
