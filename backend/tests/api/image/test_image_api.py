import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock
from datetime import datetime
from app.api.image_api import router
from app.classes.image import (
    ImageListRequest, ImageListResponse, ImageInfo, ImageType, ImageSourceType,
    ImageProcessingStatus, ImageMetadata, ImageFormat, ImageResponse,
    DeleteImageResponse, ImageUrlResponse, ImageUrlsResponse, ImageUrlInfo,
    ImageGenerateResponse, ImageGenerateRequest
)
from app.services.image.image_gen.image_gen_providers import ImageGenProvider
from app.services.image.image_constants import ImageGenModel

app = FastAPI()
app.include_router(router, prefix="/images")

# Test constants
TEST_IMAGE_ID_1 = "test-image-id-1"
TEST_IMAGE_ID_2 = "test-image-id-2"
TEST_ENTITY_ID = "test-entity-id"

# Reusable test data
_TEST_IMAGE_1 = ImageInfo(
    id=TEST_IMAGE_ID_1,
    filename="test1.jpg",
    original_filename="original1.jpg",
    title="Test Image 1",
    description="First test image",
    storage_path="/images/test1.jpg",
    storage_url="https://storage.example.com/test1.jpg",
    image_type=ImageType.PLANT_PHOTO,
    source_type=ImageSourceType.UPLOAD,
    metadata=ImageMetadata(width=1920, height=1080, format=ImageFormat.JPEG),
    processing_status=ImageProcessingStatus.COMPLETED,
    uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
    updated_at=datetime(2024, 1, 1, 12, 0, 0),
    tags=["nature", "plant"],
    is_deleted=False
)

_TEST_IMAGE_2 = ImageInfo(
    id=TEST_IMAGE_ID_2,
    filename="test2.png",
    original_filename="original2.png",
    title="Test Image 2",
    description="Second test image",
    storage_path="/images/test2.png",
    storage_url="https://storage.example.com/test2.png",
    image_type=ImageType.AGENT_AVATAR,
    source_type=ImageSourceType.AI_GENERATE,
    metadata=ImageMetadata(width=512, height=512, format=ImageFormat.PNG),
    processing_status=ImageProcessingStatus.COMPLETED,
    uploaded_at=datetime(2024, 1, 2, 12, 0, 0),
    updated_at=datetime(2024, 1, 2, 12, 0, 0),
    tags=["avatar"],
    is_deleted=False
)

class TestImageApiListImages:
    
    @pytest.mark.asyncio
    async def test_list_images_api_success(self):
        """Test listing images with default parameters"""
        mock_images = [_TEST_IMAGE_1, _TEST_IMAGE_2]
        
        mock_response = ImageListResponse(
            images=mock_images,
            total=2,
            page=1,
            page_size=50
        )
        
        mock_service = AsyncMock(return_value=mock_response)
        with patch("app.services.image.image_service.ImageService.list_images", new=mock_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {
                    "page": 1,
                    "page_size": 50,
                    "include_deleted": False
                }
                response = await ac.post("/images/list", json=request_data)
                
                # Verify the service was called with the correct parameters
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert isinstance(call_args, ImageListRequest)
                assert call_args.page == 1
                assert call_args.page_size == 50
                assert call_args.include_deleted is False
                
                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert "images" in data
                assert len(data["images"]) == 2
                assert data["total"] == 2
                assert data["page"] == 1
                assert data["page_size"] == 50
                
                # Verify first image
                assert data["images"][0]["id"] == TEST_IMAGE_ID_1
                assert data["images"][0]["filename"] == "test1.jpg"
                assert data["images"][0]["title"] == "Test Image 1"
                assert data["images"][0]["image_type"] == ImageType.PLANT_PHOTO
                assert data["images"][0]["source_type"] == ImageSourceType.UPLOAD
                assert data["images"][0]["processing_status"] == ImageProcessingStatus.COMPLETED
                assert data["images"][0]["tags"] == ["nature", "plant"]
                
                # Verify second image
                assert data["images"][1]["id"] == TEST_IMAGE_ID_2
                assert data["images"][1]["filename"] == "test2.png"
                assert data["images"][1]["title"] == "Test Image 2"
                assert data["images"][1]["image_type"] == ImageType.AGENT_AVATAR
                assert data["images"][1]["source_type"] == ImageSourceType.AI_GENERATE


    @pytest.mark.asyncio
    async def test_list_images_api_with_filters(self):
        """Test listing images with type and entity filters"""
        # Create a test image with entity fields for this specific test
        plant_image = ImageInfo(
            id=TEST_IMAGE_ID_1,
            filename="plant.jpg",
            storage_path="/images/plant.jpg",
            storage_url="https://storage.example.com/plant.jpg",
            image_type=ImageType.PLANT_PHOTO,
            source_type=ImageSourceType.UPLOAD,
            entity_id=TEST_ENTITY_ID,
            entity_type="plant",
            metadata=ImageMetadata(),
            processing_status=ImageProcessingStatus.COMPLETED,
            uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
            is_deleted=False
        )
        
        mock_response = ImageListResponse(
            images=[plant_image],
            total=1,
            page=1,
            page_size=50
        )
        
        mock_service = AsyncMock(return_value=mock_response)
        with patch("app.services.image.image_service.ImageService.list_images", new=mock_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {
                    "page": 1,
                    "page_size": 50,
                    "image_type": ImageType.PLANT_PHOTO,
                    "entity_id": TEST_ENTITY_ID,
                    "entity_type": "plant",
                    "include_deleted": False
                }
                response = await ac.post("/images/list", json=request_data)
                
                # Verify the service was called with the correct filters
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]  # Get the first positional argument (ImageListRequest)
                assert isinstance(call_args, ImageListRequest)
                assert call_args.page == 1
                assert call_args.page_size == 50
                assert call_args.image_type == ImageType.PLANT_PHOTO
                assert call_args.entity_id == TEST_ENTITY_ID
                assert call_args.entity_type == "plant"
                assert call_args.include_deleted is False
                
                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert len(data["images"]) == 1
                assert data["images"][0]["id"] == TEST_IMAGE_ID_1
                assert data["images"][0]["image_type"] == ImageType.PLANT_PHOTO
                assert data["images"][0]["entity_id"] == TEST_ENTITY_ID
                assert data["images"][0]["entity_type"] == "plant"


    @pytest.mark.asyncio
    async def test_list_images_api_with_pagination(self):
        """Test listing images with pagination"""
        mock_images = [
            ImageInfo(
                id=f"test-image-{i}",
                filename=f"test{i}.jpg",
                storage_path=f"/images/test{i}.jpg",
                image_type=ImageType.GENERAL,
                source_type=ImageSourceType.UPLOAD,
                metadata=ImageMetadata(),
                processing_status=ImageProcessingStatus.COMPLETED,
                uploaded_at=datetime(2024, 1, i, 12, 0, 0),
                updated_at=datetime(2024, 1, i, 12, 0, 0),
                is_deleted=False
            )
            for i in range(1, 11)
        ]
        
        mock_response = ImageListResponse(
            images=mock_images,
            total=25,
            page=2,
            page_size=10
        )
        
        mock_service = AsyncMock(return_value=mock_response)
        with patch("app.services.image.image_service.ImageService.list_images", new=mock_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {
                    "page": 2,
                    "page_size": 10,
                    "include_deleted": False
                }
                response = await ac.post("/images/list", json=request_data)
                
                # Verify the service was called with the correct pagination parameters
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert isinstance(call_args, ImageListRequest)
                assert call_args.page == 2
                assert call_args.page_size == 10
                assert call_args.include_deleted is False
                
                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert len(data["images"]) == 10
                assert data["total"] == 25
                assert data["page"] == 2
                assert data["page_size"] == 10


    @pytest.mark.asyncio
    async def test_list_images_api_empty_result(self):
        """Test listing images when no images exist"""
        mock_response = ImageListResponse(
            images=[],
            total=0,
            page=1,
            page_size=50
        )
        
        with patch("app.services.image.image_service.ImageService.list_images", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {
                    "page": 1,
                    "page_size": 50,
                    "include_deleted": False
                }
                response = await ac.post("/images/list", json=request_data)
                assert response.status_code == 200
                data = response.json()
                assert data["images"] == []
                assert data["total"] == 0


    @pytest.mark.asyncio
    async def test_list_images_api_include_deleted(self):
        """Test listing images including deleted ones"""
        mock_images = [
            ImageInfo(
                id=TEST_IMAGE_ID_1,
                filename="deleted.jpg",
                storage_path="/images/deleted.jpg",
                image_type=ImageType.GENERAL,
                source_type=ImageSourceType.UPLOAD,
                metadata=ImageMetadata(),
                processing_status=ImageProcessingStatus.COMPLETED,
                uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
                updated_at=datetime(2024, 1, 1, 12, 0, 0),
                is_deleted=True
            )
        ]
        
        mock_response = ImageListResponse(
            images=mock_images,
            total=1,
            page=1,
            page_size=50
        )
        
        mock_service = AsyncMock(return_value=mock_response)
        with patch("app.services.image.image_service.ImageService.list_images", new=mock_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {
                    "page": 1,
                    "page_size": 50,
                    "include_deleted": True
                }
                response = await ac.post("/images/list", json=request_data)
                
                # Verify the service was called with include_deleted=True
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert isinstance(call_args, ImageListRequest)
                assert call_args.include_deleted is True
                
                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert len(data["images"]) == 1
                assert data["images"][0]["is_deleted"] is True


    @pytest.mark.asyncio
    async def test_list_images_api_error(self):
        """Test listing images when an error occurs"""
        with patch("app.services.image.image_service.ImageService.list_images", new=AsyncMock(side_effect=Exception("Database error"))):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {
                    "page": 1,
                    "page_size": 50,
                    "include_deleted": False
                }
                response = await ac.post("/images/list", json=request_data)
                assert response.status_code == 400
                data = response.json()
                assert "detail" in data
                assert "Database error" in data["detail"]


class TestImageApiDeleteImage:

    @pytest.mark.asyncio
    async def test_delete_image_api_success(self):
        """Test deleting an image permanently"""
        mock_response = DeleteImageResponse(
            success=True,
            deleted_image_id=TEST_IMAGE_ID_1,
            message="Image deleted successfully"
        )
        
        mock_service = AsyncMock(return_value=mock_response)
        with patch("app.services.image.image_service.ImageService.delete_image", new=mock_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.delete(f"/images/{TEST_IMAGE_ID_1}")
                
                # Verify the service was called with correct parameters
                mock_service.assert_called_once_with(TEST_IMAGE_ID_1, soft_delete=False)
                
                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["deleted_image_id"] == TEST_IMAGE_ID_1
                assert data["message"] == "Image deleted successfully"


    @pytest.mark.asyncio
    async def test_delete_image_api_failure(self):
        """Test deleting an image that doesn't exist"""
        mock_response = DeleteImageResponse(
            success=False,
            deleted_image_id="",
            message="Image not found"
        )
        
        with patch("app.services.image.image_service.ImageService.delete_image", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.delete("/images/nonexistent-id")
                assert response.status_code == 400
                data = response.json()
                assert "detail" in data
                assert "Image not found" in data["detail"]


class TestImageApiBinImage:

    @pytest.mark.asyncio
    async def test_bin_image_api_success(self):
        """Test soft-deleting (binning) an image"""
        mock_response = DeleteImageResponse(
            success=True,
            deleted_image_id=TEST_IMAGE_ID_1,
            message="Image moved to bin successfully"
        )
        
        mock_service = AsyncMock(return_value=mock_response)
        with patch("app.services.image.image_service.ImageService.delete_image", new=mock_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(f"/images/bin/{TEST_IMAGE_ID_1}")
                
                # Verify the service was called with correct parameters
                mock_service.assert_called_once_with(TEST_IMAGE_ID_1, soft_delete=True)
                
                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["deleted_image_id"] == TEST_IMAGE_ID_1
                assert "bin" in data["message"].lower()


    @pytest.mark.asyncio
    async def test_bin_image_api_failure(self):
        """Test soft-deleting an image that doesn't exist"""
        mock_response = DeleteImageResponse(
            success=False,
            deleted_image_id="",
            message="Image not found"
        )
        
        with patch("app.services.image.image_service.ImageService.delete_image", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/images/bin/nonexistent-id")
                assert response.status_code == 400
                data = response.json()
                assert "detail" in data


class TestImageApiGenerateImage:

    @pytest.mark.asyncio
    async def test_generate_image_api_success(self):
        """Test generating an image with default provider"""
        mock_response = ImageGenerateResponse(
            success=True,
            image_id=TEST_IMAGE_ID_2,
            text_data=None,
            message=""
        )
        
        mock_service = AsyncMock(return_value=mock_response)
        with patch("app.services.image.image_service.ImageService.generate_image", new=mock_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/images/generate?prompt=A beautiful sunset&model=gemini-2.5-flash-image")
                
                # Verify the service was called with correct parameters
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert isinstance(call_args, ImageGenerateRequest)
                assert call_args.prompt == "A beautiful sunset"
                assert call_args.model == ImageGenModel.GEMINI_2_5_FLASH_IMAGE  # Default provider
                
                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["image_id"] == TEST_IMAGE_ID_2
                assert data["message"] == ""


    @pytest.mark.asyncio
    async def test_generate_image_api_with_provider(self):
        """Test generating an image with specific provider"""
        mock_response = ImageGenerateResponse(
            success=True,
            image_id=TEST_IMAGE_ID_1,
            text_data=None,
            message="Image generated successfully"
        )
        
        mock_service = AsyncMock(return_value=mock_response)
        with patch("app.services.image.image_service.ImageService.generate_image", new=mock_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/images/generate?prompt=A beautiful sunset&model=gemini-2.5-flash-image")
                
                # Verify the service was called with correct parameters
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert isinstance(call_args, ImageGenerateRequest)
                assert call_args.prompt == "A beautiful sunset"
                assert call_args.model == ImageGenModel.GEMINI_2_5_FLASH_IMAGE
                
                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["image_id"] == TEST_IMAGE_ID_1


    @pytest.mark.asyncio
    async def test_generate_image_api_failure(self):
        """Test generating an image when generation fails"""
        mock_response = ImageGenerateResponse(
            success=False,
            image_id=None,
            text_data=None,
            message="Failed to generate image"
        )
        
        with patch("app.services.image.image_service.ImageService.generate_image", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/images/generate?prompt=Invalid prompt&model=gemini-2.5-flash-image")
                assert response.status_code == 400
                data = response.json()
                assert "detail" in data
                assert "Failed to generate image" in data["detail"]

