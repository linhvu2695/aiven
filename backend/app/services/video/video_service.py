import base64
import datetime
import io
import logging
import tempfile
import os
from datetime import datetime, timezone
import cv2
import requests

from app.classes.video import CreateVideoRequest, CreateVideoResponse, VideoFormat, VideoMetadata
from app.utils.string.string_utils import validate_exactly_one_field, validate_required_fields
from app.utils.video.video_utils import generate_storage_path
from app.core.storage import FirebaseStorageRepository
from app.classes.media import MediaProcessingStatus
from app.core.database import insert_document

VIDEO_COLLECTION_NAME = "videos"
VIDEO_PRESIGNED_URL_EXPIRATION = 60 * 60  # 1 hour


class VideoService:
    """Service for managing videos with MongoDB and Firebase solution"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(VideoService, cls).__new__(cls)
        return cls._instance

    def _validate_create_video_request(self, request: CreateVideoRequest) -> tuple[bool, str]:
        """Validate create video request"""
        # Validate required fields
        is_valid, error_msg = validate_required_fields(request, ["filename", "video_type"])
        if not is_valid:
            return False, error_msg
        
        # Validate that exactly one data source is provided
        is_valid, error_msg = validate_exactly_one_field(
            request,
            ["file_data", "base64_data", "source_url"],
        )
        if not is_valid:
            return False, error_msg
        
        return True, ""

    async def _extract_video_metadata(self, video_data: bytes) -> VideoMetadata:
        """Extract metadata from video data using OpenCV"""
        try:
            # Create a temporary file to store video data
            # OpenCV requires a file path to read video
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                temp_file.write(video_data)
                temp_path = temp_file.name
            
            try:
                # Open video file with OpenCV
                cap = cv2.VideoCapture(temp_path)
                
                if not cap.isOpened():
                    logging.getLogger("uvicorn.warning").warning(
                        "Failed to open video file with OpenCV"
                    )
                    return VideoMetadata(file_size=len(video_data))
                
                # Extract metadata
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                # Calculate duration (seconds)
                duration = frame_count / fps if fps > 0 else None
                
                # Get format from fourcc code
                fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
                format_str = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
                
                # Try to map format to VideoFormat enum
                video_format = None
                try:
                    # Common format mappings
                    format_map = {
                        "avc1": VideoFormat.MP4,
                        "mp4v": VideoFormat.MP4,
                        "H264": VideoFormat.MP4,
                        "VP80": VideoFormat.WEBM,
                        "VP90": VideoFormat.WEBM,
                        "theo": VideoFormat.OGG,
                        "MJPG": VideoFormat.AVI,
                        "XVID": VideoFormat.AVI,
                    }
                    video_format = format_map.get(format_str.strip())
                except:
                    pass
                
                # Calculate bitrate (approximate)
                # bitrate = (file_size * 8) / duration
                bitrate = None
                if duration and duration > 0:
                    bitrate = int((len(video_data) * 8) / duration)
                
                # Release video capture
                cap.release()
                
                return VideoMetadata(
                    width=width if width > 0 else None,
                    height=height if height > 0 else None,
                    file_size=len(video_data),
                    format=video_format,
                    duration=duration,
                    fps=fps if fps > 0 else None,
                    bitrate=bitrate,
                )
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logging.getLogger("uvicorn.warning").warning(
                f"Failed to extract video metadata: {e}"
            )
            return VideoMetadata(file_size=len(video_data))

    async def _get_video_data_from_request(self, request: CreateVideoRequest) -> bytes:
        """Get video data from the request based on source type"""
        if request.file_data:
            return request.file_data
        elif request.base64_data:
            return base64.b64decode(request.base64_data)
        elif request.source_url:
            response = requests.get(request.source_url)
            response.raise_for_status()
            return response.content
        else:
            raise ValueError("No video data source provided")
            
    async def create_video(self, request: CreateVideoRequest) -> CreateVideoResponse:
        """Create and upload a new video"""
        valid, warning = self._validate_create_video_request(request)
        if not valid:
            logging.getLogger("uvicorn.warning").warning(warning)
            return CreateVideoResponse(
                success=False, video_id="", storage_path="", message=warning
            )

        try:
            # Get video data
            video_data = await self._get_video_data_from_request(request)

            # Extract metadata
            metadata = await self._extract_video_metadata(video_data)

            # Upload to Firebase Storage
            storage_path = generate_storage_path(request.filename)
            storage_repo = FirebaseStorageRepository()
            video_file = io.BytesIO(video_data)
            storage_url = await storage_repo.upload(video_file, storage_path)
            presigned_url = await storage_repo.get_presigned_url(
                storage_path, VIDEO_PRESIGNED_URL_EXPIRATION
            )

            # Create document for MongoDB
            now = datetime.now(timezone.utc)
            document = {
                "filename": request.filename,
                "original_filename": request.original_filename or request.filename,
                "title": request.title,
                "description": request.description,
                "alt_text": request.alt_text,
                "storage_path": storage_path,
                "storage_url": storage_url,
                "video_type": request.video_type.value,
                "source_type": request.source_type.value,
                "entity_id": request.entity_id,
                "entity_type": request.entity_type,
                "metadata": metadata.model_dump(),
                "processing_status": MediaProcessingStatus.COMPLETED.value,
                "uploaded_at": now,
                "updated_at": now,
                "processed_at": now,
                "tags": request.tags,
                "is_deleted": False,
                "ai_processed": False,
                "ai_tags": [],
                "content_moderation": None,
            }

            # Insert into MongoDB
            video_id = await insert_document(VIDEO_COLLECTION_NAME, document)

            return CreateVideoResponse(
                success=True, video_id=video_id, storage_path=storage_path, storage_url=storage_url, presigned_url=presigned_url, message="Video uploaded successfully"
            )
        except Exception as e:
            error_msg = f"Failed to create video: {str(e)}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return CreateVideoResponse(
                success=False, video_id="", storage_path="", message=error_msg
            )