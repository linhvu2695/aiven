import logging
import mimetypes
from google import genai
from google.genai import types

from app.classes.image import GenImageResponse
from app.core.config import settings

class ImageGenGemini:
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

    def generate_image(self, prompt: str) -> GenImageResponse:
        text_data = ""
        data_buffer = None
        mimetype = ""

        try:
            for chunk in self.client.models.generate_content_stream(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=[
                        "IMAGE",
                        "TEXT",
                    ],
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
                message=str(e),
                image_data=None,
                text_data=None,
                mimetype=None,
            )

        return GenImageResponse(
            message="",
            image_data=data_buffer,
            text_data=text_data,
            mimetype=mimetype,
        )