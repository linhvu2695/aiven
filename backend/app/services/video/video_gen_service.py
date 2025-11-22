"""
Video Generation Service - handles AI video generation requests
"""
from app.classes.video import VideoGenerateRequest, VideoGenerateResponse, GenVideoRequest
from app.services.video.video_constants import GEMINI_MODELS, OPENAI_MODELS, VideoGenModel
from app.services.video.video_gen.video_gen_gemini import VideoGenGemini
from app.services.video.video_gen.video_gen_openai import VideoGenOpenAI
from app.services.video.video_gen.video_gen_providers import VideoGenInterface
from app.services.image.image_service import ImageService
from app.core.storage import FirebaseStorageRepository


class VideoGenService:
    """Service for AI video generation"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(VideoGenService, cls).__new__(cls)
        return cls._instance

    async def generate_video(self, request: VideoGenerateRequest) -> VideoGenerateResponse:
        """Generate a video using AI models"""
        # Get video generation provider
        gen_provider: VideoGenInterface | None = None
        if request.model in GEMINI_MODELS:
            gen_provider = VideoGenGemini()
        elif request.model in OPENAI_MODELS:
            gen_provider = VideoGenOpenAI()
        else:
            return VideoGenerateResponse(
                success=False, 
                job_id="", 
                message=f"Model {request.model} not supported"
            )

        # Get image data if needed
        image_data = None
        if request.image_id:
            image_response = await ImageService().get_image(request.image_id)
            if not image_response.success or not image_response.image:
                return VideoGenerateResponse(
                    success=False, 
                    job_id="", 
                    message=f"Image not found. Error: {image_response.message}"
                )
            image_data = await FirebaseStorageRepository().download(image_response.image.storage_path)

        # Generate video
        genvideo_response = await gen_provider.generate_video(GenVideoRequest(
            prompt=request.prompt, 
            image_data=image_data,
            model=request.model,
            aspect_ratio=request.aspect_ratio,
            duration=request.duration
        ))
        if not genvideo_response.success or not genvideo_response.job_id:
            return VideoGenerateResponse(success=False, job_id="", message=genvideo_response.message)

        return VideoGenerateResponse(
            success=True,
            job_id=genvideo_response.job_id,
            message=""
        )

    async def get_models(self) -> dict[str, list[dict[str, str]]]:
        """Get available video generation models"""        
        def model_info(model: VideoGenModel) -> dict[str, str]:
            return {"value": model.value, "label": model.value}

        return {
            "google_genai": [model_info(model) for model in GEMINI_MODELS],
            "openai": [model_info(model) for model in OPENAI_MODELS],
        }

