from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Status of a background job"""
    PENDING = "pending"
    STARTED = "started"
    RETRY = "retry"
    PROGRESS = "progress"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class JobPriority(int, Enum):
    """Priority levels for jobs (Celery supports 0-9, where higher is more priority)"""
    LOW = 3
    NORMAL = 5
    HIGH = 7
    CRITICAL = 9


class JobType(str, Enum):
    """Types of background jobs"""
    VIDEO_GENERATION = "video_generation"
    VIDEO_PROCESSING = "video_processing"
    IMAGE_PROCESSING = "image_processing"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    EMAIL_NOTIFICATION = "email_notification"
    BATCH_UPDATE = "batch_update"
    SCHEDULED_TASK = "scheduled_task"
    CLEANUP = "cleanup"
    GENERAL = "general"


class JobProgress(BaseModel):
    """Progress tracking for long-running jobs"""
    current: int = 0
    total: int = 0
    message: Optional[str] = None


class JobResult(BaseModel):
    """Result information from completed job"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None


class JobInfo(BaseModel):
    """Comprehensive background job information model"""
    id: str  # also the Celery task ID (UUID)
    job_type: JobType
    job_name: str 
    
    # Status tracking
    status: JobStatus = JobStatus.PENDING
    progress: Optional[JobProgress] = None
    
    # Job metadata
    priority: JobPriority = JobPriority.NORMAL
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Relationships (what entity this job is working on)
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    
    # Timing information
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Retry information
    retries: int = 0
    max_retries: int = 3
    retry_delay: Optional[int] = None
    
    # Result
    result: Optional[JobResult] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CreateJobRequest(BaseModel):
    """Request model for creating a job"""
    job_type: JobType = JobType.GENERAL
    job_name: str
    priority: JobPriority = JobPriority.NORMAL
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    metadata: Dict[str, Any] = {}


class CreateJobResponse(BaseModel):
    """Response model for creating a job"""
    success: bool
    job_id: str
    message: str


class GetJobResponse(BaseModel):
    """Response model for getting a job"""
    success: bool
    job: Optional[JobInfo] = None
    message: str


class CancelJobRequest(BaseModel):
    """Request model for canceling a job"""
    job_id: str
    skip_running: bool = False  # Whether to skip if already running


class CancelJobResponse(BaseModel):
    """Response model for canceling a job"""
    success: bool
    job_id: str
    message: str


class RetryJobRequest(BaseModel):
    """Request model for retrying a failed job"""
    job_id: str
    reset_retries: bool = False  # Whether to reset the retry counter


class RetryJobResponse(BaseModel):
    """Response model for retrying a job"""
    success: bool
    job_id: str
    new_job_id: Optional[str] = None  # If a new job was created
    message: str


class UpdateJobRequest(BaseModel):
    """Request model for updating a job - only allows updating certain fields"""
    job_name: Optional[str] = None
    status: Optional[JobStatus] = None
    priority: Optional[JobPriority] = None
    progress: Optional[JobProgress] = None
    metadata: Optional[Dict[str, Any]] = None
    result: Optional[JobResult] = None


class UpdateJobResponse(BaseModel):
    """Response model for updating a job"""
    success: bool
    job_id: str
    message: str
