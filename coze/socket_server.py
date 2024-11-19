# UDP 服务器
import socket
from audio_handler import AudioHandler
import time
from asrclient import call_audio_to_text_api
from coze_client import chat_stream,create_conversation_id
from dotenv import load_dotenv
from tts_doubao import TTSClient
import asyncio
import wave

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('0.0.0.0', 8765))

END_MARKER = b'END_OF_AUDIO'

buffer_size = 1500  # UDP推荐的缓冲区大小

# 使用字典来存储每个客户端的 AudioHandler
class ClientSession:
    def __init__(self):
        self.audio_handler = AudioHandler()
        self.last_active = time.time()
        self.session_id = None
        self.conversation_id = None
    
    def update_active_time(self):
        self.last_active = time.time()
        
    def get_audio_handler(self):
        return self.audio_handler
    
    def get_conversation_id(self):
        if self.conversation_id is None:
            self.conversation_id = create_conversation_id()
        return self.conversation_id

# 存储所有客户端会话
clients = {}  # addr -> ClientSession

# TODO 并发量高的情况的得优化下,目前就一个ws实例
TTS_CLIENT = TTSClient()

# 创建一个协程来处理UDP数据接收
async def receive_data():
    loop = asyncio.get_event_loop()
    while True:
        try:
            # 使用线程执行器来处理阻塞的UDP接收
            data, addr = await loop.run_in_executor(None, 
                lambda: server_socket.recvfrom(buffer_size))
            
            client_session = get_client_session(addr)
            
            if data == END_MARKER:
                print(f"====================收到来自 {addr} 的结束标记====================")
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"recording_{addr[0]}_{addr[1]}_{timestamp}.wav"
                filepath = client_session.get_audio_handler().save_wav(filename)
                print(f"音频已保存到: {filepath}")
                client_session.get_audio_handler().reset_buffer()

                # 语音识别为文字
                asr_result = await call_audio_to_text_api(filepath)
                print(f"语音识别为文字: {asr_result}")
                asr_text = asr_result["result"][0]["text"]

                # 传入客户端地址
                if asr_text:
                    await chat_with_ai(asr_text, addr)
                continue
                
            if len(data) >= 2:
                sequence = int.from_bytes(data[:2], 'big')
                audio_data = data[2:]
                print(f"收到来自 {addr} 的数据包 #{sequence}, 大小: {len(audio_data)} bytes")
                client_session.get_audio_handler().add_audio_data(audio_data)
                
        except Exception as e:
            print(f"错误: {e}")

def get_client_session(addr):
    if addr not in clients:
        clients[addr] = ClientSession()
    return clients[addr]

# 修改为分块发送的异步音频处理函数
def custom_audio_handler(audio_data: bytes, addr, file_to_save):
    chunk_size = 1024  # 设置更小的块大小，可以根据ESP32的内存情况调整
    print("Total audio data length:", len(audio_data))

    print("写入数据文件")
    
    # 将数据分块发送
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i + chunk_size]
        # print(f"Sending chunk {i//chunk_size + 1}, size: {len(chunk)}, addr: {addr}")
        file_to_save.write(chunk)
        
        # 添加1字节的消息类型(1表示音频数据)和2字节的序列号
        message_type = (1).to_bytes(1, 'big')  # 1 byte for audio type
        sequence = i // chunk_size
        sequence_bytes = sequence.to_bytes(2, 'big')  # 2 bytes for sequence
        
        # 组合消息类型、序列号和音频数据
        packet = message_type + sequence_bytes + chunk
        server_socket.sendto(packet, addr)

        time.sleep(0.01)
    

# 修改函数签名，接收客户端地址
async def chat_with_ai(text, client_addr):
    current_sentence = ""
    sentence_endings = ["，", "。", "！", "？", ",", ".", "!", "?"]  # 定义句子结束标记
    min_sentence_length = 5

    file_to_save = open("esp32_query.wav", "wb")
    
    # 创建一个闭包函数来处理音频
    def audio_handler_for_client(audio_data: bytes):
        custom_audio_handler(audio_data, client_addr, file_to_save)

    client_session = get_client_session(client_addr)
    conversation_id = client_session.get_conversation_id()
        
    for message in chat_stream(bot_id="7435549735148273679", user_id="1",
                             message=text, conversation_id=conversation_id):
        print(message)
        current_sentence += message
        
        # 检查是否遇到句子结束标记
        if len(current_sentence) >= min_sentence_length and any(current_sentence.endswith(ending) for ending in sentence_endings):
            print(f"合成语音: {current_sentence}")
            # 使用新的处理函数
            await TTS_CLIENT.query_tts(current_sentence, audio_handler_for_client)
            current_sentence = ""

    if current_sentence.strip():
        print(f"合成剩余语音: {current_sentence}")
        await TTS_CLIENT.query_tts(current_sentence, audio_handler_for_client)

    print("关闭文件")
    file_to_save.close()

# 运行主循环
if __name__ == "__main__":
    try:
        print("服务器启动")
        asyncio.run(receive_data())
    except KeyboardInterrupt:
        print("服务器关闭")
    finally:
        server_socket.close()