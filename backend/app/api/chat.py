from fastapi import APIRouter, Form, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional
import json
from app.classes.chat import ChatRequest, ChatResponse, ChatMessage, ChatStreamChunk
from app.services.chat.chat_service import ChatService

router = APIRouter()


async def parse_chat_request(
    request: Request,
    message: Optional[str] = None,
    agent: Optional[str] = None,
    session_id: Optional[str] = None,
    files: Optional[List[UploadFile]] = None,
) -> ChatRequest:
    """
    Parse chat request from either FormData (with files) or JSON format.
    Returns a ChatRequest object ready for processing.
    """
    content_type = request.headers.get("content-type", "")

    # Handle FormData (when files are uploaded)
    if content_type.startswith("multipart/form-data"):
        if message is None or agent is None:
            raise HTTPException(
                status_code=400, detail="Message and agent are required"
            )

        try:
            message_data = json.loads(message)
            chat_message = ChatMessage(**message_data)

            # Create ChatRequest with files
            return ChatRequest(
                message=chat_message,
                agent=agent,
                session_id=session_id or "",
                files=files if files and len(files) > 0 and files[0].filename else None,
            )
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid message format")

    # Handle JSON (when no files)
    elif content_type.startswith("application/json"):
        # Get the JSON body
        body = await request.json()
        message_data = body.get("message")
        agent_id = body.get("agent")
        session_id = body.get("session_id", "")

        if not message_data or not agent_id:
            raise HTTPException(
                status_code=400, detail="Message and agent are required"
            )

        try:
            chat_message = ChatMessage(**message_data)
            return ChatRequest(
                message=chat_message, 
                agent=agent_id, 
                session_id=session_id or "",
                files=None
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid message format: {str(e)}")

    else:
        raise HTTPException(status_code=400, detail="Invalid request format")


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: Request,
    # FormData parameters
    message: Optional[str] = Form(None),
    agent: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    files: List[UploadFile] = File(None),
):
    """
    Chat endpoint that returns a chat response.
    Supports both JSON requests and FormData (with file uploads).
    """
    chat_request = await parse_chat_request(request, message, agent, session_id, files)
    return await ChatService().generate_chat_response(chat_request)


@router.post("/stream")
async def stream_chat_endpoint(
    request: Request,
    # FormData parameters
    message: Optional[str] = Form(None),
    agent: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    files: List[UploadFile] = File(None),
):
    """
    Streaming chat endpoint that returns Server-Sent Events (SSE).
    Supports both JSON requests and FormData (with file uploads).
    """
    chat_request = await parse_chat_request(request, message, agent, session_id, files)
    
    async def generate_sse():
        """Generate Server-Sent Events format for streaming."""
        try:
            chat_service = ChatService()
            async for chunk in chat_service.generate_streaming_chat_response(chat_request):
                # Handle ChatStreamChunk objects
                if isinstance(chunk, ChatStreamChunk):
                    response_data = {
                        'token': chunk.content,
                        'type': 'token'
                    }
                    
                    # Include session_id if present (typically in first chunk or completion)
                    if chunk.session_id:
                        response_data['session_id'] = chunk.session_id
                    
                    # Mark completion if this is the final chunk
                    if chunk.is_complete:
                        response_data['type'] = 'done'
                    
                    # Format as Server-Sent Events
                    yield f"data: {json.dumps(response_data)}\n\n"
                    
                    # If this is completion chunk, we're done
                    if chunk.is_complete:
                        return
                else:
                    # Fallback for backward compatibility (if somehow string is yielded)
                    yield f"data: {json.dumps({'content': str(chunk), 'type': 'token'})}\n\n"
            
        except Exception as e:
            # Send error signal
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_sse(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",  # Adjust for your frontend domain
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )


@router.get("/models")
async def get_models():
    return await ChatService().get_models()
