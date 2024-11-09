from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)  # 存储加密后的密码
    role = Column(String(20), nullable=False)  # 'child' 或 'parent'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    conversations = relationship("Conversation", back_populates="user")
    reports = relationship("AnalysisReport", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    response = Column(Text)
    emotion = Column(String)  # 情绪标记
    topic = Column(String)    # 主题分类
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone(timedelta(hours=8)))
    )
    
    # 关系
    user = relationship("User", back_populates="conversations")

class AnalysisReport(Base):
    __tablename__ = "analysis_reports"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    love_tendency = Column(JSON)      # 恋爱倾向
    bullying_analysis = Column(JSON)  # 霸凌分析
    study_interests = Column(JSON)    # 学习兴趣
    emotional_state = Column(JSON)    # 情绪状态
    life_pattern = Column(JSON)       # 生活作息
    mental_health = Column(JSON)      # 心理健康
    social_skills = Column(JSON)      # 社交能力
    creativity = Column(JSON)         # 创造力
    family_relations = Column(JSON)   # 家庭关系
    internet_usage = Column(JSON)     # 网络使用
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="reports")