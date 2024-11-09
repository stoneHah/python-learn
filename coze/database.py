from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 数据库文件路径
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'chat_analysis.db')}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite 特定设置
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库基类
Base = declarative_base()

@contextmanager
def get_db():
    """
    数据库会话上下文管理器
    使用示例:
    with get_db() as db:
        db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    初始化数据库（创建所有表）
    """
    from . import models  # 导入模型
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """
    获取数据库会话（用于 FastAPI 依赖注入）
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()