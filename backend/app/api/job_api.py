import logging
from fastapi import APIRouter, HTTPException
from app.classes.job import (
    CreateJobRequest,
    CreateJobResponse,
    GetJobResponse,
    JobListRequest,
    JobListResponse,
    UpdateJobRequest,
    UpdateJobResponse,
)
from app.services.job.job_service import JobService

router = APIRouter()


@router.post("/", response_model=CreateJobResponse)
async def create_job(request: CreateJobRequest):
    """
    Create a new background job entry.
    
    This endpoint creates a job record in the database that can be tracked.
    The job_id returned should be used as the Celery task ID when queuing the actual task.
    """
    response = await JobService().create_job(request)
    if response.success:
        return response
    else:
        raise HTTPException(status_code=500, detail=response.message)


@router.post("/list", response_model=JobListResponse)
async def list_jobs(request: JobListRequest):
    """
    List jobs with optional filtering and pagination.
    """
    try:
        return await JobService().list_jobs(request)
    except Exception as e:
        message = f"Error listing jobs: {str(e)}"
        logging.getLogger("uvicorn.error").error(message)
        raise HTTPException(status_code=400, detail=message)


@router.get("/{job_id}", response_model=GetJobResponse)
async def get_job(job_id: str):
    """
    Get job information by job ID.
    """
    response = await JobService().get_job(job_id)
    if response.success:
        return response
    else:
        raise HTTPException(status_code=404, detail=response.message)


@router.put("/{job_id}", response_model=UpdateJobResponse)
async def update_job(job_id: str, request: UpdateJobRequest):
    """
    Update specific fields of an existing job.
    """
    response = await JobService().update_job(job_id, request)
    if response.success:
        return response
    else:
        raise HTTPException(status_code=400, detail=response.message)