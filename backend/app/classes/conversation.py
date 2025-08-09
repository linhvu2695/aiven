from datetime import datetime, timezone
from langchain_core.messages.base import BaseMessage
from pydantic import BaseModel, Field

class Conversation(BaseModel):
    id: str
    messages: list[BaseMessage]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))