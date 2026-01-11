from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AddTextEpisodeRequest(BaseModel):
    title: str
    content: str
    description: Optional[str] = None
    reference_time: Optional[datetime] = None


class AddTextEpisodeResponse(BaseModel):
    success: bool
    episode_uuid: Optional[str] = None
    message: str
