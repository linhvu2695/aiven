import logging
import base64
import io
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from PIL import Image as PILImage
from PIL.ExifTags import TAGS
import requests
import asyncio

from app.classes.image import (
    GenImageRequest,
    ImageGenerateRequest,
    ImageGenerateResponse,
    ImageInfo,
    CreateImageRequest,
    ImageListRequest,
    UpdateImageRequest,
    ImageCreateResponse,
    ImageResponse,
    ImageListResponse,
    ImageUrlResponse,
    DeleteImageResponse,
    ImageMetadata,
    ImageFormat,
    ImageProcessingStatus,
    ImageType,
    ImageSourceType,
    ImageUrlInfo,
    ImageUrlsResponse,
)
from app.core.database import (
    insert_document,
    get_document,
    update_document,
    delete_document,
    find_documents_with_filters,
    count_documents_with_filters,
)
from app.core.storage import FirebaseStorageRepository
from app.utils.string.string_utils import (
    validate_required_fields,
    validate_exactly_one_field,
)
from app.utils.image.image_utils import generate_storage_path
from app.services.image.image_gen.image_gen_gemini import ImageGenGemini
from app.services.image.image_gen.image_gen_openai import ImageGenOpenAI
from app.services.image.image_gen.image_gen_providers import ImageGenProvider

IMAGE_COLLECTION_NAME = "images"
IMAGE_STORAGE_FOLDER = "images"
IMAGE_PRESIGNED_URL_EXPIRATION = 60 * 60  # 1 hour


class ImageService:
    """Service for managing images with MongoDB and Firebase solution"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(ImageService, cls).__new__(cls)
        return cls._instance

    def _validate_create_image_request(
        self, request: CreateImageRequest
    ) -> tuple[bool, str]:
        """Validate create image request"""
        # Validate required fields
        is_valid, error_msg = validate_required_fields(
            request,
            ["filename", "image_type"],
        )
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

    async def _extract_image_metadata(self, image_data: bytes) -> ImageMetadata:
        """Extract metadata from image data using PIL"""
        try:
            with PILImage.open(io.BytesIO(image_data)) as img:
                metadata = ImageMetadata(
                    width=img.width,
                    height=img.height,
                    file_size=len(image_data),
                    format=ImageFormat(img.format.lower()) if img.format else None,
                    color_mode=img.mode,
                )

                # Extract DPI if available
                if hasattr(img, "info") and "dpi" in img.info:
                    metadata.dpi = img.info["dpi"]

                # Extract EXIF data if available
                if hasattr(img, "getexif"):
                    exif_dict = img.getexif()
                    if exif_dict:
                        exif_data = {}
                        for tag_id, value in exif_dict.items():
                            tag = TAGS.get(tag_id, tag_id)
                            exif_data[tag] = str(value)
                        metadata.exif_data = exif_data

                return metadata
        except Exception as e:
            logging.getLogger("uvicorn.warning").warning(
                f"Failed to extract image metadata: {e}"
            )
            return ImageMetadata(file_size=len(image_data))

    async def _get_image_data_from_request(self, request: CreateImageRequest) -> bytes:
        """Get image data from the request based on source type"""
        if request.file_data:
            return request.file_data
        elif request.base64_data:
            return base64.b64decode(request.base64_data)
        elif request.source_url:
            response = requests.get(request.source_url)
            response.raise_for_status()
            return response.content
        else:
            raise ValueError("No image data source provided")

    async def create_image(self, request: CreateImageRequest) -> ImageCreateResponse:
        """Create and upload a new image"""
        valid, warning = self._validate_create_image_request(request)
        if not valid:
            logging.getLogger("uvicorn.warning").warning(warning)
            return ImageCreateResponse(
                success=False, image_id="", storage_path="", message=warning
            )

        try:
            # Get image data
            image_data = await self._get_image_data_from_request(request)

            # Extract metadata
            metadata = await self._extract_image_metadata(image_data)

            # Upload to Firebase Storage
            storage_path = generate_storage_path(
                request.image_type, request.entity_id, request.filename
            )
            storage_repo = FirebaseStorageRepository()
            image_file = io.BytesIO(image_data)
            storage_url = await storage_repo.upload(image_file, storage_path)
            presigned_url = await storage_repo.get_presigned_url(
                storage_path, IMAGE_PRESIGNED_URL_EXPIRATION
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
                "image_type": request.image_type.value,
                "source_type": request.source_type.value,
                "entity_id": request.entity_id,
                "entity_type": request.entity_type,
                "metadata": metadata.model_dump(),
                "processing_status": ImageProcessingStatus.COMPLETED.value,
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
            image_id = await insert_document(IMAGE_COLLECTION_NAME, document)

            return ImageCreateResponse(
                success=True,
                image_id=image_id,
                storage_path=storage_path,
                storage_url=storage_url,
                presigned_url=presigned_url,
                message="Image uploaded successfully",
            )

        except Exception as e:
            error_msg = f"Failed to create image: {str(e)}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return ImageCreateResponse(
                success=False, image_id="", storage_path="", message=error_msg
            )

    async def get_image(self, image_id: str) -> ImageResponse:
        """Get image by ID"""
        try:
            data = await get_document(IMAGE_COLLECTION_NAME, image_id)

            # Convert document to ImageInfo
            image_info = ImageInfo(
                id=str(data.get("_id", "")),
                filename=data.get("filename", ""),
                original_filename=data.get("original_filename"),
                title=data.get("title"),
                description=data.get("description"),
                alt_text=data.get("alt_text"),
                notes=data.get("notes"),
                storage_path=data.get("storage_path", ""),
                storage_url=data.get("storage_url"),
                image_type=ImageType(data.get("image_type", ImageType.GENERAL.value)),
                source_type=ImageSourceType(
                    data.get("source_type", ImageSourceType.UPLOAD.value)
                ),
                entity_id=data.get("entity_id"),
                entity_type=data.get("entity_type"),
                metadata=ImageMetadata(**data.get("metadata", {})),
                processing_status=ImageProcessingStatus(
                    data.get("processing_status", ImageProcessingStatus.PENDING.value)
                ),
                uploaded_at=data.get("uploaded_at") or datetime.now(timezone.utc),
                updated_at=data.get("updated_at") or datetime.now(timezone.utc),
                processed_at=data.get("processed_at"),
                tags=data.get("tags", []),
                is_deleted=data.get("is_deleted", False),
            )

            return ImageResponse(
                success=True, image=image_info, message="Image retrieved successfully"
            )

        except ValueError as e:
            return ImageResponse(success=False, image=None, message=str(e))
        except Exception as e:
            error_msg = f"Failed to get image: {str(e)}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return ImageResponse(success=False, image=None, message=error_msg)

    async def update_image(
        self, image_id: str, request: UpdateImageRequest
    ) -> ImageResponse:
        """Update image information"""
        try:
            # Build update document with only provided fields
            update_doc: Dict[str, Any] = {"updated_at": datetime.now(timezone.utc)}

            if request.title is not None:
                update_doc["title"] = request.title
            if request.description is not None:
                update_doc["description"] = request.description
            if request.alt_text is not None:
                update_doc["alt_text"] = request.alt_text
            if request.tags is not None:
                update_doc["tags"] = request.tags
            if request.notes is not None:
                update_doc["notes"] = request.notes

            # Update document
            await update_document(IMAGE_COLLECTION_NAME, image_id, update_doc)

            # Return updated image
            return await self.get_image(image_id)

        except Exception as e:
            error_msg = f"Failed to update image: {str(e)}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return ImageResponse(success=False, image=None, message=error_msg)

    async def list_images(self, request: ImageListRequest) -> ImageListResponse:
        """List images with optional filtering"""
        try:
            # Build filters dictionary for multi-field filtering
            filters: Dict[str, Any] = {}
            if not request.include_deleted:
                filters["is_deleted"] = False

            if request.image_type:
                filters["image_type"] = request.image_type.value
            if request.entity_id:
                filters["entity_id"] = request.entity_id
            if request.entity_type:
                filters["entity_type"] = request.entity_type

            # Get total count for pagination
            total_count = await count_documents_with_filters(
                IMAGE_COLLECTION_NAME, filters
            )

            # Calculate pagination
            skip = (request.page - 1) * request.page_size

            # Get paginated documents
            documents = await find_documents_with_filters(
                IMAGE_COLLECTION_NAME,
                filters,
                skip=skip,
                limit=request.page_size,
                sort_by="updated_at",
                asc=False,  # Most recent first
            )

            # Convert to ImageInfo objects
            images = []
            for doc in documents:
                image_info = ImageInfo(
                    id=str(doc.get("_id", "")),
                    filename=doc.get("filename", ""),
                    original_filename=doc.get("original_filename"),
                    title=doc.get("title"),
                    description=doc.get("description"),
                    alt_text=doc.get("alt_text"),
                    notes=doc.get("notes"),
                    storage_path=doc.get("storage_path", ""),
                    storage_url=doc.get("storage_url"),
                    image_type=ImageType(
                        doc.get("image_type", ImageType.GENERAL.value)
                    ),
                    source_type=ImageSourceType(
                        doc.get("source_type", ImageSourceType.UPLOAD.value)
                    ),
                    entity_id=doc.get("entity_id"),
                    entity_type=doc.get("entity_type"),
                    metadata=ImageMetadata(**doc.get("metadata", {})),
                    processing_status=ImageProcessingStatus(
                        doc.get(
                            "processing_status", ImageProcessingStatus.PENDING.value
                        )
                    ),
                    uploaded_at=doc.get("uploaded_at") or datetime.now(timezone.utc),
                    updated_at=doc.get("updated_at") or datetime.now(timezone.utc),
                    processed_at=doc.get("processed_at"),
                    tags=doc.get("tags", []),
                    is_deleted=doc.get("is_deleted", False),
                )
                images.append(image_info)

            return ImageListResponse(
                images=images, total=total_count, page=request.page, page_size=request.page_size
            )

        except Exception as e:
            error_msg = f"Failed to list images: {str(e)}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return ImageListResponse(images=[], total=0, page=request.page, page_size=request.page_size)

    async def get_image_presigned_url(self, image_id: str) -> ImageUrlResponse:
        """Get presigned URL for image access"""
        try:
            image_response = await self.get_image(image_id)
            if not image_response.success or not image_response.image:
                return ImageUrlResponse(
                    success=False, url="", message=f"Image not found. Error: {image_response.message}"
                )

            presigned_url = await FirebaseStorageRepository().get_presigned_url(
                image_response.image.storage_path, IMAGE_PRESIGNED_URL_EXPIRATION
            )
            expires_at = datetime.now(timezone.utc).replace(
                second=0, microsecond=0
            ) + timedelta(seconds=IMAGE_PRESIGNED_URL_EXPIRATION)

            return ImageUrlResponse(
                success=True,
                url=presigned_url,
                expires_at=expires_at,
                message="Presigned URL generated successfully",
            )

        except Exception as e:
            error_msg = f"Failed to get image URL: {str(e)}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return ImageUrlResponse(success=False, url="", message=error_msg)

    async def delete_image(self, image_id: str, soft_delete: bool = True) -> DeleteImageResponse:
        """Delete image (soft delete by default)"""
        try:
            if soft_delete:
                # Soft delete - mark as deleted
                update_doc = {
                    "is_deleted": True,
                    "updated_at": datetime.now(timezone.utc),
                }
                await update_document(IMAGE_COLLECTION_NAME, image_id, update_doc)
            else:
                # Hard delete - remove from storage and database
                data = await get_document(IMAGE_COLLECTION_NAME, image_id)
                storage_path = data.get("storage_path", "")

                # Delete from Firebase Storage
                if storage_path:
                    try:
                        await FirebaseStorageRepository().delete(storage_path)
                    except Exception as storage_exc:
                        logging.getLogger("uvicorn.warning").warning(
                            f"Failed to delete image from storage for image {image_id}: {storage_exc}"
                        )
                        return DeleteImageResponse(
                            success=False,
                            deleted_image_id=image_id,
                            message=f"Failed to delete image from storage: {storage_exc}",
                        )
                else:
                    logging.getLogger("uvicorn.warning").warning(
                        f"No storage path found for image {image_id}"
                    )

                # Delete from MongoDB
                await delete_document(IMAGE_COLLECTION_NAME, image_id)

            return DeleteImageResponse(
                success=True,
                deleted_image_id=image_id,
                message="Image deleted successfully",
            )

        except Exception as e:
            error_msg = f"Failed to delete image: {str(e)}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return DeleteImageResponse(
                success=False, deleted_image_id=image_id, message=error_msg
            )

    async def get_images_presigned_urls(self, ids: list[str]) -> ImageUrlsResponse:
        """Get presigned URLs for multiple images concurrently"""
        try:
            # Process all images concurrently
            tasks = [self.get_image_presigned_url(image_id) for image_id in ids]
            results = await asyncio.gather(*tasks, return_exceptions=True) # same order as requests
            
            # Handle any exceptions from gather
            processed_results : list[ImageUrlInfo] = []
            for i, result in enumerate(results):
                if isinstance(result, ImageUrlResponse):
                    processed_results.append(ImageUrlInfo(
                        image_id=ids[i],
                        url=result.url,
                        expires_at=result.expires_at,
                        success=result.success,
                        message=result.message
                    ))
                else:
                    processed_results.append(ImageUrlInfo(
                        image_id=ids[i],
                        url=None,
                        expires_at=None,
                        success=False,
                        message=f"Failed to process: {str(result)}"
                    ))
            
            overall_success = all(result.success for result in processed_results)
            success_count = sum(1 for result in processed_results if result.success)
            total_count = len(ids)
            
            message = f"Generated presigned URLs for {success_count}/{total_count} images"
            if not overall_success:
                message += " (some requests failed)"
            logging.getLogger("uvicorn.info").info(message)
            
            return ImageUrlsResponse(
                success=overall_success,
                results=processed_results,
                message=message
            )
            
        except Exception as e:
            error_msg = f"Failed to get multiple image URLs: {str(e)}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return ImageUrlsResponse(
                success=False,
                results=[],
                message=error_msg
            )

    async def generate_image(self, request: ImageGenerateRequest) -> ImageGenerateResponse:
        # Get image generation provider
        gen_provider = None
        if request.provider == ImageGenProvider.GEMINI:
            gen_provider = ImageGenGemini()
        elif request.provider == ImageGenProvider.OPENAI:
            gen_provider = ImageGenOpenAI()
        
        if not gen_provider:
            return ImageGenerateResponse(
                success=False, 
                image_id="", 
                message=f"Provider {request.provider} not supported"
                )

        # Get image data if needed
        image_data = None
        if request.image_id:
            image_response = await self.get_image(request.image_id)
            if not image_response.success or not image_response.image:
                return ImageGenerateResponse(
                    success=False, 
                    image_id="", 
                    message=f"Image not found. Error: {image_response.message}"
                    )
            image_data = await FirebaseStorageRepository().download(image_response.image.storage_path)

        # Generate image
        genimage_response = gen_provider.generate_image(GenImageRequest(
            prompt=request.prompt, 
            image_data=image_data,
            aspect_ratio=request.aspect_ratio
            ))

        if not genimage_response.success or not genimage_response.image_data:
            return ImageGenerateResponse(success=False, image_id="", message=genimage_response.message)

        # Persist image to database
        create_image_response = await self.create_image(CreateImageRequest(
                filename=f"image_{request.provider}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{genimage_response.mimetype}",
                image_type=ImageType.GENERAL,
                source_type=ImageSourceType.AI_GENERATE,
                file_data=genimage_response.image_data,
                description=f"Generated image for prompt: {request.prompt}. Provider: {request.provider}",
            ))

        if not create_image_response.success:
            return ImageGenerateResponse(success=False, image_id="", message=create_image_response.message)

        return ImageGenerateResponse(
            success=True,
            image_id=create_image_response.image_id,
            text_data=genimage_response.text_data,
            message=""
            )