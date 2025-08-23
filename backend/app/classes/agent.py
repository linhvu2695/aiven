from typing import Optional
from pydantic import BaseModel
from app.core.constants import LLMModel
from app.classes.image import ImageInfo, ImageType

class AgentAvatarInfo(ImageInfo):#     
    def __init__(self, **data):
        super().__init__(**data)
        self.image_type = ImageType.AGENT_AVATAR

class AgentInfo(BaseModel):
    id: str | None
    name: str
    description: str
    avatar: str
    model: LLMModel
    persona: str
    tone: str
    tools: list[str]

class CreateOrUpdateAgentRequest(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    model: LLMModel
    persona: str
    tone: str
    tools: list[str]

class CreateOrUpdateAgentResponse(BaseModel):
    success: bool
    id: str
    message: str

class SearchAgentsResponse(BaseModel):
    agents: list[AgentInfo]