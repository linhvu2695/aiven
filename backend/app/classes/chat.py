from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str  # "user", "assistant", etc.
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    agent: str

class ChatResponse(BaseModel):
    response: str
