from enum import Enum
from typing import Dict, Optional, List
from pydantic import BaseModel
from app.services.chat.chat_constants import LLMModel
from app.classes.image import ImageInfo, ImageType
from app.classes.chat import ChatMessage

class TrajectoryMatchMode(str, Enum):
    STRICT = "strict"
    UNORDERED = "unordered"
    SUPERSET = "superset"
    SUBSET = "subset"

class ToolArgsMatchMode(str, Enum):
    EXACT = "exact"
    IGNORE = "ignore"

class AgentAvatarInfo(ImageInfo):#     
    def __init__(self, **data):
        super().__init__(**data)
        self.image_type = ImageType.AGENT_AVATAR

class AgentInfo(BaseModel):
    id: str | None
    name: str
    description: str
    avatar_image_url: str | None
    avatar_image_id: str | None
    model: LLMModel
    persona: str
    tone: str
    tools: list[str]

class CreateOrUpdateAgentRequest(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    avatar_image_id: Optional[str] = None
    model: LLMModel
    persona: str
    tone: str
    tools: list[str]

class CreateOrUpdateAgentResponse(BaseModel):
    success: bool
    id: str
    message: str

class DeleteAgentResponse(BaseModel):
    success: bool
    id: str
    message: str

class UpdateAgentAvatarResponse(BaseModel):
    success: bool
    agent_id: str
    image_id: str
    storage_url: str
    message: str

class SearchAgentsResponse(BaseModel):
    agents: list[AgentInfo]

class EvaluateAgentRequest(BaseModel):
    agent_id: str
    input_messages: List[ChatMessage]
    expected_trajectory: list[dict]
    trajectory_match_mode: TrajectoryMatchMode = TrajectoryMatchMode.STRICT
    tool_args_match_mode: ToolArgsMatchMode = ToolArgsMatchMode.EXACT
    llm_as_a_judge: bool = False # if True, LLM-as-a-Judge will be used instead of TrajectoryMatch
    tool_mocks: Optional[Dict[str, str]] = None  # Map of tool_name -> mock_response

class EvaluateAgentResponse(BaseModel):
    success: bool
    score: bool  # True if trajectory matches, False otherwise
    key: str  # Evaluation key (e.g., "trajectory_strict_match")
    comment: Optional[str] = None  # Optional comment from evaluator
    actual_trajectory: list[dict]  # Actual trajectory that was evaluated
    message: str