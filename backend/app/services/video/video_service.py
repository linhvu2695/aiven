import asyncio
import base64
import datetime
import io
import logging
import tempfile
import os
from datetime import datetime, timedelta, timezone
from bson import ObjectId
import cv2
import requests

from app.classes.video import CreateVideoRequest, CreateVideoResponse, GetVideoResponse, VideoFormat, VideoInfo, VideoMetadata, VideoSourceType, VideoType, VideoUrlInfo, VideoUrlResponse, VideoUrlsResponse
from app.utils.string.string_utils import validate_exactly_one_field, validate_required_fields
from app.utils.video.video_utils import generate_storage_path
from app.core.storage import FirebaseStorageRepository
from app.classes.media import MediaProcessingStatus
from app.core.database import get_document, insert_document

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
                success=True, video_id=video_id, storage_path=storage_path, storage_url=storage_url, presigned_url=presigned_url, message=""
            )
        except Exception as e:
            error_msg = f"Failed to create video: {str(e)}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return CreateVideoResponse(
                success=False, video_id="", storage_path="", message=error_msg
            )

    async def get_video(self, video_id: str) -> GetVideoResponse:
        """Get video by ID"""
        if not ObjectId.is_valid(video_id):
            return GetVideoResponse(success=False, video=None, message="Invalid document ID format")

        try:
            data = await get_document(VIDEO_COLLECTION_NAME, video_id)
            if not data:
                return GetVideoResponse(success=False, video=None, message="Video not found")

            # Convert document to VideoInfo
            video_info = VideoInfo(
                id=str(data.get("_id", "")),
                filename=data.get("filename", ""),
                original_filename=data.get("original_filename"),
                title=data.get("title"),
                description=data.get("description"),
                alt_text=data.get("alt_text"),
                storage_path=data.get("storage_path", ""),
                storage_url=data.get("storage_url"),
                video_type=VideoType(data.get("video_type", VideoType.GENERAL.value)),
                source_type=VideoSourceType(data.get("source_type", VideoSourceType.UPLOAD.value)),
                entity_id=data.get("entity_id"),
                entity_type=data.get("entity_type"),
                metadata=VideoMetadata(**data.get("metadata", {})),
                processing_status=MediaProcessingStatus(data.get("processing_status", MediaProcessingStatus.PENDING.value)),
                uploaded_at=data.get("uploaded_at") or datetime.now(timezone.utc),
                updated_at=data.get("updated_at") or datetime.now(timezone.utc),
                processed_at=data.get("processed_at"),
                tags=data.get("tags", []),
                is_deleted=data.get("is_deleted", False),
            )

            return GetVideoResponse(success=True, video=video_info, message="")
        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Failed to get video: {str(e)}")
            return GetVideoResponse(success=False, video=None, message=f"Failed to get video: {str(e)}")

    async def get_video_presigned_url(self, video_id: str) -> VideoUrlResponse:
        """Get presigned URL for video access"""
        try:
            video_response = await self.get_video(video_id)
            if not video_response.success or not video_response.video:
                logging.getLogger("uvicorn.error").error(f"Failed to get video for presigned URL: {video_response.message}")
                return VideoUrlResponse(
                    success=False, url="", 
                    expires_at=None, 
                    message=f"Failed to get video for presigned URL: {video_response.message}"
                    )

            storage_repo = FirebaseStorageRepository()
            presigned_url = await storage_repo.get_presigned_url(
                video_response.video.storage_path, VIDEO_PRESIGNED_URL_EXPIRATION
            )
            expires_at = datetime.now(timezone.utc).replace(
                second=0, microsecond=0
            ) + timedelta(seconds=VIDEO_PRESIGNED_URL_EXPIRATION)
            return VideoUrlResponse(
                success=True, url=presigned_url, 
                expires_at=expires_at, 
                message=""
                )
        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Failed to get video presigned URL: {str(e)}")
            return VideoUrlResponse(
                success=False, url="", 
                expires_at=None, 
                message=f"Failed to get video presigned URL: {str(e)}"
                )

    async def get_videos_presigned_urls(self, ids: list[str]) -> VideoUrlsResponse:
        """Get presigned URLs for multiple videos concurrently"""
        try:
            # Process all videos concurrently
            tasks = [self.get_video_presigned_url(video_id) for video_id in ids]
            results = await asyncio.gather(*tasks, return_exceptions=True) # same order as requests
            
            # Handle any exceptions from gather
            processed_results : list[VideoUrlInfo] = []
            for i, result in enumerate(results):
                if isinstance(result, VideoUrlResponse):
                    processed_results.append(VideoUrlInfo(
                        video_id=ids[i],
                        url=result.url,
                        expires_at=result.expires_at,
                        success=result.success,
                        message=result.message
                    ))
                else:
                    processed_results.append(VideoUrlInfo(
                        video_id=ids[i],
                        url=None,
                        expires_at=None,
                        success=False,
                        message=f"Failed to process: {str(result)}"
                    ))
            
            overall_success = all(result.success for result in processed_results)
            success_count = sum(1 for result in processed_results if result.success)
            total_count = len(ids)
            
            message = f"Generated presigned URLs for {success_count}/{total_count} videos"
            if not overall_success:
                message += " (some requests failed)"
            logging.getLogger("uvicorn.info").info(message)

            return VideoUrlsResponse(
                success=overall_success,
                results=processed_results,
                message=message
                )
        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Failed to get videos presigned URLs: {str(e)}")
            return VideoUrlsResponse(
                success=False, results=[], message=f"Failed to get videos presigned URLs: {str(e)}"
                )