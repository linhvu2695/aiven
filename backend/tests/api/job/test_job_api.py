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
    JobInfo,
    JobStatus,
    JobPriority
)

# Test constants
TEST_JOB_ID = "67206999f3949388f3a80900"
TEST_JOB_ID_2 = "67206999f3949388f3a80901"

app = FastAPI()
app.include_router(router, prefix="/jobs")


@pytest.mark.asyncio
async def test_create_job():
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
async def test_create_job_missing_required_field():
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


@pytest.mark.asyncio
async def test_get_job():
    """Test retrieving a job by ID"""
    mock_job = JobInfo(
        id=TEST_JOB_ID_2,
        job_type=JobType.GENERAL,
        job_name="test_task",
        status=JobStatus.PENDING,
        priority=JobPriority.NORMAL,
        metadata={"test": "data"},
        entity_id=None,
        entity_type=None,
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
    
    mock_response = GetJobResponse(
        success=True,
        job=mock_job,
        message="Job retrieved successfully."
    )
    
    with patch("app.services.job.job_service.JobService.get_job", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Now retrieve the job
            get_response = await ac.get(f"/jobs/{TEST_JOB_ID_2}")
            
            assert get_response.status_code == 200
            data = get_response.json()
            assert data["success"] is True
            assert data["job"] is not None
            assert data["job"]["id"] == TEST_JOB_ID_2
            assert data["job"]["job_type"] == JobType.GENERAL.value
            assert data["job"]["job_name"] == "test_task"
            assert data["job"]["status"] == "pending"
            assert data["job"]["metadata"]["test"] == "data"


@pytest.mark.asyncio
async def test_get_nonexistent_job():
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

