from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import json
from fastapi.responses import StreamingResponse
from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType, COZE_CN_BASE_URL
from typing import Generator
import os
from dotenv import load_dotenv




# Pydantic 模型
class ChatMessage(BaseModel):
    bot_id: str
    message: str

class ReportRequest(BaseModel):
    user_id: int
    start_date: datetime
    end_date: datetime

class ReportResponse(BaseModel):
    id: int
    user_id: int
    start_date: datetime
    end_date: datetime
    love_tendency: dict
    bullying_analysis: dict
    study_interests: dict
    emotional_state: dict
    life_pattern: dict
    mental_health: dict
    created_at: datetime

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    response: str
    emotion: str
    topic: str
    created_at: datetime

class ConversationListResponse(BaseModel):
    total: int
    items: List[ConversationResponse]

# 加载环境变量
load_dotenv()

# 初始化 Coze 客户端
coze = Coze(auth=TokenAuth(os.getenv("COZE_API_TOKEN")), base_url=COZE_CN_BASE_URL)

# 初始化数据库
# @app.on_event("startup")
# async def startup_event():
#     init_db()

# API 路由

def create_conversation_id():
    conversation = coze.conversations.create()
    return conversation.id

def chat_stream(
    bot_id: str, 
    user_id: str, 
    message: str,
    conversation_id: Optional[str] = None
) -> Generator[str, None, None]:
    """
    处理对话流式响应
    """
    # 保存原始用户消息
    user_message = message
    response_messages = ''
    # 是否已回答
    answered = False
    
    for event in coze.chat.stream(
        bot_id=bot_id,
        user_id=str(user_id),  # 转换为字符串
        additional_messages=[Message.build_user_question_text(message)],
        conversation_id=conversation_id
    ):
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            message = event.message
            yield message.content


