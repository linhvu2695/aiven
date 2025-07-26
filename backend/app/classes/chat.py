from pydantic import BaseModel
from typing import List, Optional
from fastapi import UploadFile

class ChatMessage(BaseModel):
    role: str  # "user", "assistant", etc.
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    agent: str
    files: Optional[List[UploadFile]] = None

class ChatResponse(BaseModel):
    response: str

class ChatFileContent(BaseModel):
    type: str
    source_type: str
    data: str
    mime_type: str

class ChatFileUrl(BaseModel):
    type: str
    source_type: str = "url"
    url: str