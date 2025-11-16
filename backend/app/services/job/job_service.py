import logging
from datetime import datetime, timedelta, timezone

from app.utils.string.string_utils import is_empty_string
from app.classes.job import (
    CreateJobRequest,
    CreateJobResponse,
    GetJobResponse,
    JobInfo,
    JobStatus,
    JobPriority,
    JobType,
)
from app.core.database import (
    insert_document,
    get_document,
    update_document,
    delete_document,
)

JOB_COLLECTION_NAME = "jobs"
DEFAULT_JOB_EXPIRATION_MINUTES = 24 * 60


class JobService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(JobService, cls).__new__(cls)
        return cls._instance

    def _validate_create_job_request(
        self, request: CreateJobRequest
    ) -> tuple[bool, str]:
        warning = ""

        # Required fields
        if not request.job_name or request.job_name.strip() == "":
            warning = "Invalid job info. Missing job_name"
            return False, warning

        return True, warning

    async def create_job(
        self, request: CreateJobRequest
    ) -> CreateJobResponse:
        """
        Create a new background job entry in the database.
        """
        valid, warning = self._validate_create_job_request(request)
        if not valid:
            logging.getLogger("uvicorn.warning").warning(warning)
            return CreateJobResponse(
                success=False, 
                job_id="", 
                message=warning
            )

        try:
            # Calculate expiration time (default 24 hours from now)
            created_at = datetime.now(timezone.utc)
            expires_at = created_at + timedelta(minutes=DEFAULT_JOB_EXPIRATION_MINUTES)
            
            # Create job document (MongoDB will generate the _id)
            document = {
                "job_type": request.job_type.value,
                "job_name": request.job_name,
                "status": JobStatus.PENDING.value,
                "priority": request.priority.value,
                "metadata": request.metadata,
                "entity_id": request.entity_id,
                "entity_type": request.entity_type,
                "created_at": created_at,
                "started_at": None,
                "completed_at": None,
                "expires_at": expires_at,
                "retries": 0,
                "max_retries": 3,
                "retry_delay": None,
                "progress": None,
                "result": None,
            }

            inserted_id = await insert_document(JOB_COLLECTION_NAME, document)
            if is_empty_string(inserted_id):
                error_msg = "Failed to create job: Failed to insert document."
                logging.getLogger("uvicorn.error").error(error_msg)
                return CreateJobResponse(
                    success=False,
                    job_id="",
                    message="Failed to create job: Failed to insert document."
                )
            
            return CreateJobResponse(
                success=True,
                job_id=inserted_id,
                message=""
            )
            
        except Exception as e:
            error_msg = f"Failed to create job: {e}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return CreateJobResponse(
                success=False,
                job_id="",
                message=error_msg
            )

    async def get_job(self, job_id: str) -> GetJobResponse:
        """
        Retrieve job information by job ID.
        """
        try:
            data = await get_document(JOB_COLLECTION_NAME, job_id)
            
            if not data:
                return GetJobResponse(
                    success=False,
                    job=None,
                    message=f"Job not found: {job_id}"
                )

            # Parse the document into JobInfo
            job_info = JobInfo(
                id=str(data.get("_id", "")),
                job_type=JobType(data["job_type"]),  # Required field, should always exist
                job_name=data.get("job_name", ""),
                status=data.get("status", JobStatus.PENDING.value),
                priority=data.get("priority", JobPriority.NORMAL.value),
                metadata=data.get("metadata", {}),
                entity_id=data.get("entity_id"),
                entity_type=data.get("entity_type"),
                created_at=data["created_at"],  # Required field, should always exist
                started_at=data.get("started_at"),
                completed_at=data.get("completed_at"),
                expires_at=data.get("expires_at"),
                retries=data.get("retries", 0),
                max_retries=data.get("max_retries", 3),
                retry_delay=data.get("retry_delay"),
                progress=data.get("progress"),
                result=data.get("result"),
            )

            return GetJobResponse(
                success=True,
                job=job_info,
                message="Job retrieved successfully."
            )
            
        except Exception as e:
            error_msg = f"Failed to retrieve job {job_id}: {e}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return GetJobResponse(
                success=False,
                job=None,
                message=error_msg
            )

