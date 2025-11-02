from datetime import datetime, timezone
from bson import ObjectId
import pytest
import base64
from unittest.mock import patch, MagicMock, AsyncMock
import cv2

from app.services.video.video_service import VideoService
from app.classes.video import (
    CreateVideoRequest,
    CreateVideoResponse,
    GetVideoResponse,
    VideoType,
    VideoSourceType,
    VideoFormat,
    VideoMetadata,
)
from app.classes.media import MediaProcessingStatus

TEST_VIDEO_ID = "67206999f3949388f3a80900"

@pytest.fixture
def video_service():
    """Create a fresh instance for each test"""
    # Reset the singleton instance
    VideoService._instance = None
    return VideoService()


@pytest.fixture
def sample_video_bytes():
    """Create sample video bytes for testing"""
    # Simple fake video data
    return b"fake_video_data_content_for_testing"


@pytest.fixture
def sample_base64_video(sample_video_bytes):
    """Create base64 encoded video for testing"""
    return base64.b64encode(sample_video_bytes).decode('utf-8')


@pytest.fixture
def create_video_request_file_data(sample_video_bytes):
    """Create video request with file data"""
    return CreateVideoRequest(
        filename="test_video.mp4",
        original_filename="original_test.mp4",
        title="Test Video",
        description="A test video",
        alt_text="Test alt text",
        video_type=VideoType.GENERAL,
        source_type=VideoSourceType.UPLOAD,
        entity_id="entity_123",
        entity_type="test_entity",
        file_data=sample_video_bytes,
        tags=["test", "video"]
    )


@pytest.fixture
def create_video_request_base64(sample_base64_video):
    """Create video request with base64 data"""
    return CreateVideoRequest(
        filename="test_video.mp4",
        video_type=VideoType.GENERAL,
        source_type=VideoSourceType.BASE64,
        entity_id="entity_456",
        base64_data=sample_base64_video
    )


@pytest.fixture
def create_video_request_url():
    """Create video request with URL"""
    return CreateVideoRequest(
        filename="test_video.mp4",
        video_type=VideoType.GENERAL,
        source_type=VideoSourceType.URL,
        source_url="https://example.com/video.mp4"
    )


@pytest.fixture
def mock_video_document():
    """Mock video document from database"""
    return {
        "_id": ObjectId(TEST_VIDEO_ID),
        "filename": "test_video.mp4",
        "original_filename": "original_test.mp4",
        "title": "Test Video",
        "description": "A test video",
        "alt_text": "Test alt text",
        "storage_path": "test/path",
        "storage_url": "https://storage.url",
        "video_type": VideoType.GENERAL.value,
        "source_type": VideoSourceType.UPLOAD.value,
        "entity_id": "entity_123",
        "entity_type": "test_entity",
        "metadata": {
            "width": 1920,
            "height": 1080,
            "file_size": 1024,
            "format": VideoFormat.MP4.value,
            "duration": 30.0,
            "fps": 30.0,
            "bitrate": 1000000,
        },
        "processing_status": MediaProcessingStatus.COMPLETED.value,
        "uploaded_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "processed_at": datetime.now(timezone.utc),
        "tags": ["test", "video"],
        "is_deleted": False,
        "ai_processed": False,
        "ai_tags": [],
    }


class TestVideoServiceSingleton:
    
    def test_singleton_instance(self):
        """Test that VideoService is a singleton"""
        service1 = VideoService()
        service2 = VideoService()
        assert service1 is service2


class TestVideoServiceValidation:

    def test_validate_create_video_request_valid_file_data(self, video_service: VideoService, create_video_request_file_data: CreateVideoRequest):
        """Test validation with valid file data request"""
        valid, error_msg = video_service._validate_create_video_request(create_video_request_file_data)
        assert valid is True
        assert error_msg == ""

    def test_validate_create_video_request_valid_base64(self, video_service: VideoService, create_video_request_base64: CreateVideoRequest):
        """Test validation with valid base64 request"""
        valid, error_msg = video_service._validate_create_video_request(create_video_request_base64)
        assert valid is True
        assert error_msg == ""

    def test_validate_create_video_request_valid_url(self, video_service: VideoService, create_video_request_url: CreateVideoRequest):
        """Test validation with valid URL request"""
        valid, error_msg = video_service._validate_create_video_request(create_video_request_url)
        assert valid is True
        assert error_msg == ""

    def test_validate_create_video_request_missing_filename(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test validation with missing filename"""
        request = CreateVideoRequest(
            filename="",
            video_type=VideoType.GENERAL,
            file_data=sample_video_bytes
        )
        valid, error_msg = video_service._validate_create_video_request(request)
        assert valid is False
        assert "Missing value for field: filename" in error_msg

    def test_validate_create_video_request_missing_video_type(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test validation with missing video type"""
        # Create a mock request with empty video_type
        request = MagicMock()
        request.filename = "test.mp4"
        request.video_type = ""
        request.file_data = sample_video_bytes
        request.base64_data = None
        request.source_url = None
        
        valid, error_msg = video_service._validate_create_video_request(request)
        assert valid is False
        assert "Missing value for field: video_type" in error_msg

    def test_validate_create_video_request_no_data_source(self, video_service: VideoService):
        """Test validation with no data source provided"""
        request = CreateVideoRequest(
            filename="test.mp4",
            video_type=VideoType.GENERAL
        )
        valid, error_msg = video_service._validate_create_video_request(request)
        assert valid is False
        assert "Must provide one of: file_data, base64_data, source_url" in error_msg

    def test_validate_create_video_request_multiple_data_sources(self, video_service: VideoService, sample_video_bytes: bytes, sample_base64_video: str):
        """Test validation with multiple data sources provided"""
        request = CreateVideoRequest(
            filename="test.mp4",
            video_type=VideoType.GENERAL,
            file_data=sample_video_bytes,
            base64_data=sample_base64_video
        )
        valid, error_msg = video_service._validate_create_video_request(request)
        assert valid is False
        assert "Provide only one of: file_data, base64_data, source_url" in error_msg


class TestVideoServiceMetadata:
    
    @pytest.mark.asyncio
    async def test_extract_video_metadata_success(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test successful video metadata extraction"""
        # Mock cv2.VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 900,
            cv2.CAP_PROP_FOURCC: 0x31637661,  # 'avc1' fourcc
        }.get(prop, 0)
        
        with patch("app.services.video.video_service.cv2.VideoCapture", return_value=mock_cap), \
             patch("app.services.video.video_service.tempfile.NamedTemporaryFile") as mock_tempfile, \
             patch("app.services.video.video_service.os.path.exists", return_value=True), \
             patch("app.services.video.video_service.os.unlink"):
            
            # Mock the temp file
            mock_file = MagicMock()
            mock_file.name = "/tmp/test_video.mp4"
            mock_file.__enter__.return_value = mock_file
            mock_tempfile.return_value = mock_file
            
            metadata = await video_service._extract_video_metadata(sample_video_bytes)
            
            assert isinstance(metadata, VideoMetadata)
            assert metadata.width == 1920
            assert metadata.height == 1080
            assert metadata.file_size == len(sample_video_bytes)
            assert metadata.fps == 30.0
            assert metadata.duration == 30.0  # 900 frames / 30 fps
            assert metadata.format == VideoFormat.MP4
            assert metadata.bitrate is not None

    @pytest.mark.asyncio
    async def test_extract_video_metadata_invalid_video(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test video metadata extraction with invalid video"""
        # Mock cv2.VideoCapture that fails to open
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        
        with patch("app.services.video.video_service.cv2.VideoCapture", return_value=mock_cap), \
             patch("app.services.video.video_service.tempfile.NamedTemporaryFile") as mock_tempfile, \
             patch("app.services.video.video_service.os.path.exists", return_value=True), \
             patch("app.services.video.video_service.os.unlink"):
            
            # Mock the temp file
            mock_file = MagicMock()
            mock_file.name = "/tmp/test_video.mp4"
            mock_file.__enter__.return_value = mock_file
            mock_tempfile.return_value = mock_file
            
            metadata = await video_service._extract_video_metadata(sample_video_bytes)
            
            assert isinstance(metadata, VideoMetadata)
            assert metadata.file_size == len(sample_video_bytes)
            assert metadata.width is None
            assert metadata.height is None

    @pytest.mark.asyncio
    async def test_extract_video_metadata_exception(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test video metadata extraction with exception"""
        with patch("app.services.video.video_service.tempfile.NamedTemporaryFile", side_effect=Exception("Temp file error")):
            metadata = await video_service._extract_video_metadata(sample_video_bytes)
            
            assert isinstance(metadata, VideoMetadata)
            assert metadata.file_size == len(sample_video_bytes)
            assert metadata.width is None
            assert metadata.height is None

    @pytest.mark.asyncio
    async def test_extract_video_metadata_zero_fps(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test video metadata extraction with zero FPS"""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            cv2.CAP_PROP_FPS: 0,
            cv2.CAP_PROP_FRAME_COUNT: 900,
            cv2.CAP_PROP_FOURCC: 0x31637661,
        }.get(prop, 0)
        
        with patch("app.services.video.video_service.cv2.VideoCapture", return_value=mock_cap), \
             patch("app.services.video.video_service.tempfile.NamedTemporaryFile") as mock_tempfile, \
             patch("app.services.video.video_service.os.path.exists", return_value=True), \
             patch("app.services.video.video_service.os.unlink"):
            
            mock_file = MagicMock()
            mock_file.name = "/tmp/test_video.mp4"
            mock_file.__enter__.return_value = mock_file
            mock_tempfile.return_value = mock_file
            
            metadata = await video_service._extract_video_metadata(sample_video_bytes)
            
            assert isinstance(metadata, VideoMetadata)
            assert metadata.duration is None
            assert metadata.bitrate is None
            assert metadata.fps is None


class TestVideoServiceDataRetrieval:
    
    @pytest.mark.asyncio
    async def test_get_video_data_from_request_file_data(self, video_service: VideoService, create_video_request_file_data: CreateVideoRequest):
        """Test getting video data from file data"""
        data = await video_service._get_video_data_from_request(create_video_request_file_data)
        assert data == create_video_request_file_data.file_data

    @pytest.mark.asyncio
    async def test_get_video_data_from_request_base64(self, video_service: VideoService, create_video_request_base64: CreateVideoRequest, sample_video_bytes: bytes):
        """Test getting video data from base64"""
        data = await video_service._get_video_data_from_request(create_video_request_base64)
        assert data == sample_video_bytes

    @pytest.mark.asyncio
    async def test_get_video_data_from_request_url(self, video_service: VideoService, create_video_request_url: CreateVideoRequest, sample_video_bytes: bytes):
        """Test getting video data from URL"""
        mock_response = MagicMock()
        mock_response.content = sample_video_bytes
        mock_response.raise_for_status = MagicMock()
        
        with patch("app.services.video.video_service.requests.get", return_value=mock_response):
            data = await video_service._get_video_data_from_request(create_video_request_url)
            assert data == sample_video_bytes

    @pytest.mark.asyncio
    async def test_get_video_data_from_request_url_failure(self, video_service: VideoService, create_video_request_url: CreateVideoRequest):
        """Test getting video data from URL with failure"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        
        with patch("app.services.video.video_service.requests.get", return_value=mock_response):
            with pytest.raises(Exception, match="HTTP Error"):
                await video_service._get_video_data_from_request(create_video_request_url)

    @pytest.mark.asyncio
    async def test_get_video_data_from_request_no_source(self, video_service: VideoService):
        """Test getting video data with no source"""
        request = CreateVideoRequest(
            filename="test.mp4",
            video_type=VideoType.GENERAL
        )
        
        with pytest.raises(ValueError, match="No video data source provided"):
            await video_service._get_video_data_from_request(request)


class TestVideoServiceCreateVideo:

    @pytest.mark.asyncio
    async def test_create_video_success(self, video_service: VideoService, create_video_request_file_data: CreateVideoRequest):
        """Test successful video creation"""
        mock_storage = MagicMock()
        mock_storage.upload = AsyncMock(return_value="https://storage.url")
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url")
        
        mock_metadata = VideoMetadata(
            width=1920,
            height=1080,
            file_size=len(create_video_request_file_data.file_data or b""),
            format=VideoFormat.MP4,
            duration=30.0,
            fps=30.0,
            bitrate=1000000
        )
        
        with patch("app.services.video.video_service.generate_storage_path", return_value="test/path"), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.video.video_service.insert_document", return_value="video_123"), \
             patch.object(video_service, "_extract_video_metadata", return_value=mock_metadata):
            
            response = await video_service.create_video(create_video_request_file_data)
            
            assert isinstance(response, CreateVideoResponse)
            assert response.success is True
            assert response.video_id == "video_123"
            assert response.storage_path == "test/path"
            assert response.storage_url == "https://storage.url"
            assert response.presigned_url == "https://presigned.url"
            assert response.message == ""

    @pytest.mark.asyncio
    async def test_create_video_validation_failure(self, video_service: VideoService):
        """Test video creation with validation failure"""
        invalid_request = CreateVideoRequest(
            filename="",
            video_type=VideoType.GENERAL
        )
        
        response = await video_service.create_video(invalid_request)
        
        assert isinstance(response, CreateVideoResponse)
        assert response.success is False
        assert response.video_id == ""
        assert response.storage_path == ""
        assert "Missing value for field: filename" in response.message

    @pytest.mark.asyncio
    async def test_create_video_exception(self, video_service: VideoService, create_video_request_file_data: CreateVideoRequest):
        """Test video creation with exception"""
        with patch("app.services.video.video_service.generate_storage_path", side_effect=Exception("Storage error")):
            response = await video_service.create_video(create_video_request_file_data)
            
            assert isinstance(response, CreateVideoResponse)
            assert response.success is False
            assert response.video_id == ""
            assert response.storage_path == ""
            assert "Failed to create video: Storage error" in response.message

    @pytest.mark.asyncio
    async def test_create_video_with_base64(self, video_service: VideoService, create_video_request_base64: CreateVideoRequest, sample_video_bytes: bytes):
        """Test video creation with base64 data"""
        mock_storage = MagicMock()
        mock_storage.upload = AsyncMock(return_value="https://storage.url")
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url")
        
        mock_metadata = VideoMetadata(file_size=len(sample_video_bytes))
        
        with patch("app.services.video.video_service.generate_storage_path", return_value="test/path"), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.video.video_service.insert_document", return_value="video_123"), \
             patch.object(video_service, "_extract_video_metadata", return_value=mock_metadata):
            
            response = await video_service.create_video(create_video_request_base64)
            
            assert isinstance(response, CreateVideoResponse)
            assert response.success is True
            assert response.video_id == "video_123"

    @pytest.mark.asyncio
    async def test_create_video_with_url(self, video_service: VideoService, create_video_request_url: CreateVideoRequest, sample_video_bytes: bytes):
        """Test video creation with URL source"""
        mock_storage = MagicMock()
        mock_storage.upload = AsyncMock(return_value="https://storage.url")
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url")
        
        mock_metadata = VideoMetadata(file_size=len(sample_video_bytes))
        
        mock_response = MagicMock()
        mock_response.content = sample_video_bytes
        mock_response.raise_for_status = MagicMock()
        
        with patch("app.services.video.video_service.generate_storage_path", return_value="test/path"), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.video.video_service.insert_document", return_value="video_123"), \
             patch("app.services.video.video_service.requests.get", return_value=mock_response), \
             patch.object(video_service, "_extract_video_metadata", return_value=mock_metadata):
            
            response = await video_service.create_video(create_video_request_url)
            
            assert isinstance(response, CreateVideoResponse)
            assert response.success is True
            assert response.video_id == "video_123"

    @pytest.mark.asyncio
    async def test_create_video_storage_upload_failure(self, video_service: VideoService, create_video_request_file_data: CreateVideoRequest):
        """Test video creation when storage upload fails"""
        mock_storage = MagicMock()
        mock_storage.upload = AsyncMock(side_effect=Exception("Upload failed"))
        
        mock_metadata = VideoMetadata(file_size=len(create_video_request_file_data.file_data or b""))
        
        with patch("app.services.video.video_service.generate_storage_path", return_value="test/path"), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch.object(video_service, "_extract_video_metadata", return_value=mock_metadata):
            
            response = await video_service.create_video(create_video_request_file_data)
            
            assert isinstance(response, CreateVideoResponse)
            assert response.success is False
            assert "Failed to create video: Upload failed" in response.message

    @pytest.mark.asyncio
    async def test_create_video_database_insert_failure(self, video_service: VideoService, create_video_request_file_data: CreateVideoRequest):
        """Test video creation when database insert fails"""
        mock_storage = MagicMock()
        mock_storage.upload = AsyncMock(return_value="https://storage.url")
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url")
        
        mock_metadata = VideoMetadata(file_size=len(create_video_request_file_data.file_data or b""))
        
        with patch("app.services.video.video_service.generate_storage_path", return_value="test/path"), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.video.video_service.insert_document", side_effect=Exception("DB Error")), \
             patch.object(video_service, "_extract_video_metadata", return_value=mock_metadata):
            
            response = await video_service.create_video(create_video_request_file_data)
            
            assert isinstance(response, CreateVideoResponse)
            assert response.success is False
            assert "Failed to create video: DB Error" in response.message

    @pytest.mark.asyncio
    async def test_create_video_with_all_optional_fields(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test video creation with all optional fields populated"""
        request = CreateVideoRequest(
            filename="complete_video.mp4",
            original_filename="original_complete.mp4",
            title="Complete Video",
            description="A complete test video",
            alt_text="Complete alt text",
            video_type=VideoType.GENERAL,
            source_type=VideoSourceType.UPLOAD,
            entity_id="entity_999",
            entity_type="complete_entity",
            file_data=sample_video_bytes,
            tags=["complete", "test", "video"]
        )
        
        mock_storage = MagicMock()
        mock_storage.upload = AsyncMock(return_value="https://storage.url")
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url")
        
        mock_metadata = VideoMetadata(file_size=len(sample_video_bytes))
        
        with patch("app.services.video.video_service.generate_storage_path", return_value="test/path"), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.video.video_service.insert_document", return_value="video_999") as mock_insert, \
             patch.object(video_service, "_extract_video_metadata", return_value=mock_metadata):
            
            response = await video_service.create_video(request)
            
            assert response.success is True
            assert response.video_id == "video_999"
            
            # Verify document was created with all fields
            document = mock_insert.call_args[0][1]
            assert document["filename"] == "complete_video.mp4"
            assert document["original_filename"] == "original_complete.mp4"
            assert document["title"] == "Complete Video"
            assert document["description"] == "A complete test video"
            assert document["alt_text"] == "Complete alt text"
            assert document["entity_id"] == "entity_999"
            assert document["entity_type"] == "complete_entity"
            assert document["tags"] == ["complete", "test", "video"]
            assert document["video_type"] == VideoType.GENERAL.value
            assert document["source_type"] == VideoSourceType.UPLOAD.value
            assert document["processing_status"] == MediaProcessingStatus.COMPLETED.value
            assert document["is_deleted"] is False
            assert document["ai_processed"] is False


class TestVideoServiceGetVideo:

    @pytest.mark.asyncio
    async def test_get_video_success(self, video_service: VideoService, mock_video_document: dict):
        """Test successful video retrieval"""
        mock_storage = MagicMock()
        mock_storage.upload = AsyncMock(return_value="https://storage.url")
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url")
        
        with patch("app.services.video.video_service.get_document", return_value=mock_video_document):
            response = await video_service.get_video(TEST_VIDEO_ID)
            
            assert isinstance(response, GetVideoResponse)
            assert response.success is True
            assert response.video is not None
            assert response.video.id == TEST_VIDEO_ID
            assert response.video.filename == mock_video_document["filename"]
            assert response.video.original_filename == mock_video_document["original_filename"]
            assert response.video.title == mock_video_document["title"]
            assert response.video.description == mock_video_document["description"]
            assert response.video.alt_text == mock_video_document["alt_text"]
            assert response.video.storage_path == mock_video_document["storage_path"]
            assert response.video.storage_url == mock_video_document["storage_url"]
            assert response.video.video_type == VideoType(mock_video_document["video_type"])
            assert response.video.source_type == VideoSourceType(mock_video_document["source_type"])
            assert response.video.entity_id == mock_video_document["entity_id"]
            assert response.video.entity_type == mock_video_document["entity_type"]
            assert response.video.metadata == VideoMetadata(**mock_video_document["metadata"])
            assert response.video.processing_status == MediaProcessingStatus(mock_video_document["processing_status"])
            assert response.video.uploaded_at == mock_video_document["uploaded_at"]
            assert response.video.updated_at == mock_video_document["updated_at"]
            assert response.video.processed_at == mock_video_document["processed_at"]
            assert response.video.tags == mock_video_document["tags"]
            assert response.video.is_deleted == mock_video_document["is_deleted"]

    @pytest.mark.asyncio
    async def test_get_video_not_found(self, video_service: VideoService):
        """Test video retrieval when video is not found"""
        with patch("app.services.video.video_service.get_document", return_value=None):
            response = await video_service.get_video(TEST_VIDEO_ID)
            
            assert isinstance(response, GetVideoResponse)
            assert response.success is False
            assert response.video is None
            assert response.message == "Video not found"

    @pytest.mark.asyncio
    async def test_get_video_exception(self, video_service: VideoService):
        """Test video retrieval with exception"""
        with patch("app.services.video.video_service.get_document", side_effect=Exception("Database error")):
            response = await video_service.get_video(TEST_VIDEO_ID)
            
            assert isinstance(response, GetVideoResponse)
            assert response.success is False
            assert response.video is None
            assert "Failed to get video: Database error" in response.message

    @pytest.mark.asyncio
    async def test_get_video_invalid_id(self, video_service: VideoService):
        """Test video retrieval with invalid ID"""
        response = await video_service.get_video("invalid_id")
        
        assert isinstance(response, GetVideoResponse)
        assert response.success is False
        assert response.video is None
        assert "Invalid document ID format" in response.message

    @pytest.mark.asyncio
    async def test_get_video_empty_id(self, video_service: VideoService):
        """Test video retrieval with empty ID"""
        response = await video_service.get_video("")
        
        assert isinstance(response, GetVideoResponse)
        assert response.success is False
        assert response.video is None
        assert "Invalid document ID format" in response.message