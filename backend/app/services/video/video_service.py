import asyncio
import base64
import datetime
import io
import logging
import tempfile
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from bson import ObjectId
import cv2
import requests

from app.classes.video import CreateVideoRequest, CreateVideoResponse, DeleteVideoRequest, DeleteVideoResponse, GetVideoResponse, VideoFormat, VideoInfo, VideoMetadata, VideoSourceType, VideoType, VideoUrlInfo, VideoUrlsRequest, VideoUrlsResponse, VideoListRequest, VideoListResponse, VideoGenerateRequest, VideoGenerateResponse, GenVideoRequest
from app.classes.image import CreateImageRequest, ImageType, ImageSourceType
from app.utils.string.string_utils import is_empty_string, validate_exactly_one_field, validate_required_fields
from app.utils.video.video_utils import generate_storage_path
from app.core.storage import FirebaseStorageRepository
from app.classes.media import MediaProcessingStatus
from app.core.database import delete_document, get_document, insert_document, find_documents_with_filters, count_documents_with_filters, update_document
from app.services.image.image_service import ImageService
from app.utils.file.file_utils import create_temp_local_file
from app.services.image.image_constants import IMAGE_COLLECTION_NAME
from app.services.video.video_constants import GEMINI_MODELS, OPENAI_MODELS
from app.services.video.video_gen.video_gen_gemini import VideoGenGemini
from app.services.video.video_gen.video_gen_providers import VideoGenInterface
from app.services.video.video_gen.video_gen_openai import VideoGenOpenAI

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
        """Extract metadata from video file using OpenCV"""
        try:
            try:
                temp_path = create_temp_local_file(video_data, ".mp4")
                
                # Open video file with OpenCV
                cap = cv2.VideoCapture(temp_path)
                
                if not cap.isOpened():
                    logging.getLogger("uvicorn.warning").warning(
                        "Failed to open video file with OpenCV"
                    )
                    return VideoMetadata(file_size=os.path.getsize(temp_path))
                
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

    async def _extract_video_thumbnail(
        self, 
        video_data: bytes, 
        video_id: str,
    ) -> Optional[str]:
        """
        Extract a thumbnail image from video data and save it as a REPRESENTATIVE image
            
        Returns:
            Image ID of the created thumbnail, or None if extraction failed
        """
        if is_empty_string(video_id):
            logging.getLogger("uvicorn.warning").warning("Video ID is required")
            return None
        
        try:
            try:
                temp_path = create_temp_local_file(video_data, ".mp4")
                    
                # Open video file with OpenCV
                cap = cv2.VideoCapture(temp_path)
                
                if not cap.isOpened():
                    logging.getLogger("uvicorn.warning").warning(
                        "Failed to open video file for thumbnail extraction"
                    )
                    return None
                
                # Get total frame count and calculate middle frame
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                middle_frame = frame_count // 2 if frame_count > 0 else 0
                
                # Set position to middle frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
                
                # Read the frame
                ret, frame = cap.read()
                
                if not ret or frame is None:
                    logging.getLogger("uvicorn.warning").warning(
                        "Failed to read frame for thumbnail extraction"
                    )
                    cap.release()
                    return None
                
                # Release video capture
                cap.release()
                
                # Encode frame as JPEG (keep in BGR format, JPEG encoder will handle it correctly)
                success, buffer = cv2.imencode('.jpg', frame)
                if not success:
                    logging.getLogger("uvicorn.warning").warning(
                        "Failed to encode thumbnail image"
                    )
                    return None
                
                # Convert to bytes
                thumbnail_data = buffer.tobytes()
                thumbnail_filename = f"video_{video_id}_thumbnail.jpg"
                
                # Create image request for thumbnail
                image_request = CreateImageRequest(
                    filename=thumbnail_filename,
                    original_filename=thumbnail_filename,
                    title=f"Thumbnail for video {video_id}",
                    description="Auto-generated thumbnail from video",
                    image_type=ImageType.REPRESENTATIVE,
                    source_type=ImageSourceType.BASE64,
                    entity_id=video_id,
                    entity_type="video",
                    file_data=thumbnail_data,
                )
                
                # Create the thumbnail image
                image_service = ImageService()
                response = await image_service.create_image(image_request)
                
                if response.success:
                    logging.getLogger("uvicorn.info").info(
                        f"Successfully created thumbnail image {response.image_id} for video {video_id}"
                    )
                    return response.image_id
                else:
                    logging.getLogger("uvicorn.warning").warning(
                        f"Failed to create thumbnail image: {response.message}"
                    )
                    return None
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logging.getLogger("uvicorn.error").error(
                f"Failed to extract video thumbnail: {e}"
            )
            return None

    async def _fetch_thumbnail_urls(self, video_ids: list[str], results: list[VideoUrlInfo]) -> None:
        """
        Fetch thumbnail presigned URLs for videos and update the results in place.
        
        Args:
            video_ids: List of video IDs to fetch thumbnails for
            results: List of VideoUrlInfo objects to update with thumbnail URLs (modified in place)
        """
        if not video_ids or len(video_ids) == 0:
            logging.getLogger("uvicorn.warning").warning("No video IDs provided")
            return
        
        if not results or len(results) == 0:
            logging.getLogger("uvicorn.warning").warning("No results provided")
            return
        
        try:            
            filters = {
                "entity_id": {"$in": video_ids},
                "entity_type": "video",
                "image_type": ImageType.REPRESENTATIVE.value,
                "is_deleted": False
            }
            
            # Fetch all matching thumbnail images from the database
            IMAGE_COLLECTION_NAME = "images"
            thumbnail_docs = await find_documents_with_filters(
                IMAGE_COLLECTION_NAME,
                filters,
                skip=0,
                sort_by="uploaded_at",
                asc=False  # Get most recent thumbnails first
            )
            
            if not thumbnail_docs or len(thumbnail_docs) == 0:
                logging.getLogger("uvicorn.info").info("No thumbnails found for any videos")
                return
            
            # Build mapping of video_id -> thumbnail_image_id
            video_to_thumbnail_map: Dict[str, str] = {}
            for doc in thumbnail_docs:
                entity_id = doc.get("entity_id")
                image_id = str(doc.get("_id"))
                if (not is_empty_string(entity_id) 
                    and not is_empty_string(image_id) 
                    and ObjectId.is_valid(image_id) 
                    and entity_id not in video_to_thumbnail_map
                    ):
                    video_to_thumbnail_map[str(entity_id)] = str(image_id)
            
            # Fetch presigned URLs for all thumbnails using ImageService
            thumbnail_image_ids = list(video_to_thumbnail_map.values())
            image_service = ImageService()
            image_urls_response = await image_service.get_images_presigned_urls(thumbnail_image_ids)
            
            # Build mapping of image_id -> (url, expires_at) from the response
            thumbnail_url_map: Dict[str, tuple[Optional[str], Optional[datetime]]] = {}
            for image_url_info in image_urls_response.results:
                if image_url_info.success:
                    thumbnail_url_map[image_url_info.image_id] = (image_url_info.url, image_url_info.expires_at)
                else:
                    thumbnail_url_map[image_url_info.image_id] = (None, None)
            
            # Update results with thumbnail URLs
            for result in results:
                thumbnail_image_id = video_to_thumbnail_map.get(result.video_id)
                if  not is_empty_string(thumbnail_image_id) and thumbnail_image_id in thumbnail_url_map:
                    thumbnail_url, thumbnail_expires_at = thumbnail_url_map[thumbnail_image_id]
                    result.thumbnail_url = thumbnail_url
                    result.thumbnail_expires_at = thumbnail_expires_at
                    
        except Exception as e:
            # Don't fail the whole operation if thumbnail fetching fails
            logging.getLogger("uvicorn.error").error(f"Failed to fetch thumbnail URLs: {str(e)}")

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

    async def _get_video_presigned_url(self, video_id: str) -> VideoUrlInfo:
        """Get presigned URL for video access"""
        try:
            video_response = await self.get_video(video_id)
            if not video_response.success or not video_response.video:
                logging.getLogger("uvicorn.error").error(f"Failed to get video for presigned URL: {video_response.message}")
                return VideoUrlInfo(
                    video_id=video_id,
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
            return VideoUrlInfo(
                video_id=video_id,
                url=presigned_url, 
                expires_at=expires_at, 
                success=True,
                message=""
                )
        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Failed to get video presigned URL: {str(e)}")
            return VideoUrlInfo(
                video_id=video_id,
                url="", 
                expires_at=None, 
                success=False,
                message=f"Failed to get video presigned URL: {str(e)}"
                )

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

            # Extract and save thumbnail image (non-blocking, failures are logged but don't affect video creation)
            try:
                thumbnail_image_id = await self._extract_video_thumbnail(
                    video_data=video_data,
                    video_id=video_id,
                )
                if thumbnail_image_id:
                    logging.getLogger("uvicorn.info").info(
                        f"Thumbnail extracted successfully for video {video_id}: {thumbnail_image_id}"
                    )
            except Exception as e:
                # Log the error but don't fail the video creation
                logging.getLogger("uvicorn.warning").warning(
                    f"Failed to extract thumbnail for video {video_id}: {e}"
                )

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

    async def get_videos_presigned_urls(self, request: VideoUrlsRequest) -> VideoUrlsResponse:
        """Get presigned URLs for multiple videos concurrently"""
        if not request.video_ids or len(request.video_ids) == 0:
            return VideoUrlsResponse(
                success=True, results=[], message="No video IDs provided"
            )
        
        try:
            # Process all videos concurrently
            tasks = [self._get_video_presigned_url(video_id) for video_id in request.video_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True) # same order as requests
            
            # Handle any exceptions from gather
            processed_results : list[VideoUrlInfo] = []
            for i, result in enumerate(results):
                if isinstance(result, VideoUrlInfo):
                    processed_results.append(result)
                else:
                    processed_results.append(VideoUrlInfo(
                        video_id=request.video_ids[i],
                        url=None,
                        expires_at=None,
                        success=False,
                        message=f"Failed to process: {str(result)}"
                    ))
            
            overall_success = all(result.success for result in processed_results)
            success_count = sum(1 for result in processed_results if result.success)
            total_count = len(request.video_ids)
            
            message = f"Generated presigned URLs for {success_count}/{total_count} videos"
            if not overall_success:
                message += " (some requests failed)"
            logging.getLogger("uvicorn.info").info(message)

            # Fetch thumbnail presigned URLs if requested
            if request.retrieve_thumbnail:
                await self._fetch_thumbnail_urls(request.video_ids, processed_results)
                thumbnail_success_count = sum(
                    1 for result 
                    in processed_results 
                    if not is_empty_string(result.thumbnail_url)
                    )
                message += f" and {thumbnail_success_count}/{total_count} thumbnails"

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

    async def list_videos(self, request: VideoListRequest) -> VideoListResponse:
        """List videos with optional filtering"""
        try:
            # Build filters dictionary for multi-field filtering
            filters: Dict[str, Any] = {}
            if not request.include_deleted:
                filters["is_deleted"] = False

            if request.video_type:
                filters["video_type"] = request.video_type.value
            if request.entity_id:
                filters["entity_id"] = request.entity_id
            if request.entity_type:
                filters["entity_type"] = request.entity_type

            # Get total count for pagination
            total_count = await count_documents_with_filters(
                VIDEO_COLLECTION_NAME, filters
            )

            # Calculate pagination
            skip = (request.page - 1) * request.page_size

            # Get paginated documents
            documents = await find_documents_with_filters(
                VIDEO_COLLECTION_NAME,
                filters,
                skip=skip,
                limit=request.page_size,
                sort_by="updated_at",
                asc=False,  # Most recent first
            )

            # Convert to VideoInfo objects
            videos = []
            for doc in documents:
                video_info = VideoInfo(
                    id=str(doc.get("_id", "")),
                    filename=doc.get("filename", ""),
                    original_filename=doc.get("original_filename"),
                    title=doc.get("title"),
                    description=doc.get("description"),
                    alt_text=doc.get("alt_text"),
                    notes=doc.get("notes"),
                    storage_path=doc.get("storage_path", ""),
                    storage_url=doc.get("storage_url"),
                    video_type=VideoType(
                        doc.get("video_type", VideoType.GENERAL.value)
                    ),
                    source_type=VideoSourceType(
                        doc.get("source_type", VideoSourceType.UPLOAD.value)
                    ),
                    entity_id=doc.get("entity_id"),
                    entity_type=doc.get("entity_type"),
                    metadata=VideoMetadata(**doc.get("metadata", {})),
                    processing_status=MediaProcessingStatus(
                        doc.get(
                            "processing_status", MediaProcessingStatus.PENDING.value
                        )
                    ),
                    uploaded_at=doc.get("uploaded_at") or datetime.now(timezone.utc),
                    updated_at=doc.get("updated_at") or datetime.now(timezone.utc),
                    processed_at=doc.get("processed_at"),
                    tags=doc.get("tags", []),
                    is_deleted=doc.get("is_deleted", False),
                )
                videos.append(video_info)

            return VideoListResponse(
                videos=videos, total=total_count, page=request.page, page_size=request.page_size
            )

        except Exception as e:
            error_msg = f"Failed to list videos: {str(e)}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return VideoListResponse(videos=[], total=0, page=request.page, page_size=request.page_size)

    async def delete_video(self, request: DeleteVideoRequest) -> DeleteVideoResponse:
        """Delete a video"""
        if not ObjectId.is_valid(request.video_id):
            return DeleteVideoResponse(success=False, message="Invalid document ID format")

        try:
            data = await get_document(VIDEO_COLLECTION_NAME, request.video_id)
            if not data:
                return DeleteVideoResponse(success=False, message="Video not found")

            if request.soft_delete:
                await update_document(VIDEO_COLLECTION_NAME, request.video_id, {
                    "is_deleted": True,
                    "updated_at": datetime.now(timezone.utc)
                })
            else:
                # Hard delete - remove from storage and database
                storage_path = data.get("storage_path", "")
                if not is_empty_string(storage_path):
                    try:
                        await FirebaseStorageRepository().delete(storage_path)
                    except Exception as storage_exc:
                        logging.getLogger("uvicorn.warning").warning(
                            f"Failed to delete video from storage for video {request.video_id}: {storage_exc}"
                        )
                        # Returns immediately to prevent orphaned storage without DB records
                        return DeleteVideoResponse(success=False, message=f"Failed to delete video from storage: {storage_exc}")
                
                # Delete from MongoDB
                await delete_document(VIDEO_COLLECTION_NAME, request.video_id)

                # Delete thumbnail image if it exists
                filters = {
                    "entity_id": request.video_id,
                    "entity_type": "video",
                    "image_type": ImageType.REPRESENTATIVE.value
                }
                thumbnail_images = await find_documents_with_filters(IMAGE_COLLECTION_NAME, filters)
                deleted_thumbnail_images = 0
                for thumbnail_image in thumbnail_images:
                    thumbnail_image_id = str(thumbnail_image.get("_id", ""))
                    if ObjectId.is_valid(thumbnail_image_id):
                        await ImageService().delete_image(thumbnail_image_id, soft_delete=False)
                        deleted_thumbnail_images += 1
                logging.getLogger("uvicorn.info").info(f"Deleted {deleted_thumbnail_images}/{len(thumbnail_images)} thumbnail images for video {request.video_id}")
                
            return DeleteVideoResponse(success=True, message="")
        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Failed to delete video: {str(e)}")
            return DeleteVideoResponse(success=False, message=f"Failed to delete video: {str(e)}")

    async def generate_video(self, request: VideoGenerateRequest) -> VideoGenerateResponse:
        """Generate a video using AI models"""
        # Get video generation provider
        gen_provider: VideoGenInterface | None = None
        if request.model in GEMINI_MODELS:
            gen_provider = VideoGenGemini()
        elif request.model in OPENAI_MODELS:
            gen_provider = VideoGenOpenAI()
        else:
            return VideoGenerateResponse(
                success=False, 
                video_id="", 
                message=f"Model {request.model} not supported"
            )

        # Get image data if needed
        image_data = None
        if request.image_id:
            image_response = await ImageService().get_image(request.image_id)
            if not image_response.success or not image_response.image:
                return VideoGenerateResponse(
                    success=False, 
                    video_id="", 
                    message=f"Image not found. Error: {image_response.message}"
                )
            image_data = await FirebaseStorageRepository().download(image_response.image.storage_path)

        # Generate video
        genvideo_response = gen_provider.generate_video(GenVideoRequest(
            prompt=request.prompt, 
            image_data=image_data,
            model=request.model,
            aspect_ratio=request.aspect_ratio,
            duration=request.duration
        ))

        if not genvideo_response.success or not genvideo_response.video_data:
            return VideoGenerateResponse(success=False, video_id="", message=genvideo_response.message)

        # Persist video to database
        create_video_response = await self.create_video(CreateVideoRequest(
            filename=f"video_{request.model.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{genvideo_response.mimetype}",
            video_type=VideoType.GENERAL,
            source_type=VideoSourceType.AI_GENERATE,
            file_data=genvideo_response.video_data,
            description=f"Generated video for prompt: {request.prompt}. Model: {request.model.value}",
        ))

        if not create_video_response.success:
            return VideoGenerateResponse(success=False, video_id="", message=create_video_response.message)

        return VideoGenerateResponse(
            success=True,
            video_id=create_video_response.video_id,
            text_data=genvideo_response.text_data,
            message=""
        )

    async def get_models(self) -> dict[str, list[dict[str, str]]]:
        """Get available video generation models"""
        from app.services.video.video_constants import VideoGenModel
        
        def model_info(model: VideoGenModel) -> dict[str, str]:
            return {"value": model.value, "label": model.value}

        return {
            "google_genai": [model_info(model) for model in GEMINI_MODELS],
            "openai": [],  # No OpenAI models yet
        }