from enum import Enum

VIDEO_COLLECTION_NAME = "videos"
VIDEO_STORAGE_FOLDER = "videos"
VIDEO_PRESIGNED_URL_EXPIRATION = 60 * 60  # 1 hour

class VideoGenModel(str, Enum):
    # https://ai.google.dev/gemini-api/docs/veo
    VEO_3_1 = "veo-3.1-generate-preview"
    
    # Placeholder for future video generation models
    # OPENAI_VIDEO_MODEL = "openai-video-model"

OPENAI_MODELS = set()

GEMINI_MODELS = {
    VideoGenModel.VEO_3_1,
}

