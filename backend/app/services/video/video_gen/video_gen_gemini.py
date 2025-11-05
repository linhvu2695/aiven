import logging
import mimetypes
from google import genai
from google.genai import types

from app.classes.video import GenVideoRequest, GenVideoResponse
from app.core.config import settings
from app.utils.string.string_utils import is_empty_string
from app.services.video.video_gen.video_gen_aspect_ratio import VideoGenAspectRatio
from app.services.video.video_gen.video_gen_providers import VideoGenInterface

class VideoGenGemini(VideoGenInterface):
    """Service for generating videos using Google Gemini"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(VideoGenGemini, cls).__new__(cls)
        return cls._instance

    def __init__(self, api_key: str = settings.gemini_api_key):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        self.client = genai.Client(api_key=api_key)

    def generate_video(self, request: GenVideoRequest) -> GenVideoResponse:
        """
        Generate a video using Google Gemini.
        """
        
        # Placeholder validation
        if is_empty_string(request.prompt):
            return GenVideoResponse(
                success=False,
                message="Prompt is required",
                video_data=None,
                text_data=None,
                mimetype=None,
            )
        
        # TODO: Implement actual video generation logic
        # This should follow a similar pattern to image generation but for video
        # 
        # Expected flow:
        # 1. Prepare content parts (prompt + optional image)
        # 2. Set up video generation config with aspect ratio and duration
        # 3. Call Gemini video generation API
        # 4. Stream and collect video data chunks
        # 5. Return video data with mimetype
        
        logging.getLogger("uvicorn.error").warning(
            f"Video generation with Gemini is not yet implemented. Prompt: {request.prompt}"
        )
        
        return GenVideoResponse(
            success=False,
            message="Video generation is not yet implemented. This is a placeholder.",
            video_data=None,
            text_data=None,
            mimetype=None,
        )

