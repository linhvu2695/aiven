from app.classes.video import VideoType
from typing import Optional
from datetime import datetime, timezone

VIDEO_BASE_FOLDER = "videos"

def generate_storage_path(filename: str) -> str:
    """Generate a standardized storage path for videos"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{VIDEO_BASE_FOLDER}/{timestamp}_{filename}"