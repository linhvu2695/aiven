import logging
from fastapi import logger
from app.classes.agent import CreateAgentRequest, CreateAgentResponse, AgentInfo
from app.core.database import insert_document, get_document
from bson import ObjectId

AGENT_COLLECTION_NAME = "agents"

class AgentService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance') or cls._instance is None:
            cls._instance = super(AgentService, cls).__new__(cls)
        return cls._instance
    
    def _validate_create_agent_request(self, request: CreateAgentRequest) -> tuple[bool, str]:
        warning = ""

        # Required fields
        required_fields = ["name", "model"]
        for field in required_fields:
            value = getattr(request, field, None)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                warning = f"Invalid agent info. Missing value for field: {field}"
                return False, warning

        return True, warning
        
    async def get_agent(self, id: str) -> AgentInfo:
        data = await get_document(AGENT_COLLECTION_NAME, id)
        
        return AgentInfo(
            id=str(data.get("_id", "")),
            name=data.get("name", ""),
            description=data.get("description", ""),
            model=data.get("model", ""),
            persona=data.get("persona", ""),
            tone=data.get("tone", "")
        )

    async def create_agent(self, request: CreateAgentRequest) -> CreateAgentResponse:
        valid, warning = self._validate_create_agent_request(request)
        if not valid:
            logging.getLogger("uvicorn.error").warn(warning)
            return CreateAgentResponse(success=False, id="", message=warning)
        
        try:
            document = {
                "name": request.name,
                "description": request.description,
                "model": request.model,
                "persona": request.persona,
                "tone": request.tone
            }
            inserted_id = await insert_document(AGENT_COLLECTION_NAME, document)

            return CreateAgentResponse(success=True, id=inserted_id, message="Agent created successfully.")
        except Exception as e:
            return CreateAgentResponse(success=False, id="", message=str(e))