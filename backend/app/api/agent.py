from fastapi import APIRouter
from app.classes.agent import CreateOrUpdateAgentRequest, CreateOrUpdateAgentResponse
from app.services.agent.agent_service import AgentService

router = APIRouter()

@router.get("/{id}")
async def get_agent(id: str):
    return await AgentService().get_agent(id)

@router.post("/", response_model=CreateOrUpdateAgentResponse)
async def create_or_update_agent(request: CreateOrUpdateAgentRequest):
    return await AgentService().create_or_update_agent(request)




