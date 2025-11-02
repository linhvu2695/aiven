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
    VideoUrlInfo,
    VideoUrlsResponse,
)
from app.classes.media import MediaProcessingStatus
from app.classes.image import ImageType, ImageSourceType

TEST_VIDEO_ID = "67206999f3949388f3a80900"
TEST_VIDEO_ID_2 = "67206999f3949388f3a80901"
TEST_VIDEO_ID_3 = "67206999f3949388f3a80902"
TEST_THUMBNAIL_ID = "67206999f3949388f3a80903"

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


class TestVideoServiceThumbnail:
    
    @pytest.mark.asyncio
    async def test_extract_video_thumbnail_success(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test successful thumbnail extraction from video"""
        # Mock cv2.VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 900,
        }.get(prop, 0)
        
        # Mock frame reading
        mock_frame = MagicMock()  # Simulated frame data
        mock_cap.read.return_value = (True, mock_frame)
        
        # Mock cv2.imencode to return success and encoded buffer
        mock_buffer = MagicMock()
        mock_buffer.tobytes.return_value = b"fake_jpeg_thumbnail_data"
        
        # Mock image service response
        mock_image_response = MagicMock()
        mock_image_response.success = True
        mock_image_response.image_id = TEST_THUMBNAIL_ID
        
        with patch("app.services.video.video_service.cv2.VideoCapture", return_value=mock_cap), \
             patch("app.services.video.video_service.cv2.imencode", return_value=(True, mock_buffer)), \
             patch("app.services.video.video_service.create_temp_local_file", return_value="/tmp/test_video.mp4"), \
             patch("app.services.video.video_service.os.path.exists", return_value=True), \
             patch("app.services.video.video_service.os.unlink"), \
             patch("app.services.video.video_service.ImageService") as mock_image_service_class:
            
            # Setup image service mock
            mock_image_service = MagicMock()
            mock_image_service.create_image = AsyncMock(return_value=mock_image_response)
            mock_image_service_class.return_value = mock_image_service
            
            thumbnail_id = await video_service._extract_video_thumbnail(
                video_data=sample_video_bytes,
                video_id=TEST_VIDEO_ID,
            )
            
            assert thumbnail_id == TEST_THUMBNAIL_ID
            
            # Verify cap.set was called to set frame position
            mock_cap.set.assert_called_once_with(cv2.CAP_PROP_POS_FRAMES, 450)  # middle frame
            
            # Verify frame was read
            mock_cap.read.assert_called_once()
            
            # Verify imencode was called
            assert mock_buffer.tobytes.call_count == 1
            
            # Verify image service create_image was called
            mock_image_service.create_image.assert_called_once()
            call_args = mock_image_service.create_image.call_args[0][0]
            assert call_args.filename == f"video_{TEST_VIDEO_ID}_thumbnail.jpg"
            assert call_args.original_filename == f"video_{TEST_VIDEO_ID}_thumbnail.jpg"
            assert call_args.title == f"Thumbnail for video {TEST_VIDEO_ID}"
            assert call_args.description == "Auto-generated thumbnail from video"
            assert call_args.image_type == ImageType.REPRESENTATIVE
            assert call_args.source_type == ImageSourceType.BASE64
            assert call_args.entity_id == TEST_VIDEO_ID
            assert call_args.entity_type == "video"
            assert call_args.file_data == b"fake_jpeg_thumbnail_data"

    @pytest.mark.asyncio
    async def test_extract_video_thumbnail_empty_video_id(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test thumbnail extraction with empty video ID"""
        thumbnail_id = await video_service._extract_video_thumbnail(
            video_data=sample_video_bytes,
            video_id="",
        )
        
        assert thumbnail_id is None

    @pytest.mark.asyncio
    async def test_extract_video_thumbnail_video_not_opened(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test thumbnail extraction when video file cannot be opened"""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        
        with patch("app.services.video.video_service.cv2.VideoCapture", return_value=mock_cap), \
             patch("app.services.video.video_service.create_temp_local_file", return_value="/tmp/test_video.mp4"), \
             patch("app.services.video.video_service.os.path.exists", return_value=True), \
             patch("app.services.video.video_service.os.unlink"):
            
            thumbnail_id = await video_service._extract_video_thumbnail(
                video_data=sample_video_bytes,
                video_id=TEST_VIDEO_ID,
            )
            
            assert thumbnail_id is None

    @pytest.mark.asyncio
    async def test_extract_video_thumbnail_frame_read_failure(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test thumbnail extraction when frame reading fails"""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 900,
        }.get(prop, 0)
        
        # Simulate frame read failure
        mock_cap.read.return_value = (False, None)
        
        with patch("app.services.video.video_service.cv2.VideoCapture", return_value=mock_cap), \
             patch("app.services.video.video_service.create_temp_local_file", return_value="/tmp/test_video.mp4"), \
             patch("app.services.video.video_service.os.path.exists", return_value=True), \
             patch("app.services.video.video_service.os.unlink"):
            
            thumbnail_id = await video_service._extract_video_thumbnail(
                video_data=sample_video_bytes,
                video_id=TEST_VIDEO_ID,
            )
            
            assert thumbnail_id is None
            mock_cap.release.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_video_thumbnail_encode_failure(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test thumbnail extraction when image encoding fails"""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 900,
        }.get(prop, 0)
        
        mock_frame = MagicMock()
        mock_cap.read.return_value = (True, mock_frame)
        
        # Simulate encode failure
        with patch("app.services.video.video_service.cv2.VideoCapture", return_value=mock_cap), \
             patch("app.services.video.video_service.cv2.imencode", return_value=(False, None)), \
             patch("app.services.video.video_service.create_temp_local_file", return_value="/tmp/test_video.mp4"), \
             patch("app.services.video.video_service.os.path.exists", return_value=True), \
             patch("app.services.video.video_service.os.unlink"):
            
            thumbnail_id = await video_service._extract_video_thumbnail(
                video_data=sample_video_bytes,
                video_id=TEST_VIDEO_ID,
            )
            
            assert thumbnail_id is None
            mock_cap.release.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_video_thumbnail_image_service_failure(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test thumbnail extraction when image service fails to create image"""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 900,
        }.get(prop, 0)
        
        mock_frame = MagicMock()
        mock_cap.read.return_value = (True, mock_frame)
        
        mock_buffer = MagicMock()
        mock_buffer.tobytes.return_value = b"fake_jpeg_thumbnail_data"
        
        # Mock image service to return failure
        mock_image_response = MagicMock()
        mock_image_response.success = False
        mock_image_response.message = "Image creation failed"
        
        with patch("app.services.video.video_service.cv2.VideoCapture", return_value=mock_cap), \
             patch("app.services.video.video_service.cv2.imencode", return_value=(True, mock_buffer)), \
             patch("app.services.video.video_service.create_temp_local_file", return_value="/tmp/test_video.mp4"), \
             patch("app.services.video.video_service.os.path.exists", return_value=True), \
             patch("app.services.video.video_service.os.unlink"), \
             patch("app.services.video.video_service.ImageService") as mock_image_service_class:
            
            mock_image_service = MagicMock()
            mock_image_service.create_image = AsyncMock(return_value=mock_image_response)
            mock_image_service_class.return_value = mock_image_service
            
            thumbnail_id = await video_service._extract_video_thumbnail(
                video_data=sample_video_bytes,
                video_id=TEST_VIDEO_ID,
            )
            
            assert thumbnail_id is None

    @pytest.mark.asyncio
    async def test_extract_video_thumbnail_exception_handling(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test thumbnail extraction handles exceptions gracefully"""
        with patch("app.services.video.video_service.create_temp_local_file", side_effect=Exception("Temp file error")):
            thumbnail_id = await video_service._extract_video_thumbnail(
                video_data=sample_video_bytes,
                video_id=TEST_VIDEO_ID,
            )
            
            assert thumbnail_id is None

    @pytest.mark.asyncio
    async def test_extract_video_thumbnail_cleanup_temp_file(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test that temporary file is cleaned up even on errors"""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = Exception("Unexpected error during get")
        
        with patch("app.services.video.video_service.cv2.VideoCapture", return_value=mock_cap), \
             patch("app.services.video.video_service.create_temp_local_file", return_value="/tmp/test_video.mp4"), \
             patch("app.services.video.video_service.os.path.exists", return_value=True), \
             patch("app.services.video.video_service.os.unlink") as mock_unlink:
            
            thumbnail_id = await video_service._extract_video_thumbnail(
                video_data=sample_video_bytes,
                video_id=TEST_VIDEO_ID,
            )
            
            assert thumbnail_id is None
            # Verify cleanup was called
            mock_unlink.assert_called_once_with("/tmp/test_video.mp4")

    @pytest.mark.asyncio
    async def test_extract_video_thumbnail_middle_frame_selection(self, video_service: VideoService, sample_video_bytes: bytes):
        """Test thumbnail extraction from video with middle frame selection"""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 10000,  # Large frame count
        }.get(prop, 0)
        
        mock_frame = MagicMock()
        mock_cap.read.return_value = (True, mock_frame)
        
        mock_buffer = MagicMock()
        mock_buffer.tobytes.return_value = b"fake_jpeg_thumbnail_data"
        
        mock_image_response = MagicMock()
        mock_image_response.success = True
        mock_image_response.image_id = TEST_THUMBNAIL_ID
        
        with patch("app.services.video.video_service.cv2.VideoCapture", return_value=mock_cap), \
             patch("app.services.video.video_service.cv2.imencode", return_value=(True, mock_buffer)), \
             patch("app.services.video.video_service.create_temp_local_file", return_value="/tmp/test_video.mp4"), \
             patch("app.services.video.video_service.os.path.exists", return_value=True), \
             patch("app.services.video.video_service.os.unlink"), \
             patch("app.services.video.video_service.ImageService") as mock_image_service_class:
            
            mock_image_service = MagicMock()
            mock_image_service.create_image = AsyncMock(return_value=mock_image_response)
            mock_image_service_class.return_value = mock_image_service
            
            thumbnail_id = await video_service._extract_video_thumbnail(
                video_data=sample_video_bytes,
                video_id=TEST_VIDEO_ID,
            )
            
            assert thumbnail_id == TEST_THUMBNAIL_ID
            
            # Verify middle frame (5000) was selected
            mock_cap.set.assert_called_once_with(cv2.CAP_PROP_POS_FRAMES, 5000)


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

    @pytest.mark.asyncio
    async def test_create_video_calls_thumbnail_extraction(self, video_service: VideoService, create_video_request_file_data: CreateVideoRequest):
        """Test that create_video calls thumbnail extraction"""
        mock_storage = MagicMock()
        mock_storage.upload = AsyncMock(return_value="https://storage.url")
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url")
        
        mock_metadata = VideoMetadata(file_size=len(create_video_request_file_data.file_data or b""))
        
        with patch("app.services.video.video_service.generate_storage_path", return_value="test/path"), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.video.video_service.insert_document", return_value=TEST_VIDEO_ID), \
             patch.object(video_service, "_extract_video_metadata", return_value=mock_metadata), \
             patch.object(video_service, "_extract_video_thumbnail", return_value=TEST_THUMBNAIL_ID) as mock_extract_thumbnail:
            
            response = await video_service.create_video(create_video_request_file_data)
            
            assert response.success is True
            assert response.video_id == TEST_VIDEO_ID
            
            # Verify thumbnail extraction was called with correct parameters
            mock_extract_thumbnail.assert_called_once_with(
                video_data=create_video_request_file_data.file_data,
                video_id=TEST_VIDEO_ID
            )

    @pytest.mark.asyncio
    async def test_create_video_thumbnail_extraction_failure_does_not_fail_creation(self, video_service: VideoService, create_video_request_file_data: CreateVideoRequest):
        """Test that video creation succeeds even if thumbnail extraction fails"""
        mock_storage = MagicMock()
        mock_storage.upload = AsyncMock(return_value="https://storage.url")
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url")
        
        mock_metadata = VideoMetadata(file_size=len(create_video_request_file_data.file_data or b""))
        
        with patch("app.services.video.video_service.generate_storage_path", return_value="test/path"), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.video.video_service.insert_document", return_value=TEST_VIDEO_ID), \
             patch.object(video_service, "_extract_video_metadata", return_value=mock_metadata), \
             patch.object(video_service, "_extract_video_thumbnail", side_effect=Exception("Thumbnail extraction failed")):
            
            response = await video_service.create_video(create_video_request_file_data)
            
            # Video creation should still succeed
            assert response.success is True
            assert response.video_id == TEST_VIDEO_ID
            assert response.storage_path == "test/path"

    @pytest.mark.asyncio
    async def test_create_video_thumbnail_extraction_returns_none(self, video_service: VideoService, create_video_request_file_data: CreateVideoRequest):
        """Test that video creation succeeds when thumbnail extraction returns None"""
        mock_storage = MagicMock()
        mock_storage.upload = AsyncMock(return_value="https://storage.url")
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url")
        
        mock_metadata = VideoMetadata(file_size=len(create_video_request_file_data.file_data or b""))
        
        with patch("app.services.video.video_service.generate_storage_path", return_value="test/path"), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.video.video_service.insert_document", return_value=TEST_VIDEO_ID), \
             patch.object(video_service, "_extract_video_metadata", return_value=mock_metadata), \
             patch.object(video_service, "_extract_video_thumbnail", return_value=None) as mock_extract_thumbnail:
            
            response = await video_service.create_video(create_video_request_file_data)
            
            # Video creation should still succeed
            assert response.success is True
            assert response.video_id == TEST_VIDEO_ID
            
            # Verify thumbnail extraction was called
            mock_extract_thumbnail.assert_called_once()


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


class TestVideoServicePresignedUrl:

    @pytest.mark.asyncio
    async def test_get_video_presigned_url_success(self, video_service: VideoService, mock_video_document: dict):
        """Test successful generation of presigned URL for a single video"""
        mock_storage = MagicMock()
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url/video.mp4")
        
        with patch("app.services.video.video_service.get_document", return_value=mock_video_document), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage):
            response = await video_service.get_video_presigned_url(TEST_VIDEO_ID)
            
            assert isinstance(response, VideoUrlInfo)
            assert response.video_id == TEST_VIDEO_ID
            assert response.success is True
            assert response.url == "https://presigned.url/video.mp4"
            assert response.expires_at is not None
            assert response.message == ""
            
            # Verify storage repo was called with correct parameters
            mock_storage.get_presigned_url.assert_called_once_with(
                mock_video_document["storage_path"],
                60 * 60  # VIDEO_PRESIGNED_URL_EXPIRATION
            )

    @pytest.mark.asyncio
    async def test_get_video_presigned_url_video_not_found(self, video_service: VideoService):
        """Test presigned URL generation when video is not found"""
        with patch("app.services.video.video_service.get_document", return_value=None):
            response = await video_service.get_video_presigned_url(TEST_VIDEO_ID)
            
            assert isinstance(response, VideoUrlInfo)
            assert response.video_id == TEST_VIDEO_ID
            assert response.success is False
            assert response.url is ""
            assert response.expires_at is None
            assert "Failed to get video for presigned URL" in response.message

    @pytest.mark.asyncio
    async def test_get_video_presigned_url_invalid_id(self, video_service: VideoService):
        """Test presigned URL generation with invalid video ID"""
        response = await video_service.get_video_presigned_url("invalid_id")
        
        assert isinstance(response, VideoUrlInfo)
        assert response.video_id == "invalid_id"
        assert response.success is False
        assert response.url is ""
        assert response.expires_at is None
        assert "Failed to get video for presigned URL" in response.message

    @pytest.mark.asyncio
    async def test_get_video_presigned_url_storage_failure(self, video_service: VideoService, mock_video_document: dict):
        """Test presigned URL generation when storage operation fails"""
        mock_storage = MagicMock()
        mock_storage.get_presigned_url = AsyncMock(side_effect=Exception("Storage error"))
        
        with patch("app.services.video.video_service.get_document", return_value=mock_video_document), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage):
            response = await video_service.get_video_presigned_url(TEST_VIDEO_ID)
            
            assert isinstance(response, VideoUrlInfo)
            assert response.video_id == TEST_VIDEO_ID
            assert response.success is False
            assert response.url is ""
            assert response.expires_at is None
            assert "Failed to get video presigned URL: Storage error" in response.message

    @pytest.mark.asyncio
    async def test_get_video_presigned_url_empty_id(self, video_service: VideoService):
        """Test presigned URL generation with empty video ID"""
        response = await video_service.get_video_presigned_url("")
        
        assert isinstance(response, VideoUrlInfo)
        assert response.video_id == ""
        assert response.success is False
        assert response.url is ""
        assert response.expires_at is None
        assert "Failed to get video for presigned URL" in response.message


class TestVideoServicePresignedUrls:

    @pytest.mark.asyncio
    async def test_get_videos_presigned_urls_success(self, video_service: VideoService, mock_video_document: dict):
        """Test successful generation of presigned URLs for multiple videos"""        
        mock_doc_2 = mock_video_document.copy()
        mock_doc_2["_id"] = ObjectId(TEST_VIDEO_ID_2)
        mock_doc_2["storage_path"] = "test/path2"
        
        mock_doc_3 = mock_video_document.copy()
        mock_doc_3["_id"] = ObjectId(TEST_VIDEO_ID_3)
        mock_doc_3["storage_path"] = "test/path3"
        
        def mock_get_document(collection: str, video_id: str):
            if video_id == TEST_VIDEO_ID:
                return mock_video_document
            elif video_id == TEST_VIDEO_ID_2:
                return mock_doc_2
            elif video_id == TEST_VIDEO_ID_3:
                return mock_doc_3
            return None
        
        mock_storage = MagicMock()
        mock_storage.get_presigned_url = AsyncMock(side_effect=lambda path, exp: f"https://presigned.url/{path}")
        
        with patch("app.services.video.video_service.get_document", side_effect=mock_get_document), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage):
            
            from app.classes.video import VideoUrlsResponse
            response = await video_service.get_videos_presigned_urls([TEST_VIDEO_ID, TEST_VIDEO_ID_2, TEST_VIDEO_ID_3])
            
            assert isinstance(response, VideoUrlsResponse)
            assert response.success is True
            assert len(response.results) == 3
            assert response.message == "Generated presigned URLs for 3/3 videos"
            
            # Verify first result
            assert response.results[0].video_id == TEST_VIDEO_ID
            assert response.results[0].url == "https://presigned.url/test/path"
            assert response.results[0].success is True
            assert response.results[0].expires_at is not None
            
            # Verify second result
            assert response.results[1].video_id == TEST_VIDEO_ID_2
            assert response.results[1].url == "https://presigned.url/test/path2"
            assert response.results[1].success is True
            assert response.results[1].expires_at is not None
            
            # Verify third result
            assert response.results[2].video_id == TEST_VIDEO_ID_3
            assert response.results[2].url == "https://presigned.url/test/path3"
            assert response.results[2].success is True
            assert response.results[2].expires_at is not None

    @pytest.mark.asyncio
    async def test_get_videos_presigned_urls_partial_success(self, video_service: VideoService, mock_video_document: dict):
        """Test presigned URLs generation with some videos failing"""        
        mock_doc_3 = mock_video_document.copy()
        mock_doc_3["_id"] = ObjectId(TEST_VIDEO_ID_3)
        mock_doc_3["storage_path"] = "test/path3"
        
        def mock_get_document(collection: str, video_id: str):
            if video_id == TEST_VIDEO_ID:
                return mock_video_document
            elif video_id == TEST_VIDEO_ID_3:
                return mock_doc_3
            return None
        
        mock_storage = MagicMock()
        mock_storage.get_presigned_url = AsyncMock(side_effect=lambda path, exp: f"https://presigned.url/{path}")
        
        with patch("app.services.video.video_service.get_document", side_effect=mock_get_document), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage):
            
            from app.classes.video import VideoUrlsResponse
            response = await video_service.get_videos_presigned_urls([TEST_VIDEO_ID, TEST_VIDEO_ID_2, TEST_VIDEO_ID_3])
            
            assert isinstance(response, VideoUrlsResponse)
            assert response.success is False  # Overall success is False because one failed
            assert len(response.results) == 3
            assert "Generated presigned URLs for 2/3 videos (some requests failed)" in response.message
            
            # Verify first result (success)
            assert response.results[0].video_id == TEST_VIDEO_ID
            assert response.results[0].url == "https://presigned.url/test/path"
            assert response.results[0].success is True
            
            # Verify second result (failure - invalid ID)
            assert response.results[1].video_id == TEST_VIDEO_ID_2
            assert response.results[1].url == ""
            assert response.results[1].success is False
            assert "Failed to get video for presigned URL" in response.results[1].message
            
            # Verify third result (success)
            assert response.results[2].video_id == TEST_VIDEO_ID_3
            assert response.results[2].url == "https://presigned.url/test/path3"
            assert response.results[2].success is True

    @pytest.mark.asyncio
    async def test_get_videos_presigned_urls_all_failures(self, video_service: VideoService):
        """Test presigned URLs generation when all videos fail"""
        with patch("app.services.video.video_service.get_document", return_value=None):
            from app.classes.video import VideoUrlsResponse
            response = await video_service.get_videos_presigned_urls([TEST_VIDEO_ID_2, TEST_VIDEO_ID_3])
            
            assert isinstance(response, VideoUrlsResponse)
            assert response.success is False
            assert len(response.results) == 2
            assert "Generated presigned URLs for 0/2 videos (some requests failed)" in response.message
            
            # All results should be failures
            for result in response.results:
                assert result.success is False
                assert result.url == ""
                assert result.expires_at is None

    @pytest.mark.asyncio
    async def test_get_videos_presigned_urls_empty_list(self, video_service: VideoService):
        """Test presigned URLs generation with empty video ID list"""
        from app.classes.video import VideoUrlsResponse
        response = await video_service.get_videos_presigned_urls([])
        
        assert isinstance(response, VideoUrlsResponse)
        assert response.success is True  # No videos to process, so success
        assert len(response.results) == 0
        assert response.message == "Generated presigned URLs for 0/0 videos"

    @pytest.mark.asyncio
    async def test_get_videos_presigned_urls_single_video(self, video_service: VideoService, mock_video_document: dict):
        """Test presigned URLs generation with a single video"""
        mock_storage = MagicMock()
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url/video.mp4")
        
        with patch("app.services.video.video_service.get_document", return_value=mock_video_document), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage):
            
            from app.classes.video import VideoUrlsResponse
            response = await video_service.get_videos_presigned_urls([TEST_VIDEO_ID])
            
            assert isinstance(response, VideoUrlsResponse)
            assert response.success is True
            assert len(response.results) == 1
            assert response.message == "Generated presigned URLs for 1/1 videos"
            
            assert response.results[0].video_id == TEST_VIDEO_ID
            assert response.results[0].url == "https://presigned.url/video.mp4"
            assert response.results[0].success is True

    @pytest.mark.asyncio
    async def test_get_videos_presigned_urls_exception_handling(self, video_service: VideoService):
        """Test presigned URLs generation handles exceptions gracefully"""
        # Mock get_document to raise an exception
        with patch("app.services.video.video_service.get_document", side_effect=Exception("Database connection lost")):
            from app.classes.video import VideoUrlsResponse
            response = await video_service.get_videos_presigned_urls([TEST_VIDEO_ID])
            
            assert isinstance(response, VideoUrlsResponse)
            assert response.success is False
            assert len(response.results) == 1
            assert response.results[0].video_id == TEST_VIDEO_ID
            assert response.results[0].success is False
            assert "Failed to get video for presigned URL" in response.results[0].message
            assert "Database connection lost" in response.results[0].message

    @pytest.mark.asyncio
    async def test_get_videos_presigned_urls_maintains_order(self, video_service: VideoService, mock_video_document: dict):
        """Test that presigned URLs results maintain the same order as input IDs"""
        mock_docs = {}
        for i, vid in enumerate([TEST_VIDEO_ID, TEST_VIDEO_ID_2, TEST_VIDEO_ID_3]):
            doc = mock_video_document.copy()
            doc["_id"] = ObjectId(vid)
            doc["storage_path"] = f"test/path{i}"
            mock_docs[vid] = doc
        
        def mock_get_document(collection: str, video_id: str):
            return mock_docs.get(video_id)
        
        mock_storage = MagicMock()
        mock_storage.get_presigned_url = AsyncMock(side_effect=lambda path, exp: f"https://presigned.url/{path}")
        
        with patch("app.services.video.video_service.get_document", side_effect=mock_get_document), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage):
            # Request in specific order
            input_ids = [TEST_VIDEO_ID_3, TEST_VIDEO_ID, TEST_VIDEO_ID_2]
            response = await video_service.get_videos_presigned_urls(input_ids)
            
            assert isinstance(response, VideoUrlsResponse)
            assert response.success is True
            assert len(response.results) == 3
            
            # Verify order is maintained
            for i, video_id in enumerate([TEST_VIDEO_ID_3, TEST_VIDEO_ID, TEST_VIDEO_ID_2]):
                assert response.results[i].video_id == video_id

    @pytest.mark.asyncio
    async def test_get_videos_presigned_urls_duplicate_ids(self, video_service: VideoService, mock_video_document: dict):
        """Test presigned URLs generation with duplicate video IDs"""
        mock_storage = MagicMock()
        mock_storage.get_presigned_url = AsyncMock(return_value="https://presigned.url/video.mp4")
        
        with patch("app.services.video.video_service.get_document", return_value=mock_video_document), \
             patch("app.services.video.video_service.FirebaseStorageRepository", return_value=mock_storage):
            # Request same ID multiple times
            response = await video_service.get_videos_presigned_urls([TEST_VIDEO_ID, TEST_VIDEO_ID, TEST_VIDEO_ID])
            
            assert isinstance(response, VideoUrlsResponse)
            assert response.success is True
            assert len(response.results) == 3
            assert response.message == "Generated presigned URLs for 3/3 videos"
            
            # All should be successful and have same video_id
            for result in response.results:
                assert result.video_id == TEST_VIDEO_ID
                assert result.success is True
                assert result.url == "https://presigned.url/video.mp4"


class TestVideoServiceListVideos:

    @pytest.mark.asyncio
    async def test_list_videos_default_params(self, video_service: VideoService, mock_video_document: dict):
        """Test listing videos with default parameters"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        mock_docs = [mock_video_document]
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=1), \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs):
            
            request = VideoListRequest()
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 1
            assert response.total == 1
            assert response.page == 1
            assert response.page_size == 10
            
            # Verify first video
            video = response.videos[0]
            assert video.id == TEST_VIDEO_ID
            assert video.filename == mock_video_document["filename"]
            assert video.title == mock_video_document["title"]

    @pytest.mark.asyncio
    async def test_list_videos_with_pagination(self, video_service: VideoService, mock_video_document: dict):
        """Test listing videos with custom pagination"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        # Create multiple mock documents
        mock_docs = []
        for i in range(5):
            doc = mock_video_document.copy()
            doc["_id"] = ObjectId(f"67206999f3949388f3a8090{i}")
            doc["filename"] = f"video_{i}.mp4"
            mock_docs.append(doc)
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=25), \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs):
            
            request = VideoListRequest(page=2, page_size=5)
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 5
            assert response.total == 25
            assert response.page == 2
            assert response.page_size == 5

    @pytest.mark.asyncio
    async def test_list_videos_filter_by_video_type(self, video_service: VideoService, mock_video_document: dict):
        """Test listing videos filtered by video type"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        mock_docs = [mock_video_document]
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=1) as mock_count, \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs) as mock_find:
            
            request = VideoListRequest(video_type=VideoType.GENERAL)
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 1
            assert response.videos[0].video_type == VideoType.GENERAL
            
            # Verify filters were passed correctly
            filters = mock_count.call_args[0][1]
            assert filters["video_type"] == VideoType.GENERAL.value
            assert filters["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_list_videos_filter_by_entity_id(self, video_service: VideoService, mock_video_document: dict):
        """Test listing videos filtered by entity ID"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        mock_docs = [mock_video_document]
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=1) as mock_count, \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs):
            
            request = VideoListRequest(entity_id="entity_123")
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 1
            assert response.videos[0].entity_id == "entity_123"
            
            # Verify filters were passed correctly
            filters = mock_count.call_args[0][1]
            assert filters["entity_id"] == "entity_123"
            assert filters["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_list_videos_filter_by_entity_type(self, video_service: VideoService, mock_video_document: dict):
        """Test listing videos filtered by entity type"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        mock_docs = [mock_video_document]
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=1) as mock_count, \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs):
            
            request = VideoListRequest(entity_type="test_entity")
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 1
            assert response.videos[0].entity_type == "test_entity"
            
            # Verify filters were passed correctly
            filters = mock_count.call_args[0][1]
            assert filters["entity_type"] == "test_entity"
            assert filters["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_list_videos_filter_multiple_criteria(self, video_service: VideoService, mock_video_document: dict):
        """Test listing videos with multiple filter criteria"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        mock_docs = [mock_video_document]
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=1) as mock_count, \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs):
            
            request = VideoListRequest(
                video_type=VideoType.GENERAL,
                entity_id="entity_123",
                entity_type="test_entity"
            )
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 1
            
            # Verify all filters were passed correctly
            filters = mock_count.call_args[0][1]
            assert filters["video_type"] == VideoType.GENERAL.value
            assert filters["entity_id"] == "entity_123"
            assert filters["entity_type"] == "test_entity"
            assert filters["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_list_videos_include_deleted(self, video_service: VideoService, mock_video_document: dict):
        """Test listing videos including deleted ones"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        # Create both deleted and non-deleted videos
        mock_doc_deleted = mock_video_document.copy()
        mock_doc_deleted["_id"] = ObjectId(TEST_VIDEO_ID_2)
        mock_doc_deleted["is_deleted"] = True
        mock_docs = [mock_video_document, mock_doc_deleted]
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=2) as mock_count, \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs):
            
            request = VideoListRequest(include_deleted=True)
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 2
            assert response.total == 2
            
            # Verify is_deleted filter was not applied
            filters = mock_count.call_args[0][1]
            assert "is_deleted" not in filters

    @pytest.mark.asyncio
    async def test_list_videos_exclude_deleted(self, video_service: VideoService, mock_video_document: dict):
        """Test listing videos excluding deleted ones (default behavior)"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        mock_docs = [mock_video_document]
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=1) as mock_count, \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs):
            
            request = VideoListRequest(include_deleted=False)
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 1
            assert response.videos[0].is_deleted is False
            
            # Verify is_deleted filter was applied
            filters = mock_count.call_args[0][1]
            assert filters["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_list_videos_empty_results(self, video_service: VideoService):
        """Test listing videos when no videos exist"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=0), \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=[]):
            
            request = VideoListRequest()
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 0
            assert response.total == 0
            assert response.page == 1
            assert response.page_size == 10

    @pytest.mark.asyncio
    async def test_list_videos_large_page_size(self, video_service: VideoService, mock_video_document: dict):
        """Test listing videos with large page size"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        # Create 100 mock documents
        mock_docs = []
        for i in range(100):
            doc = mock_video_document.copy()
            doc["_id"] = ObjectId(f"67206999f3949388f3a80{i:03d}")
            mock_docs.append(doc)
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=100), \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs):
            
            request = VideoListRequest(page=1, page_size=100)
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 100
            assert response.total == 100
            assert response.page == 1
            assert response.page_size == 100

    @pytest.mark.asyncio
    async def test_list_videos_pagination_skip_calculation(self, video_service: VideoService, mock_video_document: dict):
        """Test that pagination skip is calculated correctly"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        mock_docs = [mock_video_document]
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=50), \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs) as mock_find:
            
            # Request page 3 with page_size 10
            request = VideoListRequest(page=3, page_size=10)
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            
            # Verify skip was calculated correctly (page 3 means skip first 20 items)
            call_kwargs = mock_find.call_args[1]
            assert call_kwargs["skip"] == 20
            assert call_kwargs["limit"] == 10

    @pytest.mark.asyncio
    async def test_list_videos_sort_by_updated_at_desc(self, video_service: VideoService, mock_video_document: dict):
        """Test that videos are sorted by updated_at in descending order (most recent first)"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        mock_docs = [mock_video_document]
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=1), \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs) as mock_find:
            
            request = VideoListRequest()
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            
            # Verify sort parameters
            call_kwargs = mock_find.call_args[1]
            assert call_kwargs["sort_by"] == "updated_at"
            assert call_kwargs["asc"] is False  # Descending order

    @pytest.mark.asyncio
    async def test_list_videos_exception_handling(self, video_service: VideoService):
        """Test that exceptions are handled gracefully"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        with patch("app.services.video.video_service.count_documents_with_filters", side_effect=Exception("Database error")):
            
            request = VideoListRequest()
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 0
            assert response.total == 0
            assert response.page == 1
            assert response.page_size == 10

    @pytest.mark.asyncio
    async def test_list_videos_minimal_document_fields(self, video_service: VideoService):
        """Test listing videos with minimal document fields"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        # Create a minimal mock document
        minimal_doc = {
            "_id": ObjectId(TEST_VIDEO_ID),
            "filename": "minimal_video.mp4",
            "video_type": VideoType.GENERAL.value,
            "source_type": VideoSourceType.UPLOAD.value,
            "storage_path": "test/path",
            "processing_status": MediaProcessingStatus.COMPLETED.value,
        }
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=1), \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=[minimal_doc]):
            
            request = VideoListRequest()
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 1
            
            # Verify minimal fields are handled correctly
            video = response.videos[0]
            assert video.id == TEST_VIDEO_ID
            assert video.filename == "minimal_video.mp4"
            assert video.title is None
            assert video.description is None
            assert video.tags == []

    @pytest.mark.asyncio
    async def test_list_videos_complete_video_info_mapping(self, video_service: VideoService, mock_video_document: dict):
        """Test that all VideoInfo fields are correctly mapped from document"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=1), \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=[mock_video_document]):
            
            request = VideoListRequest()
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 1
            
            video = response.videos[0]
            # Verify all fields are correctly mapped
            assert video.id == str(mock_video_document["_id"])
            assert video.filename == mock_video_document["filename"]
            assert video.original_filename == mock_video_document["original_filename"]
            assert video.title == mock_video_document["title"]
            assert video.description == mock_video_document["description"]
            assert video.alt_text == mock_video_document["alt_text"]
            assert video.storage_path == mock_video_document["storage_path"]
            assert video.storage_url == mock_video_document["storage_url"]
            assert video.video_type == VideoType(mock_video_document["video_type"])
            assert video.source_type == VideoSourceType(mock_video_document["source_type"])
            assert video.entity_id == mock_video_document["entity_id"]
            assert video.entity_type == mock_video_document["entity_type"]
            assert video.metadata.width == mock_video_document["metadata"]["width"]
            assert video.metadata.height == mock_video_document["metadata"]["height"]
            assert video.processing_status == MediaProcessingStatus(mock_video_document["processing_status"])
            assert video.uploaded_at == mock_video_document["uploaded_at"]
            assert video.updated_at == mock_video_document["updated_at"]
            assert video.processed_at == mock_video_document["processed_at"]
            assert video.tags == mock_video_document["tags"]
            assert video.is_deleted == mock_video_document["is_deleted"]

    @pytest.mark.asyncio
    async def test_list_videos_first_page(self, video_service: VideoService, mock_video_document: dict):
        """Test listing first page of videos"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        mock_docs = [mock_video_document]
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=30), \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs) as mock_find:
            
            request = VideoListRequest(page=1, page_size=10)
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert response.page == 1
            assert response.total == 30
            
            # Verify skip is 0 for first page
            call_kwargs = mock_find.call_args[1]
            assert call_kwargs["skip"] == 0

    @pytest.mark.asyncio
    async def test_list_videos_last_page_partial_results(self, video_service: VideoService, mock_video_document: dict):
        """Test listing last page when it has fewer items than page_size"""
        from app.classes.video import VideoListRequest, VideoListResponse
        
        # Only 3 videos on the last page
        mock_docs = []
        for i in range(3):
            doc = mock_video_document.copy()
            doc["_id"] = ObjectId(f"67206999f3949388f3a8090{i}")
            mock_docs.append(doc)
        
        with patch("app.services.video.video_service.count_documents_with_filters", return_value=23), \
             patch("app.services.video.video_service.find_documents_with_filters", return_value=mock_docs):
            
            # Request page 3 with page_size 10 (would skip 20, expecting 3 results)
            request = VideoListRequest(page=3, page_size=10)
            response = await video_service.list_videos(request)
            
            assert isinstance(response, VideoListResponse)
            assert len(response.videos) == 3
            assert response.total == 23
            assert response.page == 3
            assert response.page_size == 10
