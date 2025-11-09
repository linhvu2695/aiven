from enum import Enum

VIDEO_COLLECTION_NAME = "videos"
VIDEO_STORAGE_FOLDER = "videos"
VIDEO_PRESIGNED_URL_EXPIRATION = 60 * 60  # 1 hour

class VideoGenModel(str, Enum):
    # https://ai.google.dev/gemini-api/docs/veo
    VEO_3_1 = "veo-3.1-generate-preview"
    
    # https://platform.openai.com/docs/guides/video-generation#models
    SORA_2 = "sora-2"

OPENAI_MODELS = {
    VideoGenModel.SORA_2,
}

GEMINI_MODELS = {
    VideoGenModel.VEO_3_1,
}

