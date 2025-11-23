import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock
from datetime import datetime

from app.api.job_api import router
from app.classes.job import (
    JobType,
    CreateJobResponse,
    GetJobResponse,
    UpdateJobResponse,
    JobListResponse,
    JobInfo,
    JobStatus,
    JobPriority,
    JobProgress,
    JobResult,
)

# Test constants
TEST_JOB_ID = "67206999f3949388f3a80900"
TEST_JOB_ID_2 = "67206999f3949388f3a80901"

app = FastAPI()
app.include_router(router, prefix="/jobs")


@pytest.fixture
def mock_job_pending():
    """Mock job in PENDING status"""
    return JobInfo(
        id=TEST_JOB_ID,
        job_type=JobType.VIDEO_PROCESSING,
        job_name="process_video",
        status=JobStatus.PENDING,
        priority=JobPriority.NORMAL,
        metadata={"resolution": "1080p"},
        entity_id="video_123",
        entity_type="video",
        created_at=datetime.utcnow(),
        started_at=None,
        completed_at=None,
        expires_at=datetime.utcnow(),
        retries=0,
        max_retries=3,
        retry_delay=None,
        progress=None,
        result=None
    )


@pytest.fixture
def mock_job_success():
    """Mock job in SUCCESS status"""
    return JobInfo(
        id=TEST_JOB_ID_2,
        job_type=JobType.IMAGE_PROCESSING,
        job_name="process_image",
        status=JobStatus.SUCCESS,
        priority=JobPriority.HIGH,
        metadata={},
        entity_id="image_456",
        entity_type="image",
        created_at=datetime.utcnow(),
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        expires_at=datetime.utcnow(),
        retries=0,
        max_retries=3,
        retry_delay=None,
        progress=None,
        result=None
    )


class TestJobApiCreate:
    
    @pytest.mark.asyncio
    async def test_create_job(self):
        """Test creating a new job"""
        mock_response = CreateJobResponse(
            success=True,
            job_id=TEST_JOB_ID,
            message=""
        )
        
        with patch("app.services.job.job_service.JobService.create_job", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/jobs/",
                    json={
                        "job_type": JobType.VIDEO_PROCESSING.value,
                        "job_name": "process_video_task",
                        "entity_id": "test_video_123",
                        "entity_type": "video",
                        "metadata": {
                            "video_url": "https://example.com/video.mp4",
                            "resolution": "1080p"
                        }
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "job_id" in data
                assert data["job_id"] == TEST_JOB_ID
                assert data["message"] == ""

    @pytest.mark.asyncio
    async def test_create_job_missing_required_field(self):
        """Test creating a job with missing required fields"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Missing job_name
            response = await ac.post(
                "/jobs/",
                json={
                    "job_type": JobType.IMAGE_PROCESSING.value,
                    "job_name": "",
                }
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "job_name" in data["detail"].lower()


class TestJobApiGet:
    
    @pytest.mark.asyncio
    async def test_get_job(self, mock_job_pending):
        """Test retrieving a job by ID"""
        mock_response = GetJobResponse(
            success=True,
            job=mock_job_pending,
            message="Job retrieved successfully."
        )
        
        with patch("app.services.job.job_service.JobService.get_job", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                # Now retrieve the job
                get_response = await ac.get(f"/jobs/{TEST_JOB_ID}")
                
                assert get_response.status_code == 200
                data = get_response.json()
                assert data["success"] is True
                assert data["job"] is not None
                assert data["job"]["id"] == TEST_JOB_ID
                assert data["job"]["job_type"] == JobType.VIDEO_PROCESSING.value
                assert data["job"]["job_name"] == "process_video"
                assert data["job"]["status"] == "pending"
                assert data["job"]["metadata"]["resolution"] == "1080p"

    @pytest.mark.asyncio
    async def test_get_nonexistent_job(self):
        """Test retrieving a job that doesn't exist"""
        mock_response = GetJobResponse(
            success=False,
            job=None,
            message=f"Job not found: {TEST_JOB_ID}"
        )
        
        with patch("app.services.job.job_service.JobService.get_job", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                # Use a valid UUID format that doesn't exist
                response = await ac.get(f"/jobs/{TEST_JOB_ID}")
                
                assert response.status_code == 404
                data = response.json()
                assert "not found" in data["detail"].lower()


class TestJobApiUpdate:
    
    @pytest.mark.asyncio
    async def test_update_job_success(self):
        """Test successfully updating a job"""
        mock_response = UpdateJobResponse(
            success=True,
            job_id=TEST_JOB_ID,
            message=""
        )
        
        with patch("app.services.job.job_service.JobService.update_job", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put(
                    f"/jobs/{TEST_JOB_ID}",
                    json={
                        "job_name": "updated_job_name",
                        "status": JobStatus.SUCCESS.value,
                        "priority": JobPriority.HIGH.value,
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["job_id"] == TEST_JOB_ID
                assert data["message"] == ""

    @pytest.mark.asyncio
    async def test_update_job_with_progress(self):
        """Test updating a job with progress information"""
        mock_response = UpdateJobResponse(
            success=True,
            job_id=TEST_JOB_ID,
            message=""
        )
        
        with patch("app.services.job.job_service.JobService.update_job", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put(
                    f"/jobs/{TEST_JOB_ID}",
                    json={
                        "status": JobStatus.PROGRESS.value,
                        "progress": {
                            "current": 50,
                            "total": 100,
                            "message": "Processing frame 50/100"
                        }
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["job_id"] == TEST_JOB_ID

    @pytest.mark.asyncio
    async def test_update_job_with_result(self):
        """Test updating a job with result information"""
        mock_response = UpdateJobResponse(
            success=True,
            job_id=TEST_JOB_ID,
            message=""
        )
        
        with patch("app.services.job.job_service.JobService.update_job", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put(
                    f"/jobs/{TEST_JOB_ID}",
                    json={
                        "status": JobStatus.SUCCESS.value,
                        "result": {
                            "success": True,
                            "data": {"output_url": "https://example.com/output.mp4"},
                            "message": "Video processed successfully"
                        }
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["job_id"] == TEST_JOB_ID

    @pytest.mark.asyncio
    async def test_update_job_with_metadata(self):
        """Test updating a job with metadata"""
        mock_response = UpdateJobResponse(
            success=True,
            job_id=TEST_JOB_ID,
            message=""
        )
        
        with patch("app.services.job.job_service.JobService.update_job", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put(
                    f"/jobs/{TEST_JOB_ID}",
                    json={
                        "metadata": {
                            "resolution": "4K",
                            "fps": 60,
                            "codec": "h265"
                        }
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True

    @pytest.mark.asyncio
    async def test_update_job_not_found(self):
        """Test updating a job that doesn't exist"""
        mock_response = UpdateJobResponse(
            success=False,
            job_id=TEST_JOB_ID,
            message=f"Job not found: {TEST_JOB_ID}"
        )
        
        with patch("app.services.job.job_service.JobService.update_job", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put(
                    f"/jobs/{TEST_JOB_ID}",
                    json={"job_name": "new_name"}
                )
                
                assert response.status_code == 400
                data = response.json()
                assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_job_empty_job_name(self):
        """Test updating a job with empty job_name"""
        mock_response = UpdateJobResponse(
            success=False,
            job_id=TEST_JOB_ID,
            message="Job name cannot be empty"
        )
        
        with patch("app.services.job.job_service.JobService.update_job", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put(
                    f"/jobs/{TEST_JOB_ID}",
                    json={"job_name": ""}
                )
                
                assert response.status_code == 400
                data = response.json()
                assert "cannot be empty" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_job_no_fields(self):
        """Test updating a job with no fields (should succeed with no changes)"""
        mock_response = UpdateJobResponse(
            success=True,
            job_id=TEST_JOB_ID,
            message="No fields to update"
        )
        
        with patch("app.services.job.job_service.JobService.update_job", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put(
                    f"/jobs/{TEST_JOB_ID}",
                    json={}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "no fields" in data["message"].lower()


class TestJobApiListJobs:
    
    @pytest.mark.asyncio
    async def test_list_jobs_success(self, mock_job_pending, mock_job_success):
        """Test successfully listing jobs"""
        mock_response = JobListResponse(
            jobs=[mock_job_pending, mock_job_success],
            total=2,
            page=1,
            page_size=20
        )
        
        with patch("app.services.job.job_service.JobService.list_jobs", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/jobs/list",
                    json={
                        "page": 1,
                        "page_size": 20
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "jobs" in data
                assert len(data["jobs"]) == 2
                assert data["total"] == 2
                assert data["page"] == 1
                assert data["page_size"] == 20
                assert data["jobs"][0]["id"] == TEST_JOB_ID
                assert data["jobs"][0]["job_type"] == JobType.VIDEO_PROCESSING.value
                assert data["jobs"][1]["id"] == TEST_JOB_ID_2
                assert data["jobs"][1]["status"] == JobStatus.SUCCESS.value

    @pytest.mark.asyncio
    async def test_list_jobs_empty(self):
        """Test listing jobs with no results"""
        mock_response = JobListResponse(
            jobs=[],
            total=0,
            page=1,
            page_size=20
        )
        
        with patch("app.services.job.job_service.JobService.list_jobs", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/jobs/list",
                    json={
                        "page": 1,
                        "page_size": 20
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["jobs"] == []
                assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_jobs_with_all_filters(self, mock_job_pending):
        """Test listing jobs with all filters combined"""
        # Create a modified version with HIGH priority for this test
        mock_job = mock_job_pending.model_copy(update={
            "priority": JobPriority.HIGH,
            "metadata": {"resolution": "4K"}
        })
        
        mock_response = JobListResponse(
            jobs=[mock_job],
            total=1,
            page=1,
            page_size=20
        )
        
        with patch("app.services.job.job_service.JobService.list_jobs", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/jobs/list",
                    json={
                        "page": 1,
                        "page_size": 20,
                        "job_type": JobType.VIDEO_PROCESSING.value,
                        "status": JobStatus.PENDING.value,
                        "entity_id": "video_123",
                        "entity_type": "video",
                        "priority": JobPriority.HIGH.value
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert len(data["jobs"]) == 1
                assert data["jobs"][0]["job_type"] == JobType.VIDEO_PROCESSING.value
                assert data["jobs"][0]["status"] == JobStatus.PENDING.value
                assert data["jobs"][0]["priority"] == JobPriority.HIGH.value

    @pytest.mark.asyncio
    async def test_list_jobs_pagination(self, mock_job_pending):
        """Test listing jobs with pagination"""
        mock_jobs = [
            mock_job_pending.model_copy(update={"id": f"job_id_{i}"})
            for i in range(10)
        ]
        
        mock_response = JobListResponse(
            jobs=mock_jobs,
            total=50,
            page=2,
            page_size=10
        )
        
        with patch("app.services.job.job_service.JobService.list_jobs", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/jobs/list",
                    json={
                        "page": 2,
                        "page_size": 10
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert len(data["jobs"]) == 10
                assert data["total"] == 50
                assert data["page"] == 2
                assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_list_jobs_default_values(self):
        """Test listing jobs with default pagination values"""
        mock_response = JobListResponse(
            jobs=[],
            total=0,
            page=1,
            page_size=20
        )
        
        with patch("app.services.job.job_service.JobService.list_jobs", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/jobs/list",
                    json={}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["page"] == 1
                assert data["page_size"] == 20

    @pytest.mark.asyncio
    async def test_list_jobs_exception(self):
        """Test listing jobs with an exception"""
        with patch("app.services.job.job_service.JobService.list_jobs", new=AsyncMock(side_effect=Exception("Database error"))):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/jobs/list",
                    json={
                        "page": 1,
                        "page_size": 20
                    }
                )
                
                assert response.status_code == 400
                data = response.json()
                assert "error listing jobs" in data["detail"].lower()
                assert "database error" in data["detail"].lower()
