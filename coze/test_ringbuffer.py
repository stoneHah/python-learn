import unittest
from ringbuffer import RingBuffer

class TestRingBuffer(unittest.TestCase):
    def test_basic_operations(self):
        # 创建一个大小为8的环形缓冲区
        rb = RingBuffer(8)
        
        # 测试基本写入和读取
        data = bytearray(b'1234')
        written = rb.write(data)
        self.assertEqual(written, 4)
        self.assertEqual(rb.available, 4)
        
        # 读取数据并验证
        result = rb.read(4)
        self.assertEqual(result, data)
        self.assertEqual(rb.available, 0)

    def test_wrap_around(self):
        # 测试环绕写入和读取
        rb = RingBuffer(8)
        
        # 先写入5个字节
        rb.write(bytearray(b'12345'))
        # 读取3个字节
        rb.read(3)
        # 再写入6个字节，这将导致环绕
        written = rb.write(bytearray(b'abcdef'))
        self.assertEqual(written, 6)
        
        # 读取所有数据并验证
        result = rb.read(8)
        self.assertEqual(result, bytearray(b'45abcdef'))

    def test_buffer_full(self):
        # 测试缓冲区满的情况
        rb = RingBuffer(4)
        
        # 写满缓冲区
        written = rb.write(bytearray(b'1234'))
        self.assertEqual(written, 4)
        
        # 尝试继续写入
        written = rb.write(bytearray(b'56'))
        self.assertEqual(written, 0)  # 应该返回0表示写入失败

    def test_empty_read(self):
        # 测试空缓冲区读取
        rb = RingBuffer(4)
        
        result = rb.read(1)
        self.assertEqual(len(result), 0)  # 应该返回空bytearray

if __name__ == '__main__':
    unittest.main() 