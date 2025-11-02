from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

from app.classes.media import MediaProcessingStatus

class VideoType(str, Enum):
    """Types of videos in the platform"""
    GENERAL = "general"

class VideoFormat(str, Enum):
    """Supported video formats"""
    MP4 = "mp4"
    WEBM = "webm"
    OGG = "ogg"
    AVI = "avi"
    MKV = "mkv"
    FLV = "flv"
    MOV = "mov"
    WMV = "wmv"
    MPEG = "mpeg"

class VideoSourceType(str, Enum):
    """Source types for videos"""
    UPLOAD = "upload"
    BASE64 = "base64"
    URL = "url"
    CAMERA = "camera"
    AI_GENERATE = "ai_generate"

class VideoMetadata(BaseModel):
    """Metadata extracted from video"""
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None  # in bytes
    format: Optional[VideoFormat] = None
    duration: Optional[float] = None  # in seconds
    fps: Optional[float] = None
    bitrate: Optional[int] = None  # in bits per second

class VideoInfo(BaseModel):
    """Comprehensive video information model"""
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
    
    # Classification
    video_type: VideoType
    source_type: VideoSourceType = VideoSourceType.UPLOAD

    # Relationships
    entity_id: Optional[str] = None  
    entity_type: Optional[str] = None
    
    # Metadata
    metadata: VideoMetadata = Field(default_factory=VideoMetadata)
    processing_status: MediaProcessingStatus = MediaProcessingStatus.PENDING
    
    # Timestamps
    uploaded_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None

    # Tags and categorization
    tags: list[str] = Field(default_factory=list)
    is_deleted: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
class CreateVideoRequest(BaseModel):
    """Request model for creating/uploading a video"""
    filename: str
    original_filename: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None

    video_type: VideoType
    source_type: VideoSourceType = VideoSourceType.UPLOAD

    # Optional relationships
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None

    # File data (one of these should be provided)
    file_data: Optional[bytes] = None  # Raw file bytes
    base64_data: Optional[str] = None  # Base64 encoded video
    source_url: Optional[str] = None  # URL to download from

    # Optional metadata
    tags: list[str] = Field(default_factory=list)

class CreateVideoResponse(BaseModel):
    """Response model for creating/uploading a video"""
    success: bool
    video_id: str
    storage_path: str
    storage_url: Optional[str] = None
    presigned_url: Optional[str] = None
    message: str

class GetVideoResponse(BaseModel):
    """Response model for getting a video"""
    success: bool
    video: Optional[VideoInfo] = None
    message: str

class VideoUrlInfo(BaseModel):
    """Information about a single video URL"""
    video_id: str
    url: Optional[str] = None
    expires_at: Optional[datetime] = None
    success: bool
    message: str

class VideoUrlsResponse(BaseModel):
    """Response model for getting multiple video URLs"""
    success: bool
    results: list[VideoUrlInfo]
    message: str

class VideoListRequest(BaseModel):
    """Request model for listing videos"""
    page: int = 1
    page_size: int = 10
    video_type: Optional[VideoType] = None
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    include_deleted: bool = False

class VideoListResponse(BaseModel):
    """Response model for listing videos"""
    videos: list[VideoInfo]
    total: int
    page: int = 1
    page_size: int = 50