import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from app.classes.video import (
    CreateVideoRequest,
    CreateVideoResponse,
    DeleteVideoRequest,
    DeleteVideoResponse,
    GetVideoResponse,
    VideoType,
    VideoSourceType,
    VideoListRequest,
    VideoListResponse,
    VideoUrlsRequest,
    VideoGenerateRequest,
    VideoGenerateResponse,
)
from app.services.video.video_service import VideoService
from app.services.video.video_gen.video_gen_aspect_ratio import VideoGenAspectRatio
from app.services.video.video_constants import VideoGenModel

MAX_VIDEOS_LIMIT = 20

router = APIRouter()


@router.get("/models")
async def get_models():
    """Get available video generation models grouped by provider"""
    return await VideoService().get_models()


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
            return JSONResponse(
                status_code=400,
                content=response.model_dump()
            )
        return response
        
    except Exception as e:
        logging.getLogger("uvicorn.error").error(f"Failed to upload video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload video: {str(e)}")

@router.get("/{video_id}", response_model=GetVideoResponse)
async def get_video(video_id: str):
    """Get a video by ID"""
    response = await VideoService().get_video(video_id)
    if not response.success:
        raise HTTPException(status_code=404, detail=response.message)
    return response

@router.post("/list", response_model=VideoListResponse)
async def list_videos(request: VideoListRequest):
    """List all videos"""
    try:
        return await VideoService().list_videos(request)
    except Exception as e:
        message = f"Error listing videos: {str(e)}"
        logging.getLogger("uvicorn.error").error(message)
        raise HTTPException(status_code=400, detail=message)

@router.get("/serve/ids/{video_ids}")
async def serve_videos(video_ids: str):
    """Serve multiple videos via GET with comma-separated video IDs"""
    try:
        # Parse comma-separated video IDs
        ids = [id.strip() for id in video_ids.split(',') if id.strip()]
        
        if not ids:
            raise HTTPException(status_code=400, detail="No video IDs provided")
            
        if len(ids) > MAX_VIDEOS_LIMIT:
            raise HTTPException(status_code=400, detail=f"Too many video IDs (max {MAX_VIDEOS_LIMIT})")
        
        response = await VideoService().get_videos_presigned_urls(VideoUrlsRequest(video_ids=ids))
        if not response.success and all(not result.success for result in response.results):
            return JSONResponse(
                status_code=400,
                content=response.model_dump()
            )
        return response
    except Exception as e:
        logging.getLogger("uvicorn.error").error(f"Error getting video urls: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error getting video urls: {str(e)}")

@router.delete("/{video_id}", response_model=DeleteVideoResponse)
async def delete_video(video_id: str):
    """Delete a video by its ID"""
    response = await VideoService().delete_video(DeleteVideoRequest(
        video_id=video_id, 
        soft_delete=False
        ))
    if response.success:
        return response
    else:
        raise HTTPException(status_code=400, detail=response.message)

@router.post("/generate", response_model=VideoGenerateResponse)
async def generate_video(
    prompt: str, 
    model: str,
    image_id: Optional[str] = None, 
    aspect_ratio: Optional[VideoGenAspectRatio] = VideoGenAspectRatio.RATIO_16_9,
    duration: Optional[int] = 5
    ):
    """Generate a video using the specified provider"""
    video_gen_model = VideoGenModel(model)
    if not video_gen_model:
        raise HTTPException(status_code=400, detail=f"Invalid model: {model}")

    response = await VideoService().generate_video(VideoGenerateRequest(
        prompt=prompt, 
        model=video_gen_model,
        image_id=image_id,
        aspect_ratio=aspect_ratio,
        duration=duration
        ))

    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response