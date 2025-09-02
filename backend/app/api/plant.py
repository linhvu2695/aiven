import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.classes.plant import (
    AutofillPlantInfoResponse,
    CreateOrUpdatePlantRequest,
    CreateOrUpdatePlantResponse,
    PlantResponse,
    PlantListResponse,
    AddPlantPhotoRequest,
    PlantPhotoResponse,
)
from app.services.plant.plant_service import PlantService
from app.utils.string.string_utils import is_empty_string

router = APIRouter()


@router.post("/", response_model=CreateOrUpdatePlantResponse)
async def create_or_update_plant(request: CreateOrUpdatePlantRequest):
    """Create a new plant or update an existing one"""
    try:
        logging.getLogger("uvicorn.error").info(f"Creating or updating plant: {request}")
        response = await PlantService().create_or_update_plant(request)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create or update plant: {str(e)}")


@router.get("/{plant_id}", response_model=PlantResponse)
async def get_plant(plant_id: str):
    """Get a plant by ID"""
    response = await PlantService().get_plant(plant_id)
    if not response.success:
        raise HTTPException(status_code=404, detail=response.message)
    return response


@router.get("/", response_model=PlantListResponse)
async def list_plants():
    """List all plants"""
    return await PlantService().list_plants()


@router.post("/{id}/photo", response_model=PlantPhotoResponse)
async def add_plant_photo(
    id: str,
    file: UploadFile = File(...),
):
    """Add a photo to a plant"""
    if is_empty_string(id):
        raise HTTPException(status_code=400, detail="Plant ID is required")
    if not file:
        raise HTTPException(status_code=400, detail="File is required")
    
    try:
        file_data = await file.read()
        request = AddPlantPhotoRequest(
            plant_id=id,
            filename=file.filename or "plant_photo.jpg",
            file_data=file_data,
        )
        
        response = await PlantService().add_plant_photo(id, request)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")


@router.post("/autofill", response_model=AutofillPlantInfoResponse)
async def autofill_plant_info(file: UploadFile = File(...)):
    """Analyze plant health using AI"""
    file_data = await file.read()
    response = await PlantService().autofill_plant_info(file_data)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response


@router.delete("/{plant_id}")
async def delete_plant(plant_id: str):
    """Delete a plant"""
    # TODO: Implement plant deletion
    raise HTTPException(status_code=501, detail="Plant deletion not yet implemented")
