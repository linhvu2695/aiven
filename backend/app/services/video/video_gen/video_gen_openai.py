import logging
from typing import cast
from openai import OpenAI
from openai.types import VideoModel, VideoSeconds, VideoSize

from app.classes.video import GenVideoRequest, GenVideoResponse
from app.core.config import settings
from app.utils.string.string_utils import is_empty_string
from app.services.video.video_gen.video_gen_aspect_ratio import VideoGenAspectRatio
from app.services.video.video_gen.video_gen_providers import VideoGenInterface
from app.services.video.video_constants import VideoGenModel


class VideoGenOpenAI(VideoGenInterface):
    """Service for generating videos using OpenAI"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(VideoGenOpenAI, cls).__new__(cls)
        return cls._instance

    def __init__(self, api_key: str = settings.openai_api_key):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger("uvicorn")

    def _map_aspect_ratio(self, aspect_ratio: VideoGenAspectRatio | None) -> VideoSize:
        """
        Map aspect ratio to OpenAI video supported sizes.
        """
        if aspect_ratio is None:
            return "1280x720"
            
        aspect_ratio_map: dict[VideoGenAspectRatio, VideoSize] = {
            VideoGenAspectRatio.RATIO_4_3: "1280x720",
            VideoGenAspectRatio.RATIO_3_4: "720x1280",
            VideoGenAspectRatio.RATIO_9_16: "720x1280",  # 9:16 portrait
            VideoGenAspectRatio.RATIO_16_9: "1280x720",  # 16:9 landscape
        }
        return aspect_ratio_map.get(aspect_ratio, "1280x720")

    def _map_duration(self, duration: int | None) -> VideoSeconds:
        """
        Map duration to OpenAI video supported durations.
        """
        if duration is None:
            return "4"
        if duration not in [4, 8, 12]:
            self.logger.warning(f"Invalid duration: {duration}. Falling back to 4 seconds.")
            return "4"
        return cast(VideoSeconds, str(duration))

    def generate_video(self, request: GenVideoRequest) -> GenVideoResponse:
        """Generate a video using OpenAI"""
        if is_empty_string(request.prompt):
            return GenVideoResponse(
                success=False,
                message="Prompt is required",
                video_data=None,
                text_data=None,
                mimetype=None,
            )

        # TODO: Implement OpenAI video generation logic
        # This is a placeholder implementation
        # 
        # Expected flow:
        # 1. Validate request parameters
        # 2. Handle image_data if provided (for image-to-video)
        # 3. Map aspect ratio to OpenAI format
        # 4. Call OpenAI video generation API
        # 5. Poll for completion (if async)
        # 6. Download and return video data

        if request.image_data:
            self.logger.info(
                "Image-to-video generation not yet implemented"
            )

        operation = self.client.videos.create(
            prompt=request.prompt,
            model=VideoGenModel.SORA_2.value,
            size=self._map_aspect_ratio(request.aspect_ratio),
            seconds=self._map_duration(request.duration),
        )

        logging.getLogger("uvicorn").info(f"OpenAI video generation operation: {operation}")





        # Placeholder response
        return GenVideoResponse(
            success=True,
            message="",
            video_data=None,
            text_data=None,
            mimetype=None,
        )

