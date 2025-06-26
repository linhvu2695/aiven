from fastapi import APIRouter
from app.classes.chat import ChatRequest, ChatResponse
from app.services.chat.chat_service import ChatService

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    return await ChatService().generate_chat_response(request)

@router.get("/models")
async def get_models():
    return await ChatService().get_models()
