import mimetypes
from google import genai
from google.genai import types

from app.classes.image import GenImageRequest, GenImageResponse
from app.core.config import settings
from app.utils.string.string_utils import is_empty_string
from app.services.image.image_gen.image_gen_aspect_ratio import ImageGenAspectRatio
from app.services.image.image_gen.image_gen_providers import ImageGenInterface

class ImageGenGemini(ImageGenInterface):
    """Service for generating images using Google Gemini"""

    _instance = None
    _model = "gemini-2.5-flash-image"

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(ImageGenGemini, cls).__new__(cls)
        return cls._instance

    def __init__(self, api_key: str = settings.gemini_api_key):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        self.client = genai.Client(api_key=api_key)

    def generate_image(self, request: GenImageRequest) -> GenImageResponse:
        if is_empty_string(request.prompt):
            return GenImageResponse(
                success=False,
                message="Prompt is required",
                image_data=None,
                text_data=None,
                mimetype=None,
            )

        text_data = ""
        data_buffer = None
        mimetype = ""
        aspect_ratio = request.aspect_ratio if request.aspect_ratio else ImageGenAspectRatio.RATIO_1_1

        content_parts = [
            types.Part.from_text(text=request.prompt),
        ]
        if request.image_data:
            content_parts.append(types.Part.from_bytes(
                mime_type="image/jpeg",
                data=request.image_data,
            ))

        try:
            for chunk in self.client.models.generate_content_stream(
                model=self._model,
                contents=[
                    types.Content(
                        role="user",
                        parts=content_parts,
                    ),
                ],
                config=types.GenerateContentConfig(
                    response_modalities=[
                        "IMAGE",
                        "TEXT",
                    ],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio.value,
                    )
                ),
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                
                if (
                    chunk.candidates[0].content.parts[0].inline_data 
                    and chunk.candidates[0].content.parts[0].inline_data.data
                ):
                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    data_buffer = inline_data.data
                    mimetype = mimetypes.guess_extension(str(inline_data.mime_type))
                else:
                    text_data = text_data + str(chunk.text)
        except Exception as e:
            return GenImageResponse(
                success=False,
                message=str(e),
                image_data=None,
                text_data=None,
                mimetype=None,
            )

        return GenImageResponse(
            success=True,
            message="",
            image_data=data_buffer,
            text_data=text_data,
            mimetype=mimetype,
        )