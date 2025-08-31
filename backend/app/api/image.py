import logging
from fastapi import APIRouter, HTTPException
from app.services.image.image_service import ImageService
from app.classes.image import ImageUrlsResponse

MAX_IMAGES_LIMIT = 50

router = APIRouter()

@router.get("/{image_id}")
async def get_image(image_id: str):
    """Get an image by its ID"""
    response = await ImageService().get_image(image_id)
    if not response.success:
        raise HTTPException(status_code=404, detail=response.message)
    return response

@router.get("/serve/{image_id}")
async def serve_image(image_id: str):
    """Serve an image by its ID"""
    response = await ImageService().get_image_presigned_url(image_id)
    if not response.success:
        raise HTTPException(status_code=404, detail=response.message)
    return response

@router.get("/serve/ids/{image_ids}")
async def serve_images(image_ids: str):
    """Serve multiple images via GET with comma-separated image IDs"""    
    try:
        # Parse comma-separated image IDs
        ids = [id.strip() for id in image_ids.split(',') if id.strip()]
        
        if not ids:
            raise HTTPException(status_code=400, detail="No image IDs provided")
            
        if len(ids) > MAX_IMAGES_LIMIT:  # Reasonable limit
            raise HTTPException(status_code=400, detail=f"Too many image IDs (max {MAX_IMAGES_LIMIT})")
        
        response = await ImageService().get_images_presigned_urls(ids)
        
        # Check if all images failed
        if not response.success and all(not result.success for result in response.results):
            raise HTTPException(status_code=404, detail=response.message)
        
        return response
        
    except ValueError as e:
        logging.getLogger("uvicorn.error").error(f"Error getting image urls: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error getting image urls: {str(e)}")