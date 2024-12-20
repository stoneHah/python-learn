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

from coze import models
from coze.database import get_db_session, init_db

app = FastAPI(title="儿童对话分析系统",
    root_path="/aimage-chat-i"
)

# CORS 设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 模型
class ChatMessage(BaseModel):
    bot_id: Optional[str] = None
    message: str
    conversation_id: str

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

@app.get("/conversation/id")
async def get_conversation_id():
    """
    获取新的会话ID
    """
    try:
        conversation_id = coze.conversations.create().id
        return {"conversation_id": conversation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

aimage_bot_id = '7450315141968674831'

@app.post("/aimage/customer/{user_id}")
async def customer(
    user_id: int,
    chat_message: ChatMessage,
):
    """
    处理用户对话请求并保存对话记录
    返回 SSE 流式响应
    """
    try:
        return StreamingResponse(
            chat_stream(
                aimage_bot_id,
                user_id,
                chat_message.message,
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/{user_id}")
async def chat(
    user_id: int,
    chat_message: ChatMessage,
    db: Session = Depends(get_db_session)
):
    """
    处理用户对话请求并保存对话记录
    返回 SSE 流式响应
    """
    try:
        return StreamingResponse(
            chat_stream(
                chat_message.bot_id,
                user_id,
                chat_message.message,
                db  # 传入数据库会话
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/report/{user_id}")
async def generate_report(
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db_session)
):
    """
    生成指定时间段的分析报告
    """
    if end_date:
        end_date = end_date + timedelta(days=1)
    # 查询指定时间段内的对话记录
    conversations = db.query(models.Conversation).filter(
        models.Conversation.user_id == user_id,
        models.Conversation.created_at >= start_date,
        models.Conversation.created_at < end_date
    ).all()

    if not conversations:
        raise HTTPException(status_code=404, detail="未找到指定时间段内的对话记录")

    """
    处理用户对话请求并保存对话记录
    返回 SSE 流式响应
    """
    # 提取所有对话内容
    messages = [conv.message for conv in conversations]
    try:
        return StreamingResponse(
            report_stream(
                messages
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{user_id}", response_model=ConversationListResponse)
async def get_conversations(
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db_session)
):
    """
    获取指定用户的对话记录，支持时间范围筛选和分页
    """
    try:
        query = db.query(models.Conversation).filter(
            models.Conversation.user_id == user_id
        )
        
        # 添加时间范围过滤
        if start_date:
            query = query.filter(models.Conversation.created_at >= start_date)
        if end_date:
            # 将结束日期加一天，以包含整个结束日期
            end_date = end_date + timedelta(days=1)
            query = query.filter(models.Conversation.created_at < end_date)
            
        # 计算总记录数
        total = query.count()
        
        # 添加分页
        conversations = query.order_by(models.Conversation.created_at.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
            
        # 将 SQLAlchemy 模型转换为 Pydantic 模型
        conversation_responses = [
            ConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                message=conv.message,
                response=conv.response,
                emotion=conv.emotion,
                topic=conv.topic,
                created_at=conv.created_at
            ) for conv in conversations
        ]
            
        return ConversationListResponse(
            total=total,
            items=conversation_responses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 分析功能实现
def analyze_emotion(message: str) -> str:
    """情绪分析"""
    # TODO: 实现情绪分析逻辑
    return "neutral"

def classify_topic(message: str) -> str:
    """主题分类"""
    # TODO: 实现主题分类逻辑
    return "general"

def analyze_love_tendency(conversations: List[models.Conversation]) -> dict:
    """分析恋爱倾向"""
    # TODO: 实现恋爱倾向分析逻辑
    return {"level": "low", "keywords": [], "details": ""}

def analyze_bullying(conversations: List[models.Conversation]) -> dict:
    """分析霸凌情况"""
    # TODO: 实现霸凌分析逻辑
    return {"risk_level": "low", "incidents": [], "suggestions": []}

def analyze_study_interests(conversations: List[models.Conversation]) -> dict:
    """分析学习兴趣"""
    # TODO: 实现学习兴趣分析逻辑
    return {"subjects": [], "books": [], "learning_style": ""}

def analyze_emotional_state(conversations: List[models.Conversation]) -> dict:
    """分析情绪状态"""
    # TODO: 实现情绪状态分析逻辑
    return {"overall_mood": "stable", "mood_changes": [], "concerns": []}

def analyze_life_pattern(conversations: List[models.Conversation]) -> dict:
    """分析生活作息"""
    # TODO: 实现生活作息分析逻辑
    return {"sleep_pattern": "", "activity_level": "", "routine": []}

def analyze_mental_health(conversations: List[models.Conversation]) -> dict:
    """分析心理健康状况"""
    # TODO: 实现心理健康分析逻辑
    return {"status": "healthy", "stress_level": "low", "recommendations": []}

def report_stream(messages: List[str]) -> Generator[str, None, None]:
    """
    处理报告流式响应
    """
    # 将消息列表拼接为编号文本
    formatted_text = "\n".join([f"{i+1}. {message}" for i, message in enumerate(messages)])
    
    for event in coze.chat.stream(
        bot_id='7433987342346190900',
        user_id='123',  # 转换为字符串
        additional_messages=[Message.build_user_question_text(formatted_text)]
    ):
        print(event)
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            message = event.message
            # 对 content 进行 JSON 转义处理
            escaped_content = json.dumps(message.content)[1:-1]  # 去掉首尾的引号
            yield f"data: {{\"role\": \"{message.role}\", \"content\": \"{escaped_content}\"}}\n\n"

def chat_stream(
    bot_id: str, 
    user_id: str, 
    message: str,
    db: Optional[Session] = None,
    conversation_id: Optional[str] = None,
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
        print(event)
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            message = event.message
            # 对 content 进行 JSON 转义处理
            escaped_content = json.dumps(message.content)[1:-1]  # 去掉首尾的引号
            yield f"data: {{\"role\": \"{message.role}\", \"content\": \"{escaped_content}\"}}\n\n"

        if event.event == ChatEventType.CONVERSATION_MESSAGE_COMPLETED:
            message = event.message
            if not answered:
                response_messages = message.content
                answered = True
            else:
                # 解析JSON响应获取情绪和主题
                try:
                    response_data = json.loads(message.content)
                    if isinstance(response_data, dict) and "output" in response_data:
                        analysis_data = json.loads(response_data["output"])
                        emotion = analysis_data.get("emotion", "")
                        topic = analysis_data.get("topic", "")
                except (json.JSONDecodeError, KeyError):
                    emotion = ""
                    topic = ""

        if event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
            if db:
                # 如果是最终响应，保存到数据库
                conversation = models.Conversation(
                        user_id=user_id,
                        message=user_message,  # 使用原始用户消息
                        response=response_messages,
                        emotion=emotion,
                        topic=topic
                    )
                db.add(conversation)
                db.commit()

