from fastapi import APIRouter
from app.classes.agent import CreateAgentRequest, CreateAgentResponse
from app.services.agent.agent_service import AgentService

router = APIRouter()

@router.get("/{id}")
async def get_agent(id: str):
    return await AgentService().get_agent(id)

@router.post("/", response_model=CreateAgentResponse)
async def create_agent(request: CreateAgentRequest):
    return await AgentService().create_agent(request)




