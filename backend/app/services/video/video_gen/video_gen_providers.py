from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.classes.video import GenVideoRequest, GenVideoResponse


class VideoGenProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"


class VideoGenInterface(ABC):
    """Abstract base class defining the interface for video generation providers"""

    @abstractmethod
    async def generate_video(self, request: "GenVideoRequest") -> "GenVideoResponse":
        """Generate a video based on the provided request.
        """
        pass

