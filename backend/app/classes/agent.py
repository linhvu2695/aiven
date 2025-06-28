from pydantic import BaseModel
from app.core.constants import LLMModel

class AgentInfo(BaseModel):
    id: str
    name: str
    description: str
    model: LLMModel
    persona: str
    tone: str

class CreateAgentRequest(BaseModel):
    name: str
    description: str
    model: LLMModel
    persona: str
    tone: str

class CreateAgentResponse(BaseModel):
    success: bool
    id: str
    message: str