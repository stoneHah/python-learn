from langchain_community.chat_models import ChatCoze
from langchain_core.messages import HumanMessage
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
import asyncio

load_dotenv()

app = FastAPI()

async def generate_events(chat, message):
    for event in chat.stream([HumanMessage(content=message)]):
        yield event
        # 添加小延迟以避免过快发送
        await asyncio.sleep(0.1)

@app.post("/chat")
async def chat_endpoint(request: Request):
    # 从请求体获取消息
    data = await request.json()
    message = data.get("message", "")
    
    chat = ChatCoze(
        bot_id="7433341011986120731",
        user="123",
        conversation_id="222",
        streaming=True,
    )
    
    return EventSourceResponse(
        generate_events(chat, message),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
