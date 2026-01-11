from fastapi import APIRouter, HTTPException
from app.classes.graph import AddTextEpisodeRequest, AddTextEpisodeResponse
from app.services.graph.graphiti_service import GraphitiService

router = APIRouter()


@router.post("/episode/text", response_model=AddTextEpisodeResponse)
async def add_text_episode(request: AddTextEpisodeRequest):
    """Add a text episode to the knowledge graph"""
    response = await GraphitiService().add_text_episode(request)
    
    if response.success:
        return response
    else:
        raise HTTPException(status_code=400, detail=response.message)
