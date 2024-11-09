from PIL import Image
import numpy as np

def convert_image_to_rgb565(image_path, output_path):
    # 打开图片
    img = Image.open(image_path)
    
    # 调整图片大小以适应屏幕（如果需要）
    # 假设屏幕分辨率为128x160
    # img = img.resize((128, 160))
    
    # 将图片转换为RGB模式
    img = img.convert('RGB')
    
    # 将图片转换为numpy数组
    pixels = np.array(img)
    
    # 转换为RGB565格式
    r = (pixels[:,:,0] >> 3).astype(np.uint16) << 11
    g = (pixels[:,:,1] >> 2).astype(np.uint16) << 5
    b = (pixels[:,:,2] >> 3).astype(np.uint16)
    rgb565 = r | g | b
    
    # 将数组转换为字节
    byte_data = rgb565.tobytes()
    
    # 将字节数据写入文件
    with open(output_path, 'w') as f:
        f.write('image = (\n')
        for i in range(0, len(byte_data), 16):
            f.write('    ' + ', '.join([f'0x{b:02x}' for b in byte_data[i:i+16]]) + ',\n')
        f.write(')\n')

    print(f"转换完成，数据已保存到 {output_path}")

# 使用示例
convert_image_to_rgb565('images/sailuo_32.jpg', 'images/sailuo_image_data.py')