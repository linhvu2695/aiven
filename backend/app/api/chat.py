from fastapi import APIRouter
from app.classes.chat import ChatRequest, ChatResponse
from app.services.chat.chat_service import generate_chat_response

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    return await generate_chat_response(request)
