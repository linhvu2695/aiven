from fastapi import APIRouter, HTTPException, Request, UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile
from fastapi.responses import StreamingResponse
from typing import List, Optional
import json, logging, base64, mimetypes
from app.classes.chat import ChatRequest, ChatResponse, ChatMessage, ChatStreamChunk, ChatFileContent
from app.services.chat.chat_service import ChatService
from app.services.chat.chat_history import ConversationRepository
from app.classes.conversation import ConversationDeleteRequest

router = APIRouter()


def _get_file_type_category(mime_type: str) -> str:
    """Determine the file type category based on mime type."""
    if not mime_type:
        return "file"

    if mime_type.startswith("image/"):
        return "image"
    elif mime_type.startswith("audio/"):
        return "audio"
    elif mime_type.startswith("video/"):
        return "video"
    elif mime_type.startswith("text/"):
        return "text"
    elif mime_type in ["application/pdf"]:
        return "document"
    elif mime_type.startswith("application/"):
        return "application"
    else:
        return "file"


async def _process_upload_file(file: UploadFile) -> Optional[ChatFileContent]:
    """Convert uploaded file to ChatFileContent with base64 encoding."""
    if not file or not file.filename:
        return None

    try:
        logging.getLogger("uvicorn.info").info(f"Processing file: {file.filename}")
        
        # Read file content immediately while the file is still open
        content = await file.read()
        
        if not content:
            logging.getLogger("uvicorn.warning").warning(f"File {file.filename} appears to be empty")
            return None

        mime_type = (
            mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        )
        file_type = _get_file_type_category(mime_type)

        # Convert to base64
        base64_data = base64.b64encode(content).decode("utf-8")
        logging.getLogger("uvicorn.info").info(f"Successfully converted file to base64 (length: {len(base64_data)})")

        return ChatFileContent(
            type=file_type,
            source_type="base64",
            data=base64_data,
            mime_type=mime_type,
        )

    except Exception as e:
        logging.getLogger("uvicorn.error").error(f"Error processing file {file.filename}: {str(e)}")
        return None


async def _parse_formdata_request(request: Request) -> ChatRequest:
    """
    Parse FormData request (with files) and return ChatRequest object.
    """
    form = await request.form()

    if (form == None):
        raise HTTPException(
            status_code=400, detail="Form data is empty"
        )
    
    # Extract fields from form (ensure they are strings)
    message = str(form.get("message", ""))
    agent = str(form.get("agent", ""))
    session_id = str(form.get("session_id", ""))
    
    if message == "" or agent == "":
        raise HTTPException(
            status_code=400, detail="Message and agent are required"
        )

    # Parse chat message
    try:
        message_dict = json.loads(message)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="Invalid message format. Expected valid JSON."
        )
    
    role = message_dict.get("role", "user")
    content = message_dict.get("content", "")
    if (content.strip() == ""):
        raise HTTPException(
            status_code=400, detail="Message content is empty"
        )

    # Process files from form data
    file_contents = []
    files = form.getlist("files")
    if files:
        for file in files:
            if isinstance(file, StarletteUploadFile): # Cast to FastAPI UploadFile
                file = UploadFile(file=file.file, filename=file.filename, headers=file.headers)
            if (isinstance(file, UploadFile)):
                processed_file = await _process_upload_file(file)
                if processed_file:
                    file_contents.append(processed_file)

    return ChatRequest(
        message=content,
        agent=agent,
        session_id=session_id or "",
        file_contents=file_contents if file_contents else None,
    )


async def _parse_json_request(request: Request) -> ChatRequest:
    """
    Parse JSON request (no files) and return ChatRequest object.
    """
    body = await request.json()
    message = body.get("message")
    agent_id = body.get("agent")
    session_id = str(body.get("session_id", ""))
    
    # Validate required fields
    if not message or not agent_id:
        raise HTTPException(
            status_code=400, detail="Message and agent are required"
        )
    
    # Parse message if it's a dict
    if isinstance(message, dict):
        role = message.get("role", "user")
        content = message.get("content", "")
    else:
        content = str(message)
    
    if content.strip() == "":
        raise HTTPException(
            status_code=400, detail="Message content is empty"
        )

    return ChatRequest(
        message=content,
        agent=str(agent_id),
        session_id=session_id or "",
        file_contents=None,
    )


async def _parse_request(request: Request) -> ChatRequest:
    """
    Unified parser that handles both FormData and JSON from request body only.
    Extracts message, agent, session_id, and files directly from the request.
    """
    content_type = request.headers.get("content-type", "")

    # Handle FormData (when files are uploaded)
    if content_type.startswith("multipart/form-data"):
        return await _parse_formdata_request(request)

    # Handle JSON (when no files)
    elif content_type.startswith("application/json"):
        return await _parse_json_request(request)

    else:
        raise HTTPException(
            status_code=400, 
            detail="Invalid request format. Expected 'multipart/form-data' or 'application/json'"
        )


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: Request):
    """
    Chat endpoint that returns a chat response.
    Supports both JSON requests and FormData (with file uploads).
    """
    chat_request = await _parse_request(request)
    return await ChatService().generate_chat_response(chat_request)


@router.post("/stream")
async def stream_chat_endpoint(request: Request):
    """
    Streaming chat endpoint that returns Server-Sent Events (SSE).
    Supports both JSON requests and FormData (with file uploads).
    """
    chat_request = await _parse_request(request)

    async def generate_sse():
        """Generate Server-Sent Events format for streaming."""
        try:
            chat_service = ChatService()
            async for chunk in chat_service.generate_streaming_chat_response(
                chat_request
            ):
                # Handle ChatStreamChunk objects
                if isinstance(chunk, ChatStreamChunk):
                    response_data = {
                        "token": chunk.content,
                        "type": "token",
                        "message_id": chunk.message_id,
                        "tool_name": chunk.tool_name,
                    }

                    # Include session_id if present (typically in first chunk or completion)
                    if chunk.session_id:
                        response_data["session_id"] = chunk.session_id

                    # Mark completion if this is the final chunk
                    if chunk.is_complete:
                        response_data["type"] = "done"

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
        },
    )


@router.get("/models")
async def get_models():
    return await ChatService().get_models()


@router.get("/conversations")
async def get_conversations(limit: int = 10, agent_id: str = ""):
    return await ConversationRepository().get_conversations(limit, agent_id)


@router.get("/conversations/{id}")
async def get_conversation(id: str):
    return await ConversationRepository().get_conversation(id)


@router.delete("/conversations/{id}", response_model=ConversationDeleteRequest)
async def delete_conversation(id: str):
    result = await ConversationRepository().delete_conversation(id)
    if result.success:
        return result
    else:
        raise HTTPException(status_code=400, detail=result.message)