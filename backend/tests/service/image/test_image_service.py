import pytest
import io
import base64
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from PIL import Image as PILImage

from app.services.image.image_service import ImageService
from app.classes.image import (
    ImageInfo,
    CreateImageRequest,
    UpdateImageRequest,
    ImageUploadResponse,
    ImageResponse,
    ImageListResponse,
    ImageUrlResponse,
    DeleteImageResponse,
    ImageMetadata,
    ImageFormat,
    ImageProcessingStatus,
    ImageType,
    ImageSourceType,
)


@pytest.fixture
def image_service():
    """Create a fresh instance for each test"""
    # Reset the singleton instance
    ImageService._instance = None
    return ImageService()


@pytest.fixture
def sample_image_bytes():
    """Create sample image bytes for testing"""
    # Create a simple 100x100 RGB image
    img = PILImage.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


@pytest.fixture
def sample_base64_image(sample_image_bytes):
    """Create base64 encoded image for testing"""
    return base64.b64encode(sample_image_bytes).decode('utf-8')


@pytest.fixture
def create_image_request_file_data(sample_image_bytes):
    """Create image request with file data"""
    return CreateImageRequest(
        filename="test_image.png",
        original_filename="original_test.png",
        title="Test Image",
        description="A test image",
        alt_text="Test alt text",
        image_type=ImageType.PLANT_PHOTO,
        source_type=ImageSourceType.UPLOAD,
        entity_id="plant_123",
        entity_type="plant",
        file_data=sample_image_bytes,
        tags=["test", "plant"]
    )


@pytest.fixture
def create_image_request_base64(sample_base64_image):
    """Create image request with base64 data"""
    return CreateImageRequest(
        filename="test_image.png",
        image_type=ImageType.AGENT_AVATAR,
        source_type=ImageSourceType.BASE64,
        entity_id="agent_456",
        base64_data=sample_base64_image
    )


@pytest.fixture
def create_image_request_url():
    """Create image request with URL"""
    return CreateImageRequest(
        filename="test_image.jpg",
        image_type=ImageType.GENERAL,
        source_type=ImageSourceType.URL,
        source_url="https://example.com/image.jpg"
    )


@pytest.fixture
def update_image_request():
    """Create update image request"""
    return UpdateImageRequest(
        title="Updated Title",
        description="Updated Description",
        alt_text="Updated alt text",
        tags=["updated", "test"],
        notes="Updated notes"
    )


@pytest.fixture
def mock_image_document():
    """Mock image document from database"""
    return {
        "_id": "image_123",
        "filename": "test_image.png",
        "original_filename": "original_test.png",
        "title": "Test Image",
        "description": "A test image",
        "alt_text": "Test alt text",
        "notes": "Test notes",
        "storage_path": "plants/plant_123/photos/20240101_120000_test_image.png",
        "storage_url": "https://storage.googleapis.com/bucket/path",
        "image_type": "plant_photo",
        "source_type": "upload",
        "entity_id": "plant_123",
        "entity_type": "plant",
        "metadata": {
            "width": 100,
            "height": 100,
            "file_size": 1024,
            "format": "png",
            "color_mode": "RGB"
        },
        "processing_status": "completed",
        "uploaded_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "processed_at": datetime.now(timezone.utc),
        "tags": ["test", "plant"],
        "is_deleted": False,
        "ai_processed": False,
        "ai_tags": [],
        "content_moderation": None
    }


class TestImageServiceSingleton:
    
    def test_singleton_instance(self):
        """Test that ImageService is a singleton"""
        service1 = ImageService()
        service2 = ImageService()
        assert service1 is service2

class TestImageServiceValidation:

    def test_validate_create_image_request_valid_file_data(self, image_service, create_image_request_file_data):
        """Test validation with valid file data request"""
        valid, error_msg = image_service._validate_create_image_request(create_image_request_file_data)
        assert valid is True
        assert error_msg == ""

    def test_validate_create_image_request_valid_base64(self, image_service, create_image_request_base64):
        """Test validation with valid base64 request"""
        valid, error_msg = image_service._validate_create_image_request(create_image_request_base64)
        assert valid is True
        assert error_msg == ""

    def test_validate_create_image_request_valid_url(self, image_service, create_image_request_url):
        """Test validation with valid URL request"""
        valid, error_msg = image_service._validate_create_image_request(create_image_request_url)
        assert valid is True
        assert error_msg == ""

    def test_validate_create_image_request_missing_filename(self, image_service, sample_image_bytes):
        """Test validation with missing filename"""
        request = CreateImageRequest(
            filename="",
            image_type=ImageType.PLANT_PHOTO,
            file_data=sample_image_bytes
        )
        valid, error_msg = image_service._validate_create_image_request(request)
        assert valid is False
        assert "Missing value for field: filename" in error_msg

    def test_validate_create_image_request_missing_image_type(self, image_service, sample_image_bytes):
        """Test validation with missing image type"""
        # Create a mock request with empty image_type
        request = MagicMock()
        request.filename = "test.png"
        request.image_type = ""
        request.file_data = sample_image_bytes
        request.base64_data = None
        request.source_url = None
        
        valid, error_msg = image_service._validate_create_image_request(request)
        assert valid is False
        assert "Missing value for field: image_type" in error_msg

    def test_validate_create_image_request_no_data_source(self, image_service):
        """Test validation with no data source provided"""
        request = CreateImageRequest(
            filename="test.png",
            image_type=ImageType.PLANT_PHOTO
        )
        valid, error_msg = image_service._validate_create_image_request(request)
        assert valid is False
        assert "Must provide one of: file_data, base64_data, source_url" in error_msg

    def test_validate_create_image_request_multiple_data_sources(self, image_service, sample_image_bytes, sample_base64_image):
        """Test validation with multiple data sources provided"""
        request = CreateImageRequest(
            filename="test.png",
            image_type=ImageType.PLANT_PHOTO,
            file_data=sample_image_bytes,
            base64_data=sample_base64_image
        )
        valid, error_msg = image_service._validate_create_image_request(request)
        assert valid is False
        assert "Provide only one of: file_data, base64_data, source_url" in error_msg

class TestImageServiceMetadata:
    
    @pytest.mark.asyncio
    async def test_extract_image_metadata_success(self, image_service, sample_image_bytes):
        """Test successful image metadata extraction"""
        metadata = await image_service._extract_image_metadata(sample_image_bytes)
        
        assert isinstance(metadata, ImageMetadata)
        assert metadata.width == 100
        assert metadata.height == 100
        assert metadata.file_size == len(sample_image_bytes)
        assert metadata.format == ImageFormat.PNG
        assert metadata.color_mode == "RGB"

    @pytest.mark.asyncio
    async def test_extract_image_metadata_invalid_data(self, image_service):
        """Test image metadata extraction with invalid data"""
        invalid_data = b"not an image"
        metadata = await image_service._extract_image_metadata(invalid_data)
        
        assert isinstance(metadata, ImageMetadata)
        assert metadata.file_size == len(invalid_data)
        assert metadata.width is None
        assert metadata.height is None

class TestImageServiceDataRetrieval:
    
    @pytest.mark.asyncio
    async def test_get_image_data_from_request_file_data(self, image_service, create_image_request_file_data):
        """Test getting image data from file data"""
        data = await image_service._get_image_data_from_request(create_image_request_file_data)
        assert data == create_image_request_file_data.file_data

    @pytest.mark.asyncio
    async def test_get_image_data_from_request_base64(self, image_service, create_image_request_base64, sample_image_bytes):
        """Test getting image data from base64"""
        data = await image_service._get_image_data_from_request(create_image_request_base64)
        assert data == sample_image_bytes

    @pytest.mark.asyncio
    async def test_get_image_data_from_request_url(self, image_service, create_image_request_url, sample_image_bytes):
        """Test getting image data from URL"""
        mock_response = MagicMock()
        mock_response.content = sample_image_bytes
        mock_response.raise_for_status = MagicMock()
        
        with patch("app.services.image.image_service.requests.get", return_value=mock_response):
            data = await image_service._get_image_data_from_request(create_image_request_url)
            assert data == sample_image_bytes

    @pytest.mark.asyncio
    async def test_get_image_data_from_request_url_failure(self, image_service, create_image_request_url):
        """Test getting image data from URL with failure"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        
        with patch("app.services.image.image_service.requests.get", return_value=mock_response):
            with pytest.raises(Exception, match="HTTP Error"):
                await image_service._get_image_data_from_request(create_image_request_url)

    @pytest.mark.asyncio
    async def test_get_image_data_from_request_no_source(self, image_service):
        """Test getting image data with no source"""
        request = CreateImageRequest(
            filename="test.png",
            image_type=ImageType.PLANT_PHOTO
        )
        
        with pytest.raises(ValueError, match="No image data source provided"):
            await image_service._get_image_data_from_request(request)

class TestImageServiceCreateImage:

    @pytest.mark.asyncio
    async def test_create_image_success(self, image_service, create_image_request_file_data):
        """Test successful image creation"""
        mock_storage = MagicMock()
        mock_storage.upload = AsyncMock(return_value="https://storage.url")
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url")
        
        with patch("app.services.image.image_service.generate_storage_path", return_value="test/path"), \
             patch("app.services.image.image_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.image.image_service.insert_document", return_value="image_123"):
            
            response = await image_service.create_image(create_image_request_file_data)
            
            assert isinstance(response, ImageUploadResponse)
            assert response.success is True
            assert response.image_id == "image_123"
            assert response.storage_path == "test/path"
            assert response.storage_url == "https://storage.url"
            assert response.presigned_url == "https://presigned.url"
            assert response.message == "Image uploaded successfully"

    @pytest.mark.asyncio
    async def test_create_image_validation_failure(self, image_service):
        """Test image creation with validation failure"""
        invalid_request = CreateImageRequest(
            filename="",
            image_type=ImageType.PLANT_PHOTO
        )
        
        response = await image_service.create_image(invalid_request)
        
        assert isinstance(response, ImageUploadResponse)
        assert response.success is False
        assert response.image_id == ""
        assert response.storage_path == ""
        assert "Missing value for field: filename" in response.message

    @pytest.mark.asyncio
    async def test_create_image_exception(self, image_service, create_image_request_file_data):
        """Test image creation with exception"""
        with patch("app.services.image.image_service.generate_storage_path", side_effect=Exception("Storage error")):
            response = await image_service.create_image(create_image_request_file_data)
            
            assert isinstance(response, ImageUploadResponse)
            assert response.success is False
            assert response.image_id == ""
            assert response.storage_path == ""
            assert "Failed to create image: Storage error" in response.message

class TestImageServiceGetImage:
    
    @pytest.mark.asyncio
    async def test_get_image_success(self, image_service, mock_image_document):
        """Test successful image retrieval"""
        with patch("app.services.image.image_service.get_document", return_value=mock_image_document):
            response = await image_service.get_image("image_123")
            
            assert isinstance(response, ImageResponse)
            assert response.success is True
            assert response.image is not None
            assert response.image.id == "image_123"
            assert response.image.filename == "test_image.png"
            assert response.image.title == "Test Image"
            assert response.message == "Image retrieved successfully"

    @pytest.mark.asyncio
    async def test_get_image_not_found(self, image_service):
        """Test image retrieval when not found"""
        with patch("app.services.image.image_service.get_document", side_effect=ValueError("Document not found")):
            response = await image_service.get_image("nonexistent")
            
            assert isinstance(response, ImageResponse)
            assert response.success is False
            assert response.image is None
            assert "Document not found" in response.message

    @pytest.mark.asyncio
    async def test_get_image_exception(self, image_service):
        """Test image retrieval with exception"""
        with patch("app.services.image.image_service.get_document", side_effect=Exception("Database error")):
            response = await image_service.get_image("image_123")
            
            assert isinstance(response, ImageResponse)
            assert response.success is False
            assert response.image is None
            assert "Failed to get image: Database error" in response.message

class TestImageServiceUpdateImage:
    
    @pytest.mark.asyncio
    async def test_update_image_success(self, image_service, update_image_request, mock_image_document):
        """Test successful image update"""
        with patch("app.services.image.image_service.update_document"), \
             patch("app.services.image.image_service.get_document", return_value=mock_image_document):
            
            response = await image_service.update_image("image_123", update_image_request)
            
            assert isinstance(response, ImageResponse)
            assert response.success is True
            assert response.image is not None

    @pytest.mark.asyncio
    async def test_update_image_partial_update(self, image_service, mock_image_document):
        """Test partial image update"""
        partial_request = UpdateImageRequest(title="New Title Only")
        
        with patch("app.services.image.image_service.update_document") as mock_update, \
             patch("app.services.image.image_service.get_document", return_value=mock_image_document):
            
            await image_service.update_image("image_123", partial_request)
            
            # Verify only title was updated
            mock_update.assert_called_once()
            update_doc = mock_update.call_args[0][2]
            assert "title" in update_doc
            assert update_doc["title"] == "New Title Only"
            assert "description" not in update_doc
            assert "updated_at" in update_doc

    @pytest.mark.asyncio
    async def test_update_image_exception(self, image_service, update_image_request):
        """Test image update with exception"""
        with patch("app.services.image.image_service.update_document", side_effect=Exception("Update error")):
            response = await image_service.update_image("image_123", update_image_request)
            
            assert isinstance(response, ImageResponse)
            assert response.success is False
            assert response.image is None
            assert "Failed to update image: Update error" in response.message

class TestImageServiceListImages:
    
    @pytest.mark.asyncio
    async def test_list_images_success(self, image_service, mock_image_document):
        """Test successful image listing"""
        mock_documents = [mock_image_document, mock_image_document.copy()]
        
        with patch("app.services.image.image_service.count_documents_with_filters", return_value=2), \
             patch("app.services.image.image_service.find_documents_with_filters", return_value=mock_documents):
            
            response = await image_service.list_images(page=1, page_size=10)
            
            assert isinstance(response, ImageListResponse)
            assert len(response.images) == 2
            assert response.total == 2
            assert response.page == 1
            assert response.page_size == 10

    @pytest.mark.asyncio
    async def test_list_images_with_filters(self, image_service, mock_image_document):
        """Test image listing with filters"""
        with patch("app.services.image.image_service.count_documents_with_filters", return_value=1) as mock_count, \
             patch("app.services.image.image_service.find_documents_with_filters", return_value=[mock_image_document]) as mock_find:
            
            await image_service.list_images(
                image_type=ImageType.PLANT_PHOTO,
                entity_id="plant_123",
                entity_type="plant",
                include_deleted=True
            )
            
            # Verify filters were applied
            filters = mock_count.call_args[0][1]
            assert filters["image_type"] == "plant_photo"
            assert filters["entity_id"] == "plant_123"
            assert filters["entity_type"] == "plant"
            assert "is_deleted" not in filters  # Should not be present when include_deleted=True

    @pytest.mark.asyncio
    async def test_list_images_exclude_deleted(self, image_service):
        """Test image listing excludes deleted by default"""
        with patch("app.services.image.image_service.count_documents_with_filters") as mock_count, \
             patch("app.services.image.image_service.find_documents_with_filters", return_value=[]):
            
            await image_service.list_images()
            
            # Verify is_deleted filter is applied
            filters = mock_count.call_args[0][1]
            assert filters["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_list_images_exception(self, image_service):
        """Test image listing with exception"""
        with patch("app.services.image.image_service.count_documents_with_filters", side_effect=Exception("Database error")):
            response = await image_service.list_images()
            
            assert isinstance(response, ImageListResponse)
            assert response.images == []
            assert response.total == 0

class TestImageServicePresignedUrl:
    
    @pytest.mark.asyncio
    async def test_get_image_presigned_url_success(self, image_service, mock_image_document):
        """Test successful presigned URL generation"""
        mock_storage = MagicMock()
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url")
        
        with patch("app.services.image.image_service.get_document", return_value=mock_image_document), \
             patch("app.services.image.image_service.FirebaseStorageRepository", return_value=mock_storage):
            
            response = await image_service.get_image_presigned_url("image_123")
            
            assert isinstance(response, ImageUrlResponse)
            assert response.success is True
            assert response.url == "https://presigned.url"
            assert response.expires_at is not None
            assert response.message == "Presigned URL generated successfully"

    @pytest.mark.asyncio
    async def test_get_image_presigned_url_image_not_found(self, image_service):
        """Test presigned URL generation when image not found"""
        with patch("app.services.image.image_service.get_document", side_effect=ValueError("Not found")):
            response = await image_service.get_image_presigned_url("nonexistent")
            
            assert isinstance(response, ImageUrlResponse)
            assert response.success is False
            assert response.url == ""
            assert response.message == "Image not found"

    @pytest.mark.asyncio
    async def test_get_image_presigned_url_exception(self, image_service, mock_image_document):
        """Test presigned URL generation with exception"""
        mock_storage = MagicMock()
        mock_storage.get_presigned_url = AsyncMock(side_effect=Exception("Storage error"))
        
        with patch("app.services.image.image_service.get_document", return_value=mock_image_document), \
             patch("app.services.image.image_service.FirebaseStorageRepository", return_value=mock_storage):
            
            response = await image_service.get_image_presigned_url("image_123")
            
            assert isinstance(response, ImageUrlResponse)
            assert response.success is False
            assert response.url == ""
            assert "Failed to get image URL: Storage error" in response.message

class TestImageServiceDeleteImage:
    
    @pytest.mark.asyncio
    async def test_delete_image_soft_delete_success(self, image_service):
        """Test successful soft delete"""
        with patch("app.services.image.image_service.update_document") as mock_update:
            response = await image_service.delete_image("image_123", soft_delete=True)
            
            assert isinstance(response, DeleteImageResponse)
            assert response.success is True
            assert response.deleted_image_id == "image_123"
            assert response.message == "Image deleted successfully"
            
            # Verify soft delete update
            mock_update.assert_called_once()
            update_doc = mock_update.call_args[0][2]
            assert update_doc["is_deleted"] is True
            assert "updated_at" in update_doc

    @pytest.mark.asyncio
    async def test_delete_image_hard_delete_success(self, image_service, mock_image_document):
        """Test successful hard delete"""
        mock_storage = MagicMock()
        mock_storage.delete = AsyncMock()
        
        with patch("app.services.image.image_service.get_document", return_value=mock_image_document), \
             patch("app.services.image.image_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.image.image_service.delete_document") as mock_delete:
            
            response = await image_service.delete_image("image_123", soft_delete=False)
            
            assert isinstance(response, DeleteImageResponse)
            assert response.success is True
            assert response.deleted_image_id == "image_123"
            assert response.message == "Image deleted successfully"
            
            # Verify storage and database deletion
            mock_storage.delete.assert_called_once_with(mock_image_document["storage_path"])
            mock_delete.assert_called_once_with("images", "image_123")

    @pytest.mark.asyncio
    async def test_delete_image_hard_delete_storage_failure(self, image_service, mock_image_document):
        """Test hard delete with storage deletion failure"""
        mock_storage = MagicMock()
        mock_storage.delete = AsyncMock(side_effect=Exception("Storage error"))
        
        with patch("app.services.image.image_service.get_document", return_value=mock_image_document), \
             patch("app.services.image.image_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.image.image_service.delete_document"):
            
            response = await image_service.delete_image("image_123", soft_delete=False)
            
            # Should still succeed even if storage deletion fails
            assert isinstance(response, DeleteImageResponse)
            assert response.success is False
            assert response.deleted_image_id == "image_123"
            assert "Failed to delete image from storage: Storage error" in response.message

    @pytest.mark.asyncio
    async def test_delete_image_hard_delete_no_storage_path(self, image_service):
        """Test hard delete with no storage path"""
        mock_document = {"_id": "image_123", "storage_path": ""}
        
        with patch("app.services.image.image_service.get_document", return_value=mock_document), \
             patch("app.services.image.image_service.delete_document"):
            
            response = await image_service.delete_image("image_123", soft_delete=False)
            
            assert isinstance(response, DeleteImageResponse)
            assert response.success is True
            assert response.deleted_image_id == "image_123"

    @pytest.mark.asyncio
    async def test_delete_image_exception(self, image_service):
        """Test image deletion with exception"""
        with patch("app.services.image.image_service.update_document", side_effect=Exception("Delete error")):
            response = await image_service.delete_image("image_123")
            
            assert isinstance(response, DeleteImageResponse)
            assert response.success is False
            assert response.deleted_image_id == "image_123"
            assert "Failed to delete image: Delete error" in response.message
