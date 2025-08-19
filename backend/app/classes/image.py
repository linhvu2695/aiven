from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class ImageType(str, Enum):
    """Types of images in the platform"""
    PLANT_PHOTO = "plant_photo"
    AGENT_AVATAR = "agent_avatar"
    USER_AVATAR = "user_avatar"
    CHAT_ATTACHMENT = "chat_attachment"
    ARTICLE_ATTACHMENT = "article_attachment"
    GENERAL = "general"

class ImageFormat(str, Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"
    SVG = "svg"
    AVIF = "avif"

class ImageSourceType(str, Enum):
    """Source types for images"""
    UPLOAD = "upload"
    BASE64 = "base64"
    URL = "url"
    CAMERA = "camera"

class ImageProcessingStatus(str, Enum):
    """Status of image processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ImageMetadata(BaseModel):
    """Metadata extracted from image"""
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None  # in bytes
    format: Optional[ImageFormat] = None
    color_mode: Optional[str] = None  # RGB, RGBA, etc.
    dpi: Optional[tuple[int, int]] = None
    exif_data: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[Dict[str, Any]] = None  # AI-generated analysis

class ImageInfo(BaseModel):
    """Comprehensive image information model"""
    id: Optional[str] = None
    filename: str
    original_filename: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None
    notes: Optional[str] = None
    
    # Storage information
    storage_path: str  # Path in Firebase Storage
    storage_url: Optional[str] = None  # Public URL
    presigned_url: Optional[str] = None  # Temporary access URL
    presigned_url_expires_at: Optional[datetime] = None
    
    # Classification
    image_type: ImageType
    source_type: ImageSourceType = ImageSourceType.UPLOAD
    
    # Relationships
    entity_id: Optional[str] = None  # Related entity (plant_id, agent_id, etc.)
    entity_type: Optional[str] = None  # Type of related entity
    
    # Metadata
    metadata: ImageMetadata = Field(default_factory=ImageMetadata)
    processing_status: ImageProcessingStatus = ImageProcessingStatus.PENDING
    
    # Timestamps
    uploaded_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    
    # Tags and categorization
    tags: list[str] = Field(default_factory=list)
    is_deleted: bool = False
    
    # AI and analysis
    ai_processed: bool = False
    ai_tags: list[str] = Field(default_factory=list)
    content_moderation: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CreateImageRequest(BaseModel):
    """Request model for creating/uploading an image"""
    filename: str
    original_filename: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None
    
    image_type: ImageType
    source_type: ImageSourceType = ImageSourceType.UPLOAD
    
    # Optional relationships
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    
    # File data (one of these should be provided)
    file_data: Optional[bytes] = None  # Raw file bytes
    base64_data: Optional[str] = None  # Base64 encoded image
    source_url: Optional[str] = None  # URL to download from
    
    # Optional metadata
    tags: list[str] = Field(default_factory=list)
    
class UpdateImageRequest(BaseModel):
    """Request model for updating image information"""
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None
    tags: Optional[list[str]] = None
    is_public: Optional[bool] = None
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None

class ImageUploadResponse(BaseModel):
    """Response model for image upload operations"""
    success: bool
    image_id: str
    storage_path: str
    storage_url: Optional[str] = None
    presigned_url: Optional[str] = None
    message: str

class ImageResponse(BaseModel):
    """Response model for single image operations"""
    success: bool
    image: Optional[ImageInfo] = None
    message: str

class ImageListResponse(BaseModel):
    """Response model for listing images"""
    images: list[ImageInfo]
    total: int
    page: int = 1
    page_size: int = 50

class ImageUrlResponse(BaseModel):
    """Response model for getting image URLs"""
    success: bool
    url: str
    expires_at: Optional[datetime] = None
    message: str

class ImageProcessingResponse(BaseModel):
    """Response model for image processing operations"""
    success: bool
    image_id: str
    processing_status: ImageProcessingStatus
    metadata: Optional[ImageMetadata] = None
    message: str

class DeleteImageResponse(BaseModel):
    """Response model for image deletion"""
    success: bool
    deleted_image_id: str
    message: str



