from typing import Optional
from PIL import Image as PILImage
import io
import logging
from datetime import datetime, timezone
from app.classes.image import ImageType

def generate_storage_path(image_type: ImageType, entity_id: Optional[str], filename: str) -> str:
    """Generate a standardized storage path for images"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base_folder = get_image_folder_by_type(image_type)
    
    if image_type == ImageType.PLANT_PHOTO and entity_id:
        return f"{base_folder}/{entity_id}/photos/{timestamp}_{filename}"
    elif image_type == ImageType.AGENT_AVATAR and entity_id:
        return f"{base_folder}/{entity_id}/avatar/{filename}"
    elif image_type == ImageType.USER_AVATAR and entity_id:
        return f"{base_folder}/{entity_id}/avatar/{filename}"
    elif image_type == ImageType.ARTICLE_ATTACHMENT and entity_id:
        return f"{base_folder}/{entity_id}/attachments/{timestamp}_{filename}"
    elif image_type == ImageType.REPRESENTATIVE and entity_id:
        return f"{base_folder}/{entity_id}/{timestamp}_{filename}"
    else:
        return f"{base_folder}/{timestamp}_{filename}"

def get_image_folder_by_type(image_type: ImageType) -> str:
    """Get the base folder for an image type"""
    folder_map = {
        ImageType.PLANT_PHOTO: "plants",
        ImageType.AGENT_AVATAR: "agents",
        ImageType.USER_AVATAR: "users", 
        ImageType.ARTICLE_ATTACHMENT: "articles",
        ImageType.GENERAL: "general",
        ImageType.REPRESENTATIVE: "representatives"
    }
    return folder_map.get(image_type, "general")

def detect_image_mime_type(image_bytes: bytes) -> str:
    """Detect MIME type from image bytes using PIL"""
    try:
        with PILImage.open(io.BytesIO(image_bytes)) as img:
            format_to_mime = {
                "JPEG": "image/jpeg",
                "PNG": "image/png",
                "GIF": "image/gif",
                "BMP": "image/bmp",
                "WEBP": "image/webp",
                "TIFF": "image/tiff",
            }
            return format_to_mime.get(img.format or "JPEG", "image/jpeg")
    except Exception as e:
        logging.getLogger("uvicorn.warning").warning(
            f"Failed to detect image format: {e}, defaulting to image/jpeg"
        )
        return "image/jpeg"