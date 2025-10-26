import base64
import logging
from typing import Literal
from openai import OpenAI

from app.classes.image import GenImageRequest, GenImageResponse
from app.core.config import settings
from app.utils.string.string_utils import is_empty_string
from app.services.image.image_gen.image_gen_aspect_ratio import ImageGenAspectRatio
from app.services.image.image_gen.image_gen_providers import ImageGenInterface

# Type alias for OpenAI gpt-image-1 supported sizes
GptImage1Size = Literal["1024x1024", "1024x1536", "1536x1024"]


class ImageGenOpenAI(ImageGenInterface):
    """Service for generating images using OpenAI gpt-image-1"""

    _instance = None
    _model = "gpt-image-1"

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(ImageGenOpenAI, cls).__new__(cls)
        return cls._instance

    def __init__(self, api_key: str = settings.openai_api_key):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger("uvicorn")

    def _map_aspect_ratio_to_size(self, aspect_ratio: ImageGenAspectRatio) -> GptImage1Size:
        """
        Map aspect ratio to OpenAI gpt-image-1 supported sizes.
        gpt-image-1 supports: 1024x1024, 1024x1536, 1536x1024
        """
        aspect_ratio_map: dict[ImageGenAspectRatio, GptImage1Size] = {
            ImageGenAspectRatio.RATIO_1_1: "1024x1024",    # Square
            ImageGenAspectRatio.RATIO_2_3: "1024x1536",    # Portrait
            ImageGenAspectRatio.RATIO_3_2: "1536x1024",    # Landscape
            ImageGenAspectRatio.RATIO_3_4: "1024x1536",    # Mobile
            ImageGenAspectRatio.RATIO_4_3: "1536x1024",    # Twitter
            ImageGenAspectRatio.RATIO_4_5: "1024x1536",    # Instagram
            ImageGenAspectRatio.RATIO_5_4: "1536x1024",    # Camera
            ImageGenAspectRatio.RATIO_9_16: "1024x1536",   # Tiktok
            ImageGenAspectRatio.RATIO_16_9: "1536x1024",   # Widescreen
            ImageGenAspectRatio.RATIO_21_9: "1536x1024",   # Ultra-wide
        }
        return aspect_ratio_map.get(aspect_ratio, "1024x1024")

    def generate_image(self, request: GenImageRequest) -> GenImageResponse:
        """Generate an image using OpenAI gpt-image-1"""
        if is_empty_string(request.prompt):
            return GenImageResponse(
                success=False,
                message="Prompt is required",
                image_data=None,
                text_data=None,
                mimetype=None,
            )

        # OpenAI gpt-image-1 doesn't support image-to-image generation directly
        # If image_data is provided, we'll log a warning
        if request.image_data:
            self.logger.warning(
                "OpenAI gpt-image-1 does not support image-to-image generation. "
                "Only the text prompt will be used."
            )

        aspect_ratio = request.aspect_ratio if request.aspect_ratio else ImageGenAspectRatio.RATIO_1_1
        size = self._map_aspect_ratio_to_size(aspect_ratio)

        try:
            # Generate image using OpenAI gpt-image-1
            response = self.client.images.generate(
                model=self._model,
                prompt=request.prompt,
                size=size,
                quality="medium",  # Options: "low", "medium", "high" for gpt-image-1
                n=1,  # Number of images to generate
            )

            # Extract the generated image data
            if not response.data or len(response.data) == 0:
                return GenImageResponse(
                    success=False,
                    message="No image data returned from OpenAI",
                    image_data=None,
                    text_data=None,
                    mimetype=None,
                )

            # Get the first image result
            image_result = response.data[0]
            
            # Decode base64 image data
            if not image_result.b64_json:
                return GenImageResponse(
                    success=False,
                    message="No base64 image data in response",
                    image_data=None,
                    text_data=None,
                    mimetype=None,
                )

            image_data = base64.b64decode(image_result.b64_json)
            mimetype = ".png" # gpt-1-image returns PNG images
            text_data = "" # gpt-1-image doesn't support output text

            return GenImageResponse(
                success=True,
                message="",
                image_data=image_data,
                text_data=text_data,
                mimetype=mimetype,
            )

        except Exception as e:
            error_msg = f"Failed to generate image with OpenAI: {str(e)}"
            self.logger.error(error_msg)
            return GenImageResponse(
                success=False,
                message=error_msg,
                image_data=None,
                text_data=None,
                mimetype=None,
            )

