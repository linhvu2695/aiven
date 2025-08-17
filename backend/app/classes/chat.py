from pydantic import BaseModel
from typing import List, Optional, Union, Any, Dict

class MessageContentItem(BaseModel):
    type: str
    text: Optional[str] = None
    source_type: Optional[str] = None
    data: Optional[str] = None
    mime_type: Optional[str] = None
    url: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: Union[str, List[MessageContentItem]]  # support multimodal

class ChatResponse(BaseModel):
    response: str

class ChatStreamChunk(BaseModel):
    content: str = ""
    session_id: str = ""
    is_complete: bool = False

class ChatFileContent(BaseModel):
    type: str
    source_type: str
    data: str
    mime_type: str

class ChatFileUrl(BaseModel):
    type: str
    source_type: str = "url"
    url: str

class ChatRequest(BaseModel):
    message: str
    session_id: str = ""
    agent: str
    file_contents: Optional[List[ChatFileContent]] = None