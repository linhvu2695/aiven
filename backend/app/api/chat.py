from fastapi import APIRouter, Form, UploadFile, File, HTTPException, Request
from typing import List, Optional
import json
from app.classes.chat import ChatRequest, ChatResponse, ChatMessage
from app.services.chat.chat_service import ChatService

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: Request,
    # FormData parameters
    messages: Optional[str] = Form(None),
    agent: Optional[str] = Form(None),
    files: List[UploadFile] = File(None),
):
    content_type = request.headers.get("content-type", "")

    # Handle FormData (when files are uploaded)
    if content_type.startswith("multipart/form-data"):
        if messages is None or agent is None:
            raise HTTPException(
                status_code=400, detail="Messages and agent are required"
            )

        try:
            messages_data = json.loads(messages)
            chat_messages = [ChatMessage(**msg) for msg in messages_data]

            # Create ChatRequest with files
            chat_request = ChatRequest(
                messages=chat_messages,
                agent=agent,
                files=files if files and files[0].filename else None,
            )
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid messages format")

    # Handle JSON (when no files)
    elif content_type.startswith("application/json"):
        # Get the JSON body
        body = await request.json()
        messages_data = body.get("messages", [])
        agent_id = body.get("agent")

        if not messages_data or not agent_id:
            raise HTTPException(
                status_code=400, detail="Messages and agent are required"
            )

        chat_messages = [ChatMessage(**msg) for msg in messages_data]
        chat_request = ChatRequest(messages=chat_messages, agent=agent_id, files=None)

    else:
        raise HTTPException(status_code=400, detail="Invalid request format")

    return await ChatService().generate_chat_response(chat_request)


@router.get("/models")
async def get_models():
    return await ChatService().get_models()
