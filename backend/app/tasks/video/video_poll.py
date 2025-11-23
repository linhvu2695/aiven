"""
Poll video generation operation status
"""
import asyncio
import logging
from celery import Task
from openai import OpenAI
from app.classes.job import JobProgress, JobResult, JobStatus, UpdateJobRequest
from app.services.video.video_service import VideoService
from app.classes.video import CreateVideoRequest, VideoSourceType, VideoType
from background import background_app, get_worker_loop
from app.core.config import settings
from app.services.job.job_service import JobService

@background_app.task(name="video.poll", bind=True, max_retries=12)
def video_poll(self, job_id: str, operation_id: str):
    loop = get_worker_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(_video_poll_async(self, job_id, operation_id))

async def _video_poll_async(task: Task, job_id: str, operation_id: str):
    """
    Poll video generation operation status from OpenAI.
    
    Args:
        job_id: The job ID in our database
        operation_id: The OpenAI operation ID
        
    Returns:
        dict: Status information about the polling result
    """
    logger = logging.getLogger("uvicorn")
    logger.info(f"Polling video operation {operation_id} for job {job_id}")
    
    try:
        # Initialize OpenAI client and retrieve operation status
        client = OpenAI(api_key=settings.openai_api_key)
        operation = client.videos.retrieve(operation_id)
        
        logger.info(f"OpenAI video operation: {operation}")
        logger.info(f"Operation {operation_id} status: {operation.status}")
        
        if operation.status == "completed":
            logger.info(f"Video generation completed for operation {operation_id}. Downloading video content...")
            
            # Download video content
            response_content = client.videos.download_content(operation_id, variant="video")

            if not response_content or not response_content.content:
                error_msg = f"Video content not found for operation {operation_id}"
                logger.error(error_msg)
                
                # Update job as failed
                await JobService().update_job(job_id, UpdateJobRequest(
                    status=JobStatus.FAILURE,
                    result=JobResult(
                        success=False,
                        message=error_msg
                    )
                ))
                return
            
            # Extract bytes from the response wrapper
            video_bytes = response_content.content
            logger.info(f"Downloaded {len(video_bytes)} bytes of video data")
            
            # Save video content to database/storage
            create_video_response = await VideoService().create_video(CreateVideoRequest(
                filename=f"video_{job_id}.mp4",
                video_type=VideoType.GENERAL,
                source_type=VideoSourceType.AI_GENERATE,
                entity_id=job_id,
                entity_type="job",
                file_data=video_bytes,
            ))

            if not create_video_response.success:
                error_msg = f"Failed to create video: {create_video_response.message}"
                logger.error(error_msg)
                
                # Update job as failed
                await JobService().update_job(job_id, UpdateJobRequest(
                    status=JobStatus.FAILURE,
                    result=JobResult(
                        success=False,
                        message=error_msg
                    )
                ))
                return
            
            # Update job as completed
            await JobService().update_job(job_id, UpdateJobRequest(
                status=JobStatus.SUCCESS,
                progress=JobProgress(
                    current=100,
                    total=100,
                ),
                result=JobResult(
                    success=True,
                    data={
                        "video_id": create_video_response.video_id,
                        "operation_id": operation_id,
                    }
                )
            ))
            
        elif operation.status == "failed":
            # Video generation failed
            operation_error = getattr(operation, "error", None)
            error_msg = getattr(operation_error, "message", "Video generation failed")
            logger.error(f"Video generation failed for operation {operation_id}: {error_msg}")
            
            # Update job as failed
            await JobService().update_job(job_id, UpdateJobRequest(
                status=JobStatus.FAILURE,
                result=JobResult(
                    success=False,
                    message=error_msg
                )
            ))
            
        elif operation.status in ["pending", "in_progress", "queued"]:
            # Still processing - retry after 5 seconds
            progress = getattr(operation, "progress", 0)
            message = f"Video generation still in progress: {progress}. Status: {operation.status}"
            logger.info(message)
            
            await JobService().update_job(job_id, UpdateJobRequest(
                status=JobStatus.PROGRESS,
                progress=JobProgress(
                    current=progress,
                    total=100,
                    message=message
                ),
            ))
            
            # Re-enqueue this task to poll again after 5 seconds
            video_poll.apply_async(
                args=[job_id, operation_id],
                countdown=5
            )
            return  # Exit cleanly without exception
            
        else:
            error_msg = f"Unknown operation status: {operation.status}"
            logger.warning(error_msg)
            
            # Update job as failed
            await JobService().update_job(job_id, UpdateJobRequest(
                status=JobStatus.FAILURE,
                result=JobResult(
                    success=False,
                    message=error_msg
                )
            ))
            
    except Exception as e:
        logger.error(f"Error polling video operation {operation_id}: {e}")
        
        # Update job as failed
        await JobService().update_job(job_id, UpdateJobRequest(
            status=JobStatus.FAILURE,
            result=JobResult(
                success=False,
                message=str(e)
            )
        ))
        
        return
