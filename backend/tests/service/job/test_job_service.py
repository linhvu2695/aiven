import pytest
from datetime import datetime, timezone
from bson import ObjectId
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.job.job_service import JobService
from app.classes.job import (
    CreateJobRequest,
    CreateJobResponse,
    GetJobResponse,
    JobType,
    JobStatus,
    JobPriority,
)

# Test constants
TEST_JOB_ID = "67206999f3949388f3a80900"
TEST_JOB_ID_2 = "67206999f3949388f3a80901"


@pytest.fixture
def job_service():
    """Create a fresh instance for each test"""
    # Reset the singleton instance
    JobService._instance = None
    return JobService()


@pytest.fixture
def create_job_request():
    """Create a standard job request for testing"""
    return CreateJobRequest(
        job_type=JobType.VIDEO_PROCESSING,
        job_name="process_video",
        priority=JobPriority.NORMAL,
        entity_id="video_123",
        entity_type="video",
        metadata={"resolution": "1080p"}
    )


@pytest.fixture
def mock_job_document():
    """Mock job document from database"""
    return {
        "_id": ObjectId(TEST_JOB_ID),
        "job_type": JobType.VIDEO_PROCESSING.value,
        "job_name": "process_video",
        "status": JobStatus.PENDING.value,
        "priority": JobPriority.NORMAL.value,
        "metadata": {"resolution": "1080p"},
        "entity_id": "video_123",
        "entity_type": "video",
        "created_at": datetime.now(timezone.utc),
        "started_at": None,
        "completed_at": None,
        "expires_at": datetime.now(timezone.utc),
        "retries": 0,
        "max_retries": 3,
        "retry_delay": None,
        "progress": None,
        "result": None,
    }


class TestJobServiceSingleton:
    
    def test_singleton_instance(self):
        """Test that JobService is a singleton"""
        service1 = JobService()
        service2 = JobService()
        assert service1 is service2


class TestJobServiceValidation:

    def test_validate_create_job_request_valid(self, job_service: JobService, create_job_request: CreateJobRequest):
        """Test validation with valid request"""
        valid, error_msg = job_service._validate_create_job_request(create_job_request)
        assert valid is True
        assert error_msg == ""

    def test_validate_create_job_request_missing_job_name(self, job_service: JobService):
        """Test validation with missing job_name"""
        request = CreateJobRequest(
            job_type=JobType.GENERAL,
            job_name="",  # Empty string
        )
        
        valid, error_msg = job_service._validate_create_job_request(request)
        assert valid is False
        assert "job_name" in error_msg.lower()

    def test_validate_create_job_request_whitespace_job_name(self, job_service: JobService):
        """Test validation with whitespace-only job_name"""
        request = CreateJobRequest(
            job_type=JobType.GENERAL,
            job_name="   ",  # Whitespace only
        )
        
        valid, error_msg = job_service._validate_create_job_request(request)
        assert valid is False
        assert "job_name" in error_msg.lower()


class TestJobServiceCreateJob:

    @pytest.mark.asyncio
    async def test_create_job_success(self, job_service: JobService, create_job_request: CreateJobRequest):
        """Test successfully creating a job"""
        with patch("app.services.job.job_service.insert_document", return_value=TEST_JOB_ID):
            response = await job_service.create_job(create_job_request)
            
            assert isinstance(response, CreateJobResponse)
            assert response.success is True
            assert response.job_id == TEST_JOB_ID
            assert response.message == ""

    @pytest.mark.asyncio
    async def test_create_job_validation_failure(self, job_service: JobService):
        """Test job creation with validation failure"""
        invalid_request = CreateJobRequest(
            job_type=JobType.GENERAL,
            job_name="",  # Invalid empty name
        )
        
        response = await job_service.create_job(invalid_request)
        
        assert isinstance(response, CreateJobResponse)
        assert response.success is False
        assert response.job_id == ""
        assert "job_name" in response.message.lower()

    @pytest.mark.asyncio
    async def test_create_job_database_insert_failure(self, job_service: JobService, create_job_request: CreateJobRequest):
        """Test job creation when database insert fails"""
        with patch("app.services.job.job_service.insert_document", side_effect=Exception("DB Error")):
            response = await job_service.create_job(create_job_request)
            
            assert isinstance(response, CreateJobResponse)
            assert response.success is False
            assert response.job_id == ""
            assert "Failed to create job: DB Error" in response.message

    @pytest.mark.asyncio
    async def test_create_job_empty_inserted_id(self, job_service: JobService, create_job_request: CreateJobRequest):
        """Test job creation when insert_document returns empty string"""
        with patch("app.services.job.job_service.insert_document", return_value=""):
            response = await job_service.create_job(create_job_request)
            
            assert isinstance(response, CreateJobResponse)
            assert response.success is False
            assert response.job_id == ""
            assert "Failed to insert document" in response.message

    @pytest.mark.asyncio
    async def test_create_job_with_minimal_fields(self, job_service: JobService):
        """Test creating a job with only required fields"""
        request = CreateJobRequest(
            job_type=JobType.GENERAL,
            job_name="simple_task"
        )
        
        with patch("app.services.job.job_service.insert_document", return_value=TEST_JOB_ID) as mock_insert:
            response = await job_service.create_job(request)
            
            assert response.success is True
            assert response.job_id == TEST_JOB_ID
            
            # Verify document was created with defaults
            document = mock_insert.call_args[0][1]
            assert document["job_name"] == "simple_task"
            assert document["status"] == JobStatus.PENDING.value
            assert document["priority"] == JobPriority.NORMAL.value
            assert document["metadata"] == {}
            assert document["entity_id"] is None
            assert document["entity_type"] is None
            assert document["retries"] == 0
            assert document["max_retries"] == 3

    @pytest.mark.asyncio
    async def test_create_job_with_all_fields(self, job_service: JobService, create_job_request: CreateJobRequest):
        """Test creating a job with all fields populated"""
        with patch("app.services.job.job_service.insert_document", return_value=TEST_JOB_ID) as mock_insert:
            response = await job_service.create_job(create_job_request)
            
            assert response.success is True
            assert response.job_id == TEST_JOB_ID
            
            # Verify all fields in document
            document = mock_insert.call_args[0][1]
            assert document["job_type"] == JobType.VIDEO_PROCESSING.value
            assert document["job_name"] == "process_video"
            assert document["priority"] == JobPriority.NORMAL.value
            assert document["entity_id"] == "video_123"
            assert document["entity_type"] == "video"
            assert document["metadata"]["resolution"] == "1080p"

    @pytest.mark.asyncio
    async def test_create_job_sets_timestamps(self, job_service: JobService, create_job_request: CreateJobRequest):
        """Test that create_job sets created_at and expires_at timestamps"""
        with patch("app.services.job.job_service.insert_document", return_value=TEST_JOB_ID) as mock_insert:
            response = await job_service.create_job(create_job_request)
            
            assert response.success is True
            
            # Verify timestamps were set
            document = mock_insert.call_args[0][1]
            assert "created_at" in document
            assert "expires_at" in document
            assert isinstance(document["created_at"], datetime)
            assert isinstance(document["expires_at"], datetime)
            assert document["expires_at"] > document["created_at"]

    @pytest.mark.asyncio
    async def test_create_job_with_different_priorities(self, job_service: JobService):
        """Test creating jobs with different priority levels"""
        priorities = [JobPriority.LOW, JobPriority.NORMAL, JobPriority.HIGH, JobPriority.CRITICAL]
        
        for priority in priorities:
            request = CreateJobRequest(
                job_type=JobType.GENERAL,
                job_name=f"test_job_{priority.name}",
                priority=priority
            )
            
            with patch("app.services.job.job_service.insert_document", return_value=TEST_JOB_ID) as mock_insert:
                response = await job_service.create_job(request)
                
                assert response.success is True
                
                # Verify priority was set correctly
                document = mock_insert.call_args[0][1]
                assert document["priority"] == priority.value


class TestJobServiceGetJob:

    @pytest.mark.asyncio
    async def test_get_job_success(self, job_service: JobService, mock_job_document: dict):
        """Test successful job retrieval"""
        with patch("app.services.job.job_service.get_document", return_value=mock_job_document):
            response = await job_service.get_job(TEST_JOB_ID)
            
            assert isinstance(response, GetJobResponse)
            assert response.success is True
            assert response.job is not None
            assert response.job.id == TEST_JOB_ID
            assert response.job.job_type == JobType.VIDEO_PROCESSING
            assert response.job.job_name == "process_video"
            assert response.job.status == JobStatus.PENDING
            assert response.job.priority == JobPriority.NORMAL
            assert response.job.entity_id == "video_123"
            assert response.job.entity_type == "video"
            assert response.job.metadata["resolution"] == "1080p"
            assert response.job.retries == 0
            assert response.job.max_retries == 3
            assert isinstance(response.job.created_at, datetime)
            assert response.job.expires_at is not None

    @pytest.mark.asyncio
    async def test_get_job_not_found(self, job_service: JobService):
        """Test job retrieval when job is not found"""
        with patch("app.services.job.job_service.get_document", return_value=None):
            response = await job_service.get_job(TEST_JOB_ID)
            
            assert isinstance(response, GetJobResponse)
            assert response.success is False
            assert response.job is None
            assert "not found" in response.message.lower()

    @pytest.mark.asyncio
    async def test_get_job_exception(self, job_service: JobService):
        """Test job retrieval with exception"""
        with patch("app.services.job.job_service.get_document", side_effect=Exception("Database error")):
            response = await job_service.get_job(TEST_JOB_ID)
            
            assert isinstance(response, GetJobResponse)
            assert response.success is False
            assert response.job is None
            assert "Failed to retrieve job" in response.message

    @pytest.mark.asyncio
    async def test_get_job_invalid_id(self, job_service: JobService):
        """Test job retrieval with invalid ID"""
        with patch("app.services.job.job_service.get_document", side_effect=ValueError("Invalid document id format")):
            response = await job_service.get_job("invalid_id")
            
            assert isinstance(response, GetJobResponse)
            assert response.success is False
            assert response.job is None
            assert "Invalid document id format" in response.message

    @pytest.mark.asyncio
    async def test_get_job_empty_id(self, job_service: JobService):
        """Test job retrieval with empty ID"""
        with patch("app.services.job.job_service.get_document", side_effect=ValueError("Invalid document id format")):
            response = await job_service.get_job("")
            
            assert isinstance(response, GetJobResponse)
            assert response.success is False
            assert response.job is None
