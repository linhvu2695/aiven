import pytest
import io
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock
from datetime import datetime
from app.api.video_api import router
from app.classes.video import (
    CreateVideoRequest,
    CreateVideoResponse,
    GetVideoResponse,
    VideoInfo,
    VideoType,
    VideoSourceType,
    VideoMetadata,
    VideoFormat,
    VideoListRequest,
    VideoListResponse,
)
from app.classes.media import MediaProcessingStatus

app = FastAPI()
app.include_router(router, prefix="/videos")

# Test constants - using valid MongoDB ObjectId format
TEST_VIDEO_ID = "507f1f77bcf86cd799439011"
TEST_VIDEO_ID_2 = "507f191e810c19729de860ea"
TEST_STORAGE_PATH = "videos/test/video.mp4"
TEST_STORAGE_URL = "https://storage.example.com/videos/test/video.mp4"
TEST_PRESIGNED_URL = "https://storage.example.com/videos/test/video.mp4?token=abc123"

# Reusable test data
_TEST_VIDEO_METADATA = VideoMetadata(
    width=1920,
    height=1080,
    file_size=1024000,
    format=VideoFormat.MP4,
    duration=60.5,
    fps=30.0,
    bitrate=128000,
)

_TEST_VIDEO_INFO = VideoInfo(
    id=TEST_VIDEO_ID,
    filename="test_video.mp4",
    original_filename="original_test.mp4",
    title="Test Video",
    description="A test video for unit tests",
    alt_text="Test video alt text",
    storage_path=TEST_STORAGE_PATH,
    storage_url=TEST_STORAGE_URL,
    video_type=VideoType.GENERAL,
    source_type=VideoSourceType.UPLOAD,
    entity_id=None,
    entity_type=None,
    metadata=_TEST_VIDEO_METADATA,
    processing_status=MediaProcessingStatus.COMPLETED,
    uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
    updated_at=datetime(2024, 1, 1, 12, 0, 0),
    processed_at=datetime(2024, 1, 1, 12, 5, 0),
    tags=["test", "video"],
    is_deleted=False,
)


class TestVideoApiUpload:
    """Test cases for the video upload endpoint"""

    @pytest.mark.asyncio
    async def test_upload_video_success(self):
        """Test successful video upload with minimal parameters"""
        mock_response = CreateVideoResponse(
            success=True,
            video_id=TEST_VIDEO_ID,
            storage_path=TEST_STORAGE_PATH,
            storage_url=TEST_STORAGE_URL,
            presigned_url=TEST_PRESIGNED_URL,
            message="Video uploaded successfully",
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.create_video",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                # Create a test video file
                test_video_content = b"fake video content for testing"
                test_file = io.BytesIO(test_video_content)

                files = {"file": ("test_video.mp4", test_file, "video/mp4")}

                response = await ac.post("/videos/upload", files=files)

                # Verify the service was called
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert isinstance(call_args, CreateVideoRequest)
                assert call_args.filename == "test_video.mp4"
                assert call_args.original_filename == "test_video.mp4"
                assert call_args.video_type == VideoType.GENERAL
                assert call_args.source_type == VideoSourceType.UPLOAD
                assert call_args.file_data == test_video_content

                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["video_id"] == TEST_VIDEO_ID
                assert data["storage_path"] == TEST_STORAGE_PATH
                assert data["storage_url"] == TEST_STORAGE_URL
                assert data["presigned_url"] == TEST_PRESIGNED_URL

    @pytest.mark.asyncio
    async def test_upload_video_with_title_and_description(self):
        """Test video upload with title and description"""
        mock_response = CreateVideoResponse(
            success=True,
            video_id=TEST_VIDEO_ID,
            storage_path=TEST_STORAGE_PATH,
            storage_url=TEST_STORAGE_URL,
            presigned_url=TEST_PRESIGNED_URL,
            message="",
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.create_video",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                test_video_content = b"fake video content"
                test_file = io.BytesIO(test_video_content)

                # Use params for title and description, files for the file
                files = {"file": ("my_video.mp4", test_file, "video/mp4")}
                params = {
                    "title": "My Awesome Video",
                    "description": "This is a great video about testing",
                }

                response = await ac.post("/videos/upload", files=files, params=params)

                # Verify the service was called with correct parameters
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert isinstance(call_args, CreateVideoRequest)
                assert call_args.filename == "my_video.mp4"
                assert call_args.title == "My Awesome Video"
                assert call_args.description == "This is a great video about testing"
                assert call_args.video_type == VideoType.GENERAL
                assert call_args.source_type == VideoSourceType.UPLOAD

                # Verify the response
                assert response.status_code == 200
                response_data = response.json()
                assert response_data["success"] is True
                assert response_data["video_id"] == TEST_VIDEO_ID
                assert response_data["storage_path"] == TEST_STORAGE_PATH
                assert response_data["storage_url"] == TEST_STORAGE_URL
                assert response_data["presigned_url"] == TEST_PRESIGNED_URL
                assert response_data["message"] == ""

    @pytest.mark.asyncio
    async def test_upload_video_missing_file(self):
        """Test video upload without a file"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Send request without file
            response = await ac.post("/videos/upload")

            # Should return 400 error
            assert response.status_code == 422  # FastAPI validation error

    @pytest.mark.asyncio
    async def test_upload_video_service_failure(self):
        """Test video upload when service returns failure"""
        mock_response = CreateVideoResponse(
            success=False,
            video_id="",
            storage_path="",
            storage_url=None,
            presigned_url=None,
            message="Invalid format",
        )

        with patch(
            "app.services.video.video_service.VideoService.create_video",
            new=AsyncMock(return_value=mock_response),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                test_video_content = b"invalid content"
                test_file = io.BytesIO(test_video_content)

                files = {"file": ("invalid.txt", test_file, "text/plain")}

                response = await ac.post("/videos/upload", files=files)

                # API now returns 400 status code with the response body
                assert response.status_code == 400
                data = response.json()
                assert data["success"] is False
                assert data["message"] == "Invalid format"
                assert data["video_id"] == ""
                assert data["storage_path"] == ""

    @pytest.mark.asyncio
    async def test_upload_video_service_exception(self):
        """Test video upload when service raises an exception"""
        with patch(
            "app.services.video.video_service.VideoService.create_video",
            new=AsyncMock(side_effect=Exception("Database connection error")),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                test_video_content = b"test content"
                test_file = io.BytesIO(test_video_content)

                files = {"file": ("test.mp4", test_file, "video/mp4")}

                response = await ac.post("/videos/upload", files=files)

                # Should return 500 error
                assert response.status_code == 500
                data = response.json()
                assert "detail" in data
                assert "Failed to upload video" in data["detail"]
                assert "Database connection error" in data["detail"]

    @pytest.mark.asyncio
    async def test_upload_video_different_formats(self):
        """Test video upload with different video formats"""
        formats = [
            ("test.mp4", "video/mp4"),
            ("test.webm", "video/webm"),
            ("test.avi", "video/avi"),
            ("test.mov", "video/quicktime"),
        ]

        for filename, content_type in formats:
            mock_response = CreateVideoResponse(
                success=True,
                video_id=TEST_VIDEO_ID,
                storage_path=f"videos/{filename}",
                storage_url=f"https://storage.example.com/videos/{filename}",
                presigned_url=TEST_PRESIGNED_URL,
                message="",
            )

            mock_service = AsyncMock(return_value=mock_response)
            with patch(
                "app.services.video.video_service.VideoService.create_video",
                new=mock_service,
            ):
                transport = ASGITransport(app=app)
                async with AsyncClient(
                    transport=transport, base_url="http://test"
                ) as ac:
                    test_video_content = b"test video content"
                    test_file = io.BytesIO(test_video_content)

                    files = {"file": (filename, test_file, content_type)}

                    response = await ac.post("/videos/upload", files=files)

                    # Verify the service was called
                    mock_service.assert_called_once()
                    call_args = mock_service.call_args[0][0]
                    assert call_args.filename == filename

                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True


class TestVideoApiGetVideo:
    """Test cases for the get video endpoint"""

    @pytest.mark.asyncio
    async def test_get_video_success(self):
        """Test successfully retrieving a video by ID"""
        mock_response = GetVideoResponse(
            success=True, video=_TEST_VIDEO_INFO, message=""
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.get_video",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(f"/videos/{TEST_VIDEO_ID}")

                # Verify the service was called with correct video_id
                mock_service.assert_called_once_with(TEST_VIDEO_ID)

                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["video"] is not None
                assert data["video"]["id"] == TEST_VIDEO_ID
                assert data["video"]["filename"] == "test_video.mp4"
                assert data["video"]["title"] == "Test Video"
                assert data["video"]["description"] == "A test video for unit tests"
                assert data["video"]["storage_path"] == TEST_STORAGE_PATH
                assert data["video"]["storage_url"] == TEST_STORAGE_URL
                assert data["video"]["video_type"] == VideoType.GENERAL
                assert data["video"]["source_type"] == VideoSourceType.UPLOAD
                assert data["video"]["processing_status"] == MediaProcessingStatus.COMPLETED
                assert data["video"]["tags"] == ["test", "video"]
                assert data["video"]["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_get_video_with_metadata(self):
        """Test retrieving a video with complete metadata"""
        mock_response = GetVideoResponse(
            success=True, video=_TEST_VIDEO_INFO, message=""
        )

        with patch(
            "app.services.video.video_service.VideoService.get_video",
            new=AsyncMock(return_value=mock_response),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(f"/videos/{TEST_VIDEO_ID}")

                assert response.status_code == 200
                data = response.json()
                assert data["video"]["metadata"]["width"] == 1920
                assert data["video"]["metadata"]["height"] == 1080
                assert data["video"]["metadata"]["file_size"] == 1024000
                assert data["video"]["metadata"]["format"] == VideoFormat.MP4
                assert data["video"]["metadata"]["duration"] == 60.5
                assert data["video"]["metadata"]["fps"] == 30.0
                assert data["video"]["metadata"]["bitrate"] == 128000

    @pytest.mark.asyncio
    async def test_get_video_not_found(self):
        """Test retrieving a video that doesn't exist"""
        mock_response = GetVideoResponse(
            success=False, video=None, message="Video not found"
        )

        with patch(
            "app.services.video.video_service.VideoService.get_video",
            new=AsyncMock(return_value=mock_response),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/videos/nonexistent-id")

                # Should return 404 error
                assert response.status_code == 404
                data = response.json()
                assert "detail" in data
                assert "Video not found" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_video_invalid_id_format(self):
        """Test retrieving a video with invalid ID format"""
        mock_response = GetVideoResponse(
            success=False, video=None, message="Invalid document ID format"
        )

        with patch(
            "app.services.video.video_service.VideoService.get_video",
            new=AsyncMock(return_value=mock_response),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/videos/invalid-id-123")

                # Should return 404 error
                assert response.status_code == 404
                data = response.json()
                assert "detail" in data
                assert "Invalid document ID format" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_video_with_entity_relationship(self):
        """Test retrieving a video with entity relationships"""
        test_plant_id = "65a1b2c3d4e5f6a7b8c9d0e1"  # Valid MongoDB ObjectId
        video_with_entity = VideoInfo(
            id=TEST_VIDEO_ID_2,
            filename="plant_video.mp4",
            storage_path="videos/plants/plant_video.mp4",
            storage_url="https://storage.example.com/videos/plants/plant_video.mp4",
            video_type=VideoType.GENERAL,
            source_type=VideoSourceType.UPLOAD,
            entity_id=test_plant_id,
            entity_type="plant",
            metadata=VideoMetadata(width=1280, height=720),
            processing_status=MediaProcessingStatus.COMPLETED,
            uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
            tags=["plant", "nature"],
            is_deleted=False,
        )

        mock_response = GetVideoResponse(
            success=True, video=video_with_entity, message=""
        )

        with patch(
            "app.services.video.video_service.VideoService.get_video",
            new=AsyncMock(return_value=mock_response),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(f"/videos/{TEST_VIDEO_ID_2}")

                assert response.status_code == 200
                data = response.json()
                assert data["video"]["entity_id"] == test_plant_id
                assert data["video"]["entity_type"] == "plant"
                assert data["video"]["tags"] == ["plant", "nature"]

    @pytest.mark.asyncio
    async def test_get_video_service_exception(self):
        """Test get video when service raises an exception"""
        with patch(
            "app.services.video.video_service.VideoService.get_video",
            new=AsyncMock(side_effect=Exception("Database error")),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                # FastAPI will propagate the exception
                with pytest.raises(Exception, match="Database error"):
                    await ac.get(f"/videos/{TEST_VIDEO_ID}")

    @pytest.mark.asyncio
    async def test_get_video_different_processing_status(self):
        """Test retrieving videos with different processing statuses"""
        statuses = [
            MediaProcessingStatus.PENDING,
            MediaProcessingStatus.PROCESSING,
            MediaProcessingStatus.COMPLETED,
            MediaProcessingStatus.FAILED,
        ]

        for status in statuses:
            video_info = VideoInfo(
                id=TEST_VIDEO_ID,
                filename="test.mp4",
                storage_path="videos/test.mp4",
                video_type=VideoType.GENERAL,
                source_type=VideoSourceType.UPLOAD,
                metadata=VideoMetadata(),
                processing_status=status,
                uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
                updated_at=datetime(2024, 1, 1, 12, 0, 0),
                is_deleted=False,
            )

            mock_response = GetVideoResponse(
                success=True, video=video_info, message=""
            )

            with patch(
                "app.services.video.video_service.VideoService.get_video",
                new=AsyncMock(return_value=mock_response),
            ):
                transport = ASGITransport(app=app)
                async with AsyncClient(
                    transport=transport, base_url="http://test"
                ) as ac:
                    response = await ac.get(f"/videos/{TEST_VIDEO_ID}")

                    assert response.status_code == 200
                    data = response.json()
                    assert data["video"]["processing_status"] == status

    @pytest.mark.asyncio
    async def test_get_video_deleted_video(self):
        """Test retrieving a soft-deleted video"""
        deleted_video = VideoInfo(
            id=TEST_VIDEO_ID,
            filename="deleted.mp4",
            storage_path="videos/deleted.mp4",
            video_type=VideoType.GENERAL,
            source_type=VideoSourceType.UPLOAD,
            metadata=VideoMetadata(),
            processing_status=MediaProcessingStatus.COMPLETED,
            uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
            is_deleted=True,
        )

        mock_response = GetVideoResponse(
            success=True, video=deleted_video, message=""
        )

        with patch(
            "app.services.video.video_service.VideoService.get_video",
            new=AsyncMock(return_value=mock_response),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(f"/videos/{TEST_VIDEO_ID}")

                assert response.status_code == 200
                data = response.json()
                assert data["video"]["is_deleted"] is True


class TestVideoApiListVideos:
    """Test cases for the list videos endpoint"""

    @pytest.mark.asyncio
    async def test_list_videos_success_default_params(self):
        """Test successfully listing videos with default parameters"""
        video_info_1 = VideoInfo(
            id=TEST_VIDEO_ID,
            filename="video1.mp4",
            storage_path="videos/video1.mp4",
            video_type=VideoType.GENERAL,
            source_type=VideoSourceType.UPLOAD,
            metadata=VideoMetadata(),
            processing_status=MediaProcessingStatus.COMPLETED,
            uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
            is_deleted=False,
        )
        
        video_info_2 = VideoInfo(
            id=TEST_VIDEO_ID_2,
            filename="video2.mp4",
            storage_path="videos/video2.mp4",
            video_type=VideoType.GENERAL,
            source_type=VideoSourceType.UPLOAD,
            metadata=VideoMetadata(),
            processing_status=MediaProcessingStatus.COMPLETED,
            uploaded_at=datetime(2024, 1, 2, 12, 0, 0),
            updated_at=datetime(2024, 1, 2, 12, 0, 0),
            is_deleted=False,
        )

        mock_response = VideoListResponse(
            videos=[video_info_1, video_info_2],
            total=2,
            page=1,
            page_size=10,
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {"page": 1, "page_size": 10}
                response = await ac.post("/videos/list", json=request_data)

                # Verify the service was called
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert isinstance(call_args, VideoListRequest)
                assert call_args.page == 1
                assert call_args.page_size == 10
                assert call_args.video_type is None
                assert call_args.entity_id is None
                assert call_args.entity_type is None
                assert call_args.include_deleted is False

                # Verify the response
                assert response.status_code == 200
                data = response.json()
                assert len(data["videos"]) == 2
                assert data["total"] == 2
                assert data["page"] == 1
                assert data["page_size"] == 10
                assert data["videos"][0]["id"] == TEST_VIDEO_ID
                assert data["videos"][1]["id"] == TEST_VIDEO_ID_2

    @pytest.mark.asyncio
    async def test_list_videos_empty_result(self):
        """Test listing videos when no videos exist"""
        mock_response = VideoListResponse(
            videos=[],
            total=0,
            page=1,
            page_size=10,
        )

        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=AsyncMock(return_value=mock_response),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {"page": 1, "page_size": 10}
                response = await ac.post("/videos/list", json=request_data)

                assert response.status_code == 200
                data = response.json()
                assert len(data["videos"]) == 0
                assert data["total"] == 0
                assert data["page"] == 1
                assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_list_videos_with_pagination(self):
        """Test listing videos with custom pagination parameters"""
        mock_videos = [
            VideoInfo(
                id=f"507f1f77bcf86cd79943901{i}",
                filename=f"video{i}.mp4",
                storage_path=f"videos/video{i}.mp4",
                video_type=VideoType.GENERAL,
                source_type=VideoSourceType.UPLOAD,
                metadata=VideoMetadata(),
                processing_status=MediaProcessingStatus.COMPLETED,
                uploaded_at=datetime(2024, 1, i, 12, 0, 0),
                updated_at=datetime(2024, 1, i, 12, 0, 0),
                is_deleted=False,
            )
            for i in range(1, 6)  # 5 videos
        ]

        mock_response = VideoListResponse(
            videos=mock_videos,
            total=25,  # Total of 25 videos in the system
            page=2,
            page_size=5,
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {"page": 2, "page_size": 5}
                response = await ac.post("/videos/list", json=request_data)

                # Verify the service was called with correct pagination
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert call_args.page == 2
                assert call_args.page_size == 5

                assert response.status_code == 200
                data = response.json()
                assert len(data["videos"]) == 5
                assert data["total"] == 25
                assert data["page"] == 2
                assert data["page_size"] == 5

    @pytest.mark.asyncio
    async def test_list_videos_filter_by_video_type(self):
        """Test listing videos filtered by video_type"""
        mock_videos = [
            VideoInfo(
                id=TEST_VIDEO_ID,
                filename="tutorial.mp4",
                storage_path="videos/tutorial.mp4",
                video_type=VideoType.GENERAL,
                source_type=VideoSourceType.UPLOAD,
                metadata=VideoMetadata(),
                processing_status=MediaProcessingStatus.COMPLETED,
                uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
                updated_at=datetime(2024, 1, 1, 12, 0, 0),
                is_deleted=False,
            ),
        ]

        mock_response = VideoListResponse(
            videos=mock_videos,
            total=1,
            page=1,
            page_size=10,
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {
                    "page": 1,
                    "page_size": 10,
                    "video_type": VideoType.GENERAL,
                }
                response = await ac.post("/videos/list", json=request_data)

                # Verify the service was called with video_type filter
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert call_args.video_type == VideoType.GENERAL

                assert response.status_code == 200
                data = response.json()
                assert len(data["videos"]) == 1
                assert data["videos"][0]["video_type"] == VideoType.GENERAL

    @pytest.mark.asyncio
    async def test_list_videos_filter_by_entity(self):
        """Test listing videos filtered by entity_id and entity_type"""
        test_plant_id = "65a1b2c3d4e5f6a7b8c9d0e1"
        
        mock_videos = [
            VideoInfo(
                id=TEST_VIDEO_ID,
                filename="plant_video.mp4",
                storage_path="videos/plants/plant_video.mp4",
                video_type=VideoType.GENERAL,
                source_type=VideoSourceType.UPLOAD,
                entity_id=test_plant_id,
                entity_type="plant",
                metadata=VideoMetadata(),
                processing_status=MediaProcessingStatus.COMPLETED,
                uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
                updated_at=datetime(2024, 1, 1, 12, 0, 0),
                is_deleted=False,
            ),
        ]

        mock_response = VideoListResponse(
            videos=mock_videos,
            total=1,
            page=1,
            page_size=10,
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {
                    "page": 1,
                    "page_size": 10,
                    "entity_id": test_plant_id,
                    "entity_type": "plant",
                }
                response = await ac.post("/videos/list", json=request_data)

                # Verify the service was called with entity filters
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert call_args.entity_id == test_plant_id
                assert call_args.entity_type == "plant"

                assert response.status_code == 200
                data = response.json()
                assert len(data["videos"]) == 1
                assert data["videos"][0]["entity_id"] == test_plant_id
                assert data["videos"][0]["entity_type"] == "plant"

    @pytest.mark.asyncio
    async def test_list_videos_include_deleted(self):
        """Test listing videos including soft-deleted videos"""
        mock_videos = [
            VideoInfo(
                id=TEST_VIDEO_ID,
                filename="active.mp4",
                storage_path="videos/active.mp4",
                video_type=VideoType.GENERAL,
                source_type=VideoSourceType.UPLOAD,
                metadata=VideoMetadata(),
                processing_status=MediaProcessingStatus.COMPLETED,
                uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
                updated_at=datetime(2024, 1, 1, 12, 0, 0),
                is_deleted=False,
            ),
            VideoInfo(
                id=TEST_VIDEO_ID_2,
                filename="deleted.mp4",
                storage_path="videos/deleted.mp4",
                video_type=VideoType.GENERAL,
                source_type=VideoSourceType.UPLOAD,
                metadata=VideoMetadata(),
                processing_status=MediaProcessingStatus.COMPLETED,
                uploaded_at=datetime(2024, 1, 2, 12, 0, 0),
                updated_at=datetime(2024, 1, 2, 12, 0, 0),
                is_deleted=True,
            ),
        ]

        mock_response = VideoListResponse(
            videos=mock_videos,
            total=2,
            page=1,
            page_size=10,
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {
                    "page": 1,
                    "page_size": 10,
                    "include_deleted": True,
                }
                response = await ac.post("/videos/list", json=request_data)

                # Verify the service was called with include_deleted flag
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert call_args.include_deleted is True

                assert response.status_code == 200
                data = response.json()
                assert len(data["videos"]) == 2
                assert data["videos"][0]["is_deleted"] is False
                assert data["videos"][1]["is_deleted"] is True

    @pytest.mark.asyncio
    async def test_list_videos_multiple_filters(self):
        """Test listing videos with multiple filters applied"""
        test_plant_id = "65a1b2c3d4e5f6a7b8c9d0e1"
        
        mock_videos = [
            VideoInfo(
                id=TEST_VIDEO_ID,
                filename="plant_general.mp4",
                storage_path="videos/plants/plant_general.mp4",
                video_type=VideoType.GENERAL,
                source_type=VideoSourceType.UPLOAD,
                entity_id=test_plant_id,
                entity_type="plant",
                metadata=VideoMetadata(),
                processing_status=MediaProcessingStatus.COMPLETED,
                uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
                updated_at=datetime(2024, 1, 1, 12, 0, 0),
                is_deleted=False,
            ),
        ]

        mock_response = VideoListResponse(
            videos=mock_videos,
            total=1,
            page=1,
            page_size=10,
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {
                    "page": 1,
                    "page_size": 10,
                    "video_type": VideoType.GENERAL,
                    "entity_id": test_plant_id,
                    "entity_type": "plant",
                    "include_deleted": False,
                }
                response = await ac.post("/videos/list", json=request_data)

                # Verify all filters were passed
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert call_args.video_type == VideoType.GENERAL
                assert call_args.entity_id == test_plant_id
                assert call_args.entity_type == "plant"
                assert call_args.include_deleted is False

                assert response.status_code == 200
                data = response.json()
                assert len(data["videos"]) == 1

    @pytest.mark.asyncio
    async def test_list_videos_service_exception(self):
        """Test list videos when service raises an exception"""
        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=AsyncMock(side_effect=Exception("Database connection error")),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {"page": 1, "page_size": 10}
                response = await ac.post("/videos/list", json=request_data)

                # Should return 400 error with detail message
                assert response.status_code == 400
                data = response.json()
                assert "detail" in data
                assert "Error listing videos" in data["detail"]
                assert "Database connection error" in data["detail"]

    @pytest.mark.asyncio
    async def test_list_videos_with_complete_metadata(self):
        """Test listing videos that include complete metadata"""
        video_with_full_metadata = VideoInfo(
            id=TEST_VIDEO_ID,
            filename="full_metadata.mp4",
            original_filename="original_full.mp4",
            title="Video with Full Metadata",
            description="This video has all metadata fields",
            alt_text="Full metadata video",
            storage_path=TEST_STORAGE_PATH,
            storage_url=TEST_STORAGE_URL,
            video_type=VideoType.GENERAL,
            source_type=VideoSourceType.UPLOAD,
            metadata=_TEST_VIDEO_METADATA,
            processing_status=MediaProcessingStatus.COMPLETED,
            uploaded_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
            processed_at=datetime(2024, 1, 1, 12, 5, 0),
            tags=["test", "metadata", "complete"],
            is_deleted=False,
        )

        mock_response = VideoListResponse(
            videos=[video_with_full_metadata],
            total=1,
            page=1,
            page_size=10,
        )

        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=AsyncMock(return_value=mock_response),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {"page": 1, "page_size": 10}
                response = await ac.post("/videos/list", json=request_data)

                assert response.status_code == 200
                data = response.json()
                assert len(data["videos"]) == 1
                video = data["videos"][0]
                assert video["title"] == "Video with Full Metadata"
                assert video["description"] == "This video has all metadata fields"
                assert video["alt_text"] == "Full metadata video"
                assert video["metadata"]["width"] == 1920
                assert video["metadata"]["height"] == 1080
                assert video["metadata"]["duration"] == 60.5
                assert video["metadata"]["fps"] == 30.0
                assert video["tags"] == ["test", "metadata", "complete"]

    @pytest.mark.asyncio
    async def test_list_videos_different_processing_statuses(self):
        """Test listing videos with various processing statuses"""
        mock_videos = [
            VideoInfo(
                id=f"507f1f77bcf86cd79943901{i}",
                filename=f"video_{status}.mp4",
                storage_path=f"videos/video_{status}.mp4",
                video_type=VideoType.GENERAL,
                source_type=VideoSourceType.UPLOAD,
                metadata=VideoMetadata(),
                processing_status=status,
                uploaded_at=datetime(2024, 1, i, 12, 0, 0),
                updated_at=datetime(2024, 1, i, 12, 0, 0),
                is_deleted=False,
            )
            for i, status in enumerate([
                MediaProcessingStatus.PENDING,
                MediaProcessingStatus.PROCESSING,
                MediaProcessingStatus.COMPLETED,
                MediaProcessingStatus.FAILED,
            ], start=1)
        ]

        mock_response = VideoListResponse(
            videos=mock_videos,
            total=4,
            page=1,
            page_size=10,
        )

        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=AsyncMock(return_value=mock_response),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {"page": 1, "page_size": 10}
                response = await ac.post("/videos/list", json=request_data)

                assert response.status_code == 200
                data = response.json()
                assert len(data["videos"]) == 4
                assert data["videos"][0]["processing_status"] == MediaProcessingStatus.PENDING
                assert data["videos"][1]["processing_status"] == MediaProcessingStatus.PROCESSING
                assert data["videos"][2]["processing_status"] == MediaProcessingStatus.COMPLETED
                assert data["videos"][3]["processing_status"] == MediaProcessingStatus.FAILED

    @pytest.mark.asyncio
    async def test_list_videos_page_zero(self):
        """Test listing videos with page number 0 (edge case)"""
        mock_response = VideoListResponse(
            videos=[],
            total=10,
            page=0,
            page_size=10,
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {"page": 0, "page_size": 10}
                response = await ac.post("/videos/list", json=request_data)

                # Verify the service was called with page 0
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert call_args.page == 0

                assert response.status_code == 200
                data = response.json()
                assert data["page"] == 0
                assert data["total"] == 10

    @pytest.mark.asyncio
    async def test_list_videos_negative_page_number(self):
        """Test listing videos with negative page number (edge case)"""
        mock_response = VideoListResponse(
            videos=[],
            total=10,
            page=-1,
            page_size=10,
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {"page": -1, "page_size": 10}
                response = await ac.post("/videos/list", json=request_data)

                # Verify the service was called with negative page
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert call_args.page == -1

                assert response.status_code == 200
                data = response.json()
                assert data["page"] == -1
                assert data["total"] == 10

    @pytest.mark.asyncio
    async def test_list_videos_page_exceeds_total_pages(self):
        """Test listing videos when requested page exceeds total available pages"""
        # Total of 15 videos, page_size 10 = 2 pages
        # Request page 5 which is beyond available pages
        mock_response = VideoListResponse(
            videos=[],  # No videos on this page
            total=15,
            page=5,
            page_size=10,
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {"page": 5, "page_size": 10}
                response = await ac.post("/videos/list", json=request_data)

                # Verify the service was called
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert call_args.page == 5
                assert call_args.page_size == 10

                # Should return 200 with empty list but correct metadata
                assert response.status_code == 200
                data = response.json()
                assert len(data["videos"]) == 0
                assert data["total"] == 15  # Total count is still accurate
                assert data["page"] == 5
                assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_list_videos_very_large_page_number(self):
        """Test listing videos with extremely large page number"""
        mock_response = VideoListResponse(
            videos=[],
            total=10,
            page=999999,
            page_size=10,
        )

        mock_service = AsyncMock(return_value=mock_response)
        with patch(
            "app.services.video.video_service.VideoService.list_videos",
            new=mock_service,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                request_data = {"page": 999999, "page_size": 10}
                response = await ac.post("/videos/list", json=request_data)

                # Verify the service was called
                mock_service.assert_called_once()
                call_args = mock_service.call_args[0][0]
                assert call_args.page == 999999

                # Should return 200 with empty list
                assert response.status_code == 200
                data = response.json()
                assert len(data["videos"]) == 0
                assert data["page"] == 999999
                assert data["total"] == 10
