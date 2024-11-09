import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from coze.database import engine
from coze.models import Base

def init_db():
    """初始化数据库（创建所有表）"""
    print(f"Creating database at: {engine.url}")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()