from enum import Enum

IMAGE_COLLECTION_NAME = "images"
IMAGE_STORAGE_FOLDER = "images"
IMAGE_PRESIGNED_URL_EXPIRATION = 60 * 60  # 1 hour

class ImageGenModel(str, Enum):
    # https://ai.google.dev/gemini-api/docs/imagen
    GEMINI_2_5_FLASH_IMAGE = "gemini-2.5-flash-image"
    GEMINI_3_PRO_IMAGE_PREVIEW = "gemini-3-pro-image-preview"

    # https://platform.openai.com/docs/guides/images-vision
    GPT_IMAGE_1 = "gpt-image-1"
    GPT_IMAGE_1_MINI = "gpt-image-1-mini"

OPENAI_MODELS = {
    ImageGenModel.GPT_IMAGE_1,
    ImageGenModel.GPT_IMAGE_1_MINI,
}

GEMINI_MODELS = {
    ImageGenModel.GEMINI_2_5_FLASH_IMAGE,
    ImageGenModel.GEMINI_3_PRO_IMAGE_PREVIEW,
}