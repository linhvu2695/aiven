from typing import Optional
from pydantic import BaseModel
from app.core.constants import LLMModel

class AgentInfo(BaseModel):
    id: str | None
    name: str
    description: str
    avatar: str
    model: LLMModel
    persona: str
    tone: str

class CreateOrUpdateAgentRequest(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    model: LLMModel
    persona: str
    tone: str

class CreateOrUpdateAgentResponse(BaseModel):
    success: bool
    id: str
    message: str

class SearchAgentsResponse(BaseModel):
    agents: list[AgentInfo]