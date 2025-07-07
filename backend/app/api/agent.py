from fastapi import APIRouter, UploadFile, File, HTTPException
from app.classes.agent import CreateOrUpdateAgentRequest, CreateOrUpdateAgentResponse, SearchAgentsResponse
from app.services.agent.agent_service import AgentService

router = APIRouter()

@router.get("/id={id}")
async def get_agent(id: str):
    return await AgentService().get_agent(id)

@router.post("/", response_model=CreateOrUpdateAgentResponse)
async def create_or_update_agent(request: CreateOrUpdateAgentRequest):
    return await AgentService().create_or_update_agent(request)

@router.get("/search", response_model=SearchAgentsResponse)
async def search_agents():
    return await AgentService().search_agents()

@router.post("/delete")
async def delete_agent(id: str):
    return await AgentService().delete_agent(id)

@router.post("/avatar")
async def update_agent_avatar(id: str, avatar: UploadFile = File(...)):
    try:
        filename = avatar.filename or "avatar"
        url = await AgentService().update_agent_avatar(id, avatar.file, filename)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



