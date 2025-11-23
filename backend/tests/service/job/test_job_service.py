import pytest
from datetime import datetime, timezone
from bson import ObjectId
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.job.job_service import JobService
from app.classes.job import (
    CreateJobRequest,
    CreateJobResponse,
    GetJobResponse,
    UpdateJobRequest,
    UpdateJobResponse,
    JobType,
    JobStatus,
    JobPriority,
    JobProgress,
    JobResult,
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
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
            
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
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=None)
            response = await job_service.get_job(TEST_JOB_ID)
            
            assert isinstance(response, GetJobResponse)
            assert response.success is False
            assert response.job is None
            assert "not found" in response.message.lower()

    @pytest.mark.asyncio
    async def test_get_job_exception(self, job_service: JobService):
        """Test job retrieval with exception"""
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(side_effect=Exception("Database error"))
            response = await job_service.get_job(TEST_JOB_ID)
            
            assert isinstance(response, GetJobResponse)
            assert response.success is False
            assert response.job is None
            assert "Failed to retrieve job" in response.message

    @pytest.mark.asyncio
    async def test_get_job_invalid_id(self, job_service: JobService):
        """Test job retrieval with invalid ID"""
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(side_effect=ValueError("Invalid document id format"))
            response = await job_service.get_job("invalid_id")
            
            assert isinstance(response, GetJobResponse)
            assert response.success is False
            assert response.job is None
            assert "Invalid document id format" in response.message

    @pytest.mark.asyncio
    async def test_get_job_empty_id(self, job_service: JobService):
        """Test job retrieval with empty ID"""
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(side_effect=ValueError("Invalid document id format"))
            response = await job_service.get_job("")
            
            assert isinstance(response, GetJobResponse)
            assert response.success is False
            assert response.job is None


class TestJobServiceUpdateJob:

    @pytest.mark.asyncio
    async def test_update_job_success_all_fields(self, job_service: JobService, mock_job_document: dict):
        """Test successfully updating all allowed fields"""
        update_request = UpdateJobRequest(
            job_name="updated_job_name",
            status=JobStatus.SUCCESS,
            priority=JobPriority.HIGH,
            progress=JobProgress(current=100, total=100, message="Complete"),
            metadata={"new_key": "new_value"},
            result=JobResult(success=True, message="Job completed successfully")
        )
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class, \
             patch("app.services.job.job_service.update_document", return_value=True) as mock_update:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
            
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert isinstance(response, UpdateJobResponse)
            assert response.success is True
            assert response.job_id == TEST_JOB_ID
            assert response.message == ""
            
            # Verify update_document was called with correct data
            update_data = mock_update.call_args[0][2]
            assert update_data["job_name"] == "updated_job_name"
            assert update_data["status"] == JobStatus.SUCCESS.value
            assert update_data["priority"] == JobPriority.HIGH.value
            assert update_data["progress"]["current"] == 100
            assert update_data["metadata"]["new_key"] == "new_value"
            assert update_data["result"]["success"] is True

    @pytest.mark.asyncio
    async def test_update_job_single_field(self, job_service: JobService, mock_job_document: dict):
        """Test updating only a single field"""
        update_request = UpdateJobRequest(job_name="new_name_only")
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class, \
             patch("app.services.job.job_service.update_document", return_value=True) as mock_update:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
            
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert response.success is True
            
            # Verify only job_name was in update_data
            update_data = mock_update.call_args[0][2]
            assert "job_name" in update_data
            assert update_data["job_name"] == "new_name_only"
            # Should not include other fields
            assert len([k for k in update_data.keys() if k != "job_name"]) == 0

    @pytest.mark.asyncio
    async def test_update_job_status_with_timestamp_started(self, job_service: JobService, mock_job_document: dict):
        """Test that changing status to STARTED sets started_at timestamp"""
        update_request = UpdateJobRequest(status=JobStatus.STARTED)
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class, \
             patch("app.services.job.job_service.update_document", return_value=True) as mock_update:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
            
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert response.success is True
            
            # Verify started_at was automatically added
            update_data = mock_update.call_args[0][2]
            assert "status" in update_data
            assert update_data["status"] == JobStatus.STARTED.value
            assert "started_at" in update_data
            assert isinstance(update_data["started_at"], datetime)

    @pytest.mark.asyncio
    async def test_update_job_status_with_timestamp_completed(self, job_service: JobService, mock_job_document: dict):
        """Test that changing status to terminal state sets completed_at timestamp"""
        terminal_statuses = [JobStatus.SUCCESS, JobStatus.FAILURE, JobStatus.CANCELLED]
        
        for status in terminal_statuses:
            update_request = UpdateJobRequest(status=status)
            
            with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class, \
                 patch("app.services.job.job_service.update_document", return_value=True) as mock_update:
                mock_mongodb_instance = MagicMock()
                mock_mongodb_class.return_value = mock_mongodb_instance
                mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
                
                response = await job_service.update_job(TEST_JOB_ID, update_request)
                
                assert response.success is True
                
                # Verify completed_at was automatically added
                update_data = mock_update.call_args[0][2]
                assert "status" in update_data
                assert update_data["status"] == status.value
                assert "completed_at" in update_data
                assert isinstance(update_data["completed_at"], datetime)

    @pytest.mark.asyncio
    async def test_update_job_status_does_not_override_existing_timestamp(self, job_service: JobService, mock_job_document: dict):
        """Test that timestamps are not overridden if already set"""
        # Modify mock to have started_at already set
        mock_started_document = mock_job_document.copy()
        existing_started_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_started_document["started_at"] = existing_started_at
        mock_started_document["status"] = JobStatus.STARTED.value
        
        update_request = UpdateJobRequest(status=JobStatus.SUCCESS)
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class, \
             patch("app.services.job.job_service.update_document", return_value=True) as mock_update:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_started_document)
            
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert response.success is True
            
            # Verify started_at was NOT changed
            update_data = mock_update.call_args[0][2]
            assert "started_at" not in update_data  # Should not be in update
            assert "completed_at" in update_data  # But completed_at should be added

    @pytest.mark.asyncio
    async def test_update_job_empty_id(self, job_service: JobService):
        """Test update with empty job_id"""
        update_request = UpdateJobRequest(job_name="test")
        
        response = await job_service.update_job("", update_request)
        
        assert isinstance(response, UpdateJobResponse)
        assert response.success is False
        assert "required" in response.message.lower()

    @pytest.mark.asyncio
    async def test_update_job_not_found(self, job_service: JobService):
        """Test update when job does not exist"""
        update_request = UpdateJobRequest(job_name="test")
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=None)
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert isinstance(response, UpdateJobResponse)
            assert response.success is False
            assert response.job_id == TEST_JOB_ID
            assert "not found" in response.message.lower()

    @pytest.mark.asyncio
    async def test_update_job_empty_job_name(self, job_service: JobService, mock_job_document: dict):
        """Test update with empty job_name is rejected"""
        update_request = UpdateJobRequest(job_name="")
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
            
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert isinstance(response, UpdateJobResponse)
            assert response.success is False
            assert "cannot be empty" in response.message.lower()

    @pytest.mark.asyncio
    async def test_update_job_whitespace_job_name(self, job_service: JobService, mock_job_document: dict):
        """Test update with whitespace-only job_name is rejected"""
        update_request = UpdateJobRequest(job_name="   ")
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
            
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert isinstance(response, UpdateJobResponse)
            assert response.success is False
            assert "cannot be empty" in response.message.lower()

    @pytest.mark.asyncio
    async def test_update_job_no_fields(self, job_service: JobService, mock_job_document: dict):
        """Test update with no fields returns success with no changes"""
        update_request = UpdateJobRequest()  # All fields are None
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
            
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert isinstance(response, UpdateJobResponse)
            assert response.success is True
            assert "no fields" in response.message.lower()

    @pytest.mark.asyncio
    async def test_update_job_database_update_failure(self, job_service: JobService, mock_job_document: dict):
        """Test update when database update fails"""
        update_request = UpdateJobRequest(job_name="new_name")
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class, \
             patch("app.services.job.job_service.update_document", return_value=False):
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
            
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert isinstance(response, UpdateJobResponse)
            assert response.success is False
            assert "database update failed" in response.message.lower()

    @pytest.mark.asyncio
    async def test_update_job_exception(self, job_service: JobService):
        """Test update with exception"""
        update_request = UpdateJobRequest(job_name="test")
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(side_effect=Exception("Database error"))
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert isinstance(response, UpdateJobResponse)
            assert response.success is False
            assert "Failed to update job" in response.message
            assert "Database error" in response.message

    @pytest.mark.asyncio
    async def test_update_job_priority_levels(self, job_service: JobService, mock_job_document: dict):
        """Test updating job with different priority levels"""
        priorities = [JobPriority.LOW, JobPriority.NORMAL, JobPriority.HIGH, JobPriority.CRITICAL]
        
        for priority in priorities:
            update_request = UpdateJobRequest(priority=priority)
            
            with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class, \
                 patch("app.services.job.job_service.update_document", return_value=True) as mock_update:
                mock_mongodb_instance = MagicMock()
                mock_mongodb_class.return_value = mock_mongodb_instance
                mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
                
                response = await job_service.update_job(TEST_JOB_ID, update_request)
                
                assert response.success is True
                
                # Verify priority was set correctly
                update_data = mock_update.call_args[0][2]
                assert update_data["priority"] == priority.value

    @pytest.mark.asyncio
    async def test_update_job_progress_tracking(self, job_service: JobService, mock_job_document: dict):
        """Test updating job progress"""
        update_request = UpdateJobRequest(
            progress=JobProgress(current=50, total=100, message="Processing...")
        )
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class, \
             patch("app.services.job.job_service.update_document", return_value=True) as mock_update:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
            
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert response.success is True
            
            # Verify progress was updated
            update_data = mock_update.call_args[0][2]
            assert "progress" in update_data
            assert update_data["progress"]["current"] == 50
            assert update_data["progress"]["total"] == 100
            assert update_data["progress"]["message"] == "Processing..."

    @pytest.mark.asyncio
    async def test_update_job_result(self, job_service: JobService, mock_job_document: dict):
        """Test updating job result"""
        update_request = UpdateJobRequest(
            result=JobResult(
                success=True,
                data={"output_file": "video.mp4"},
                message="Video processed successfully",
            )
        )
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class, \
             patch("app.services.job.job_service.update_document", return_value=True) as mock_update:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
            
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert response.success is True
            
            # Verify result was updated
            update_data = mock_update.call_args[0][2]
            assert "result" in update_data
            assert update_data["result"]["success"] is True
            assert update_data["result"]["data"]["output_file"] == "video.mp4"
            assert update_data["result"]["message"] == "Video processed successfully"

    @pytest.mark.asyncio
    async def test_update_job_metadata(self, job_service: JobService, mock_job_document: dict):
        """Test updating job metadata"""
        update_request = UpdateJobRequest(
            metadata={"resolution": "4K", "fps": 60, "codec": "h265"}
        )
        
        with patch("app.services.job.job_service.MongoDB") as mock_mongodb_class, \
             patch("app.services.job.job_service.update_document", return_value=True) as mock_update:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_job_document)
            
            response = await job_service.update_job(TEST_JOB_ID, update_request)
            
            assert response.success is True
            
            # Verify metadata was updated
            update_data = mock_update.call_args[0][2]
            assert "metadata" in update_data
            assert update_data["metadata"]["resolution"] == "4K"
            assert update_data["metadata"]["fps"] == 60
            assert update_data["metadata"]["codec"] == "h265"
