from fastapi import APIRouter, UploadFile, File, HTTPException
from app.classes.agent import (
    CreateOrUpdateAgentRequest, 
    CreateOrUpdateAgentResponse, 
    DeleteAgentResponse,
    UpdateAgentAvatarResponse,
    SearchAgentsResponse,
    EvaluateAgentRequest,
    EvaluateAgentResponse
)
from app.services.agent.agent_service import AgentService
from app.services.agent.agent_eval_service import AgentEvalService
from app.services.image.image_service import ImageService

router = APIRouter()

@router.get("/id={id}")
async def get_agent(id: str):
    return await AgentService().get_agent(id)

@router.post("/", response_model=CreateOrUpdateAgentResponse)
async def create_or_update_agent(request: CreateOrUpdateAgentRequest):
    response = await AgentService().create_or_update_agent(request)
    if response.success:
        return response
    else:
        raise HTTPException(status_code=500, detail=response.message)

@router.get("/search", response_model=SearchAgentsResponse)
async def search_agents():
    return await AgentService().search_agents()

@router.post("/delete", response_model=DeleteAgentResponse)
async def delete_agent(id: str):
    response = await AgentService().delete_agent(id)
    if response.success:
        return response
    else:
        raise HTTPException(status_code=500, detail=response.message)

@router.post("/avatar", response_model=UpdateAgentAvatarResponse)
async def update_agent_avatar(id: str, avatar: UploadFile = File(...)):
    response = await AgentService().update_agent_avatar(id, avatar.file, avatar.filename or "avatar")
    if response.success:
        return response
    else:
        raise HTTPException(status_code=500, detail=response.message)

@router.get("/avatar/{agent_id}")
async def get_agent_avatar_url(agent_id: str):
    """Get the avatar URL for an agent"""
    try:
        agent = await AgentService().get_agent(agent_id)
        if not agent.avatar_image_id:
            return {"url": ""}
        
        image_service = ImageService()
        url_response = await image_service.get_image_presigned_url(agent.avatar_image_id)
        if url_response.success:
            return {"url": url_response.url}
        else:
            return {"url": ""}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate", response_model=EvaluateAgentResponse)
async def evaluate_agent(request: EvaluateAgentRequest):
    """Evaluate an agent by comparing expected vs actual trajectory"""
    response = await AgentEvalService().evaluate_agent(request)
    if response.success:
        return response
    else:
        raise HTTPException(status_code=500, detail=response.message)


