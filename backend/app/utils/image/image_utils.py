from typing import Optional
from datetime import datetime
from app.classes.image import ImageType

def generate_storage_path(image_type: ImageType, entity_id: Optional[str], filename: str) -> str:
    """Generate a standardized storage path for images"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if image_type == ImageType.PLANT_PHOTO and entity_id:
        return f"plants/{entity_id}/photos/{timestamp}_{filename}"
    elif image_type == ImageType.AGENT_AVATAR and entity_id:
        return f"agents/{entity_id}/avatar/{filename}"
    elif image_type == ImageType.USER_AVATAR and entity_id:
        return f"users/{entity_id}/avatar/{filename}"
    elif image_type == ImageType.ARTICLE_ATTACHMENT and entity_id:
        return f"articles/{entity_id}/attachments/{timestamp}_{filename}"
    else:
        return f"general/{timestamp}_{filename}"

def get_image_folder_by_type(image_type: ImageType) -> str:
    """Get the base folder for an image type"""
    folder_map = {
        ImageType.PLANT_PHOTO: "plants",
        ImageType.AGENT_AVATAR: "agents",
        ImageType.USER_AVATAR: "users", 
        ImageType.ARTICLE_ATTACHMENT: "articles",
        ImageType.GENERAL: "general"
    }
    return folder_map.get(image_type, "general")