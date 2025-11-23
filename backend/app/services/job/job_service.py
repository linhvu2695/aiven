import logging
from datetime import datetime, timedelta, timezone

from app.utils.string.string_utils import is_empty_string
from app.classes.job import (
    CreateJobRequest,
    CreateJobResponse,
    GetJobResponse,
    UpdateJobRequest,
    UpdateJobResponse,
    JobListRequest,
    JobListResponse,
    JobInfo,
    JobStatus,
    JobPriority,
    JobType,
)
from app.core.database import MongoDB

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

            inserted_id = await MongoDB().insert_document(JOB_COLLECTION_NAME, document)
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
            data = await MongoDB().get_document(JOB_COLLECTION_NAME, job_id)
            
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
                message=""
            )
            
        except Exception as e:
            error_msg = f"Failed to retrieve job {job_id}: {e}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return GetJobResponse(
                success=False,
                job=None,
                message=error_msg
            )

    async def update_job(
        self, job_id: str, request: UpdateJobRequest
    ) -> UpdateJobResponse:
        """
        Update specific fields of an existing job.
        """
        if is_empty_string(job_id):
            return UpdateJobResponse(
                success=False,
                job_id="",
                message="Job ID is required"
            )

        try:
            # Check if the job exists
            existing_job = await MongoDB().get_document(JOB_COLLECTION_NAME, job_id)
            if not existing_job:
                return UpdateJobResponse(
                    success=False,
                    job_id=job_id,
                    message=f"Job not found: {job_id}"
                )

            # Build update document with only the fields that were provided
            update_data = {}
            
            if request.job_name is not None:
                if request.job_name.strip() == "":
                    return UpdateJobResponse(
                        success=False,
                        job_id=job_id,
                        message="Job name cannot be empty"
                    )
                update_data["job_name"] = request.job_name
            
            if request.status is not None:
                update_data["status"] = request.status.value
                
                # Auto-update timestamps based on status changes
                current_status = existing_job.get("status")
                if request.status.value != current_status:
                    now = datetime.now(timezone.utc)
                    
                    # Set started_at when moving to STARTED
                    if request.status == JobStatus.STARTED and not existing_job.get("started_at"):
                        update_data["started_at"] = now
                    
                    # Set completed_at when moving to terminal states
                    elif request.status in [JobStatus.SUCCESS, JobStatus.FAILURE, JobStatus.CANCELLED]:
                        if not existing_job.get("completed_at"):
                            update_data["completed_at"] = now
            
            if request.priority is not None:
                update_data["priority"] = request.priority.value
            
            if request.progress is not None:
                update_data["progress"] = request.progress.model_dump()
            
            if request.metadata is not None:
                update_data["metadata"] = request.metadata
            
            if request.result is not None:
                update_data["result"] = request.result.model_dump()

            # If no fields to update, return early
            if not update_data:
                return UpdateJobResponse(
                    success=True,
                    job_id=job_id,
                    message="No fields to update"
                )

            # Perform the update
            success = await MongoDB().update_document(
                JOB_COLLECTION_NAME,
                job_id,
                update_data
            )

            if not success:
                error_msg = "Failed to update job: Database update failed"
                logging.getLogger("uvicorn.error").error(error_msg)
                return UpdateJobResponse(
                    success=False,
                    job_id=job_id,
                    message=error_msg
                )

            return UpdateJobResponse(
                success=True,
                job_id=job_id,
                message=""
            )

        except Exception as e:
            error_msg = f"Failed to update job {job_id}: {e}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return UpdateJobResponse(
                success=False,
                job_id=job_id,
                message=error_msg
            )

    async def list_jobs(self, request: JobListRequest) -> JobListResponse:
        """
        List jobs with optional filtering and pagination.
        """
        try:
            # Build filters dictionary for multi-field filtering
            filters = {}
            
            if request.job_type:
                filters["job_type"] = request.job_type.value
            
            if request.status:
                filters["status"] = request.status.value
            
            if request.entity_id:
                filters["entity_id"] = request.entity_id
            
            if request.entity_type:
                filters["entity_type"] = request.entity_type
            
            if request.priority:
                filters["priority"] = request.priority.value

            # Get total count for pagination
            total_count = await MongoDB().count_documents_with_filters(
                JOB_COLLECTION_NAME, filters
            )

            # Calculate pagination
            skip = (request.page - 1) * request.page_size

            # Get paginated documents
            documents = await MongoDB().find_documents_with_filters(
                JOB_COLLECTION_NAME,
                filters,
                skip=skip,
                limit=request.page_size,
                sort_by="created_at",
                asc=False,  # Most recent first
            )

            # Convert to JobInfo objects
            jobs = []
            for doc in documents:
                job_info = JobInfo(
                    id=str(doc.get("_id", "")),
                    job_type=JobType(doc["job_type"]),
                    job_name=doc.get("job_name", ""),
                    status=JobStatus(doc["status"]),
                    priority=JobPriority(doc["priority"]),
                    metadata=doc.get("metadata", {}),
                    entity_id=doc.get("entity_id"),
                    entity_type=doc.get("entity_type"),
                    created_at=doc["created_at"],
                    started_at=doc.get("started_at"),
                    completed_at=doc.get("completed_at"),
                    expires_at=doc.get("expires_at"),
                    retries=doc.get("retries", 0),
                    max_retries=doc.get("max_retries", 3),
                    retry_delay=doc.get("retry_delay"),
                    progress=doc.get("progress"),
                    result=doc.get("result"),
                )
                jobs.append(job_info)

            return JobListResponse(
                jobs=jobs,
                total=total_count,
                page=request.page,
                page_size=request.page_size
            )

        except Exception as e:
            error_msg = f"Failed to list jobs: {e}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return JobListResponse(
                jobs=[],
                total=0,
                page=request.page,
                page_size=request.page_size
            )

