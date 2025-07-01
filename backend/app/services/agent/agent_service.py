import logging
from fastapi import logger
from app.classes.agent import (
    CreateOrUpdateAgentRequest,
    CreateOrUpdateAgentResponse,
    AgentInfo,
    SearchAgentsResponse,
)
from app.core.database import insert_document, get_document, update_document, list_documents
from bson import ObjectId

AGENT_COLLECTION_NAME = "agents"


class AgentService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(AgentService, cls).__new__(cls)
        return cls._instance

    def _validate_create_agent_request(
        self, request: CreateOrUpdateAgentRequest
    ) -> tuple[bool, str]:
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
            tone=data.get("tone", ""),
        )

    async def create_or_update_agent(
        self, request: CreateOrUpdateAgentRequest
    ) -> CreateOrUpdateAgentResponse:
        valid, warning = self._validate_create_agent_request(request)
        if not valid:
            logging.getLogger("uvicorn.error").warn(warning)
            return CreateOrUpdateAgentResponse(success=False, id="", message=warning)

        try:
            document = {
                "name": request.name,
                "description": request.description,
                "model": request.model,
                "persona": request.persona,
                "tone": request.tone,
            }
            
            if getattr(request, "id", None):  # Update if id is present
                updated_id = await update_document(
                    AGENT_COLLECTION_NAME, str(request.id), document
                )
                if updated_id is not None:
                    raise Exception(f"Agent update failed for id {request.id}")

                return CreateOrUpdateAgentResponse(
                    success=True,
                    id=str(updated_id),
                    message="Agent updated successfully.",
                )
            else:  # Insert new
                inserted_id = await insert_document(AGENT_COLLECTION_NAME, document)
                return CreateOrUpdateAgentResponse(
                    success=True, id=inserted_id, message="Agent created successfully."
                )
        except Exception as e:
            return CreateOrUpdateAgentResponse(success=False, id="", message=str(e))

    async def search_agents(self) -> SearchAgentsResponse:
        documents = await list_documents(AGENT_COLLECTION_NAME)
        agents = [
            AgentInfo(
                id=str(doc.get("_id", "")),
                name=doc.get("name", ""),
                description=doc.get("description", ""),
                model=doc.get("model", ""),
                persona=doc.get("persona", ""),
                tone=doc.get("tone", ""),
            )
            for doc in documents
        ]
        return SearchAgentsResponse(agents=agents)
