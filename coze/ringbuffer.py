class RingBuffer:
    """环形缓冲区实现"""
    def __init__(self, size):
        self.size = size
        self.buffer = bytearray(size)
        self.write_pos = 0
        self.read_pos = 0
        self.available = 0
        
    def write(self, data):
        """写入数据到缓冲区"""
        print(f"写入数据到缓冲区: {data}")
        data_len = len(data)   
        if data_len > self.size - self.available:
            print("缓冲区满了")
            return 0  # 缓冲区已满
            
        # 写入数据
        first_part = min(data_len, self.size - self.write_pos)
        self.buffer[self.write_pos:self.write_pos + first_part] = data[:first_part]
        
        if first_part < data_len:
            # 需要环绕写入
            second_part = data_len - first_part
            self.buffer[0:second_part] = data[first_part:]
            self.write_pos = second_part
        else:
            self.write_pos = (self.write_pos + first_part) % self.size
            
        self.available += data_len
        return data_len
        
    def read(self, size):
        """从缓冲区读取数据"""
        if self.available == 0:
            return bytearray(0)
            
        read_size = min(size, self.available)
        first_part = min(read_size, self.size - self.read_pos)
        result = bytearray(read_size)
        
        result[:first_part] = self.buffer[self.read_pos:self.read_pos + first_part]
        
        if first_part < read_size:
            # 需要环绕读取
            second_part = read_size - first_part
            result[first_part:] = self.buffer[0:second_part]
            self.read_pos = second_part
        else:
            self.read_pos = (self.read_pos + first_part) % self.size
            
        self.available -= read_size
        return result