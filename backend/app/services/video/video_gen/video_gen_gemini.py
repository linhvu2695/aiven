import logging
import mimetypes
import time
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

        image = (
            types.Image(
                image_bytes=request.image_data,
                mime_type="image/jpeg",
            )
            if request.image_data
            else None
        )

        aspect_ratio = (
            request.aspect_ratio.value
            if request.aspect_ratio
            else VideoGenAspectRatio.RATIO_16_9.value
        )

        duration = 4
        if request.duration:
            if request.duration not in [4, 8]:
                logging.getLogger("uvicorn.error").error(f"Invalid Gemini duration: {request.duration}. Falling back to 4 seconds.")
            else:
                duration = request.duration

        operation = self.client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=request.prompt,
            image=image,
            config=types.GenerateVideosConfig(
                duration_seconds=duration,
                aspect_ratio=aspect_ratio,
            ),
        )

        # Poll the operation status until the video is ready.
        while not operation.done:
            print("Waiting for video generation to complete...")
            time.sleep(10)
            operation = self.client.operations.get(operation)

        # Download the video.
        if not operation.response:
            return GenVideoResponse(
                success=False,
                message="Failed to generate video: No response from Gemini",
                video_data=None,
                text_data=None,
                mimetype=None,
            )
        if not operation.response.generated_videos:
            return GenVideoResponse(
                success=False,
                message=f"Failed to generate video: No generated videos. Error: {operation.error}",
                video_data=None,
                text_data=None,
                mimetype=None,
            )

        video = operation.response.generated_videos[0]
        if not video.video:
            return GenVideoResponse(
                success=False,
                message="Failed to generate video: empty video file from Gemini",
                video_data=None,
                text_data=None,
                mimetype=None,
            )

        self.client.files.download(file=video.video)
        video.video.save("veo3.1_with_interpolation.mp4")
        print("Generated video saved to veo3.1_with_interpolation.mp4")

        return GenVideoResponse(
            success=True,
            message="",
            video_data=video.video.video_bytes,
            text_data=None,
            mimetype=video.video.mime_type,
        )
