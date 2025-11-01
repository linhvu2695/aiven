import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.classes.video import (
    CreateVideoRequest,
    CreateVideoResponse,
    VideoType,
    VideoSourceType,
)
from app.services.video.video_service import VideoService

router = APIRouter()


@router.post("/upload", response_model=CreateVideoResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str | None = None,
    description: str | None = None,
):
    """Upload a video file"""
    if not file:
        raise HTTPException(status_code=400, detail="File is required")
    
    try:
        file_data = await file.read()
        request = CreateVideoRequest(
            filename=file.filename or "video.mp4",
            original_filename=file.filename,
            title=title,
            description=description,
            video_type=VideoType.GENERAL,
            source_type=VideoSourceType.UPLOAD,
            file_data=file_data,
        )
        
        response = await VideoService().create_video(request)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
        
    except Exception as e:
        logging.getLogger("uvicorn.error").error(f"Failed to upload video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload video: {str(e)}")

