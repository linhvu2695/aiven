from datetime import datetime, timezone
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field

class Conversation(BaseModel):
    id: str
    name: str
    messages: list[HumanMessage|AIMessage]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConversationInfo(BaseModel):
    session_id: str
    name: str
    updated_at: datetime