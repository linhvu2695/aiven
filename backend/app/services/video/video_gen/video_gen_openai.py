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
from app.services.job.job_service import JobService
from app.classes.job import CreateJobRequest, JobType
from app.tasks.video.video_poll import video_poll


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

    async def generate_video(self, request: GenVideoRequest) -> GenVideoResponse:
        """Generate a video using OpenAI"""
        if is_empty_string(request.prompt):
            return GenVideoResponse(
                success=False,
                message="Prompt is required",
                job_id="",
            )

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

        # Create job record
        video_job = await JobService().create_job(CreateJobRequest(
            job_type=JobType.VIDEO_GENERATION,
            job_name=f"{JobType.VIDEO_GENERATION.value}_{request.model.value}_{operation.id}",
            metadata={
                "prompt": request.prompt, 
                "model": request.model.value if hasattr(request.model, 'value') else str(request.model),
                "aspect_ratio": request.aspect_ratio.value if request.aspect_ratio and hasattr(request.aspect_ratio, 'value') else str(request.aspect_ratio), 
                "duration": request.duration,
                "operation_id": operation.id,
            },
        ))

        if not video_job.success:
            return GenVideoResponse(
                success=False,
                message=f"Failed to create job: {video_job.message}",
                job_id="",
            )

        # Queue the polling task to check video generation status
        video_poll.apply_async(
            args=[video_job.job_id, operation.id],
            countdown=5 
        )

        # Return success with job ID for tracking
        return GenVideoResponse(
            success=True,
            message=f"Video generation started. Job ID: {video_job.job_id}",
            job_id=video_job.job_id,
        )

