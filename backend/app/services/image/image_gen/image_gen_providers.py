from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.classes.image import GenImageRequest, GenImageResponse


class ImageGenProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"


class ImageGenInterface(ABC):
    """Abstract base class defining the interface for image generation providers"""

    @abstractmethod
    def generate_image(self, request: "GenImageRequest") -> "GenImageResponse":
        """
        Generate an image based on the provided request.
        """
        pass