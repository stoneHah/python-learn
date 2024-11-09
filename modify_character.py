import os
import chardet
from pathlib import Path


def convert_to_gbk(directory):
    # 遍历指定目录下的所有文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = Path(root) / file

                # 读取文件内容
                with open(file_path, 'rb') as f:
                    content = f.read()

                # 检测原始编码
                detected = chardet.detect(content)
                original_encoding = detected['encoding']

                # 如果原始编码不是 GBK，则进行转换
                if original_encoding.lower() != 'gbk':
                    try:
                        # 解码内容
                        decoded_content = content.decode(original_encoding)

                        # 使用 GBK 编码重新写入文件
                        with open(file_path, 'w', encoding='gbk') as f:
                            f.write(decoded_content)

                        print(f"转换成功: {file_path} (从 {original_encoding} 到 GBK)")
                    except Exception as e:
                        print(f"转换失败: {file_path} - {str(e)}")
                else:
                    print(f"跳过: {file_path} (已经是 GBK 编码)")


# 使用示例
directory_path = r"C:\Users\Admin\Desktop\ruoyi"  # 替换为你的目录路径
convert_to_gbk(directory_path)
