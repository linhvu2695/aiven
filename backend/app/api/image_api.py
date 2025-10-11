import logging
from fastapi import APIRouter, HTTPException
from app.services.image.image_service import ImageService
from app.classes.image import DeleteImageResponse, ImageGenerateRequest, ImageGenerateResponse
from app.services.image.image_gen.image_gen_providers import ImageGenProvider

MAX_IMAGES_LIMIT = 50

router = APIRouter()

@router.get("/{image_id}")
async def get_image(image_id: str):
    """Get an image by its ID"""
    response = await ImageService().get_image(image_id)
    if not response.success:
        raise HTTPException(status_code=404, detail=response.message)
    return response

@router.delete("/{image_id}", response_model=DeleteImageResponse)
async def delete_image(image_id: str):
    """Delete an image by its ID"""
    response = await ImageService().delete_image(image_id, soft_delete=False)
    if response.success:
        return response
    else:
        raise HTTPException(status_code=400, detail=response.message)

@router.post("/bin/{image_id}", response_model=DeleteImageResponse)
async def bin_image(image_id: str):
    """Bin an image by its ID"""
    response = await ImageService().delete_image(image_id, soft_delete=True)
    if response.success:
        return response
    else:
        raise HTTPException(status_code=400, detail=response.message)

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

@router.post("/generate", response_model=ImageGenerateResponse)
async def generate_image(prompt: str, provider: ImageGenProvider = ImageGenProvider.GEMINI):
    """Generate an image using the specified provider"""
    response = await ImageService().generate_image(ImageGenerateRequest(prompt=prompt, provider=provider))
    if response.success:
        return response
    else:
        raise HTTPException(status_code=400, detail=response.message)
    