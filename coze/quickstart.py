import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Generator
from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType, COZE_CN_BASE_URL

load_dotenv()

app = FastAPI()

# 添加 CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，生产环境建议设置具体的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)

coze = Coze(auth=TokenAuth(os.getenv("COZE_API_TOKEN")), base_url=COZE_CN_BASE_URL)

class ChatRequest(BaseModel):
    bot_id: str
    user_id: str
    message: str

def chat_stream(bot_id: str, user_id: str, message: str) -> Generator[str, None, None]:
    for event in coze.chat.stream(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[Message.build_user_question_text(message)]
    ):
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            message = event.message
            yield f"data: {{'role': '{message.role}', 'content': '{message.content}'}}\n\n"

@app.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        chat_stream(request.bot_id, request.user_id, request.message),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)