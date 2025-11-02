import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from app.classes.video import (
    CreateVideoRequest,
    CreateVideoResponse,
    GetVideoResponse,
    VideoType,
    VideoSourceType,
    VideoListRequest,
    VideoListResponse,
    VideoUrlsRequest,
)
from app.services.video.video_service import VideoService

MAX_VIDEOS_LIMIT = 20

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

@router.get("/serve/{video_id}")
async def serve_video(video_id: str):
    """Serve a video by its ID"""
    response = await VideoService().get_video_presigned_url(video_id)
    if not response:
        raise HTTPException(status_code=404, detail="Video not found")
    return response

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