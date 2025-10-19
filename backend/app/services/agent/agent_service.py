import logging

from bson import ObjectId
from app.classes.agent import (
    CreateOrUpdateAgentRequest,
    CreateOrUpdateAgentResponse,
    DeleteAgentResponse,
    UpdateAgentAvatarResponse,
    AgentInfo,
    SearchAgentsResponse,
)
from app.classes.image import ImageType, ImageSourceType, CreateImageRequest
from app.core.database import (
    insert_document,
    get_document,
    update_document,
    list_documents,
    delete_document,
)
from app.services.image.image_service import ImageService
from app.utils.string.string_utils import is_empty_string

AGENT_COLLECTION_NAME = "agents"
AVATAR_STORAGE_FOLDER = "avatar"
AGENT_AVATAR_PRESIGNED_URL_EXPIRATION = 60 * 60


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

    async def _get_avatar_url(self, avatar_image_id: str) -> str:
        if is_empty_string(avatar_image_id):
            return ""
        return (await ImageService().get_image_presigned_url(avatar_image_id)).url or ""
    
    async def get_agent(self, id: str) -> AgentInfo:
        data = await get_document(AGENT_COLLECTION_NAME, id)

        return AgentInfo(
            id=str(data.get("_id", "")),
            name=data.get("name", ""),
            description=data.get("description", ""),
            avatar_image_url=await self._get_avatar_url(data.get("avatar_image_id", "")),
            avatar_image_id=data.get("avatar_image_id"),
            model=data.get("model", ""),
            persona=data.get("persona", ""),
            tone=data.get("tone", ""),
            tools=data.get("tools", []),
        )

    async def create_or_update_agent(
        self, request: CreateOrUpdateAgentRequest
    ) -> CreateOrUpdateAgentResponse:
        valid, warning = self._validate_create_agent_request(request)
        if not valid:
            logging.getLogger("uvicorn.warning").warning(warning)
            return CreateOrUpdateAgentResponse(success=False, id="", message=warning)

        try:
            document = {
                "name": request.name,
                "description": request.description,
                "avatar_image_id": request.avatar_image_id,
                "model": request.model,
                "persona": request.persona,
                "tone": request.tone,
                "tools": request.tools,
            }

            if getattr(request, "id", None):  # Update if id is present
                await update_document(
                    AGENT_COLLECTION_NAME, str(request.id), document
                )

                return CreateOrUpdateAgentResponse(
                    success=True,
                    id=str(request.id),
                    message="Agent updated successfully.",
                )
            else:  # Insert new
                inserted_id = await insert_document(AGENT_COLLECTION_NAME, document)
                return CreateOrUpdateAgentResponse(
                    success=True, id=inserted_id, message="Agent created successfully."
                )
        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Failed to create or update agent: {e}")
            return CreateOrUpdateAgentResponse(success=False, id="", message=str(e))

    async def search_agents(self) -> SearchAgentsResponse:
        documents = await list_documents(AGENT_COLLECTION_NAME)
        agents = [
            AgentInfo(
                id=str(doc.get("_id", "")),
                name=doc.get("name", ""),
                description=doc.get("description", ""),
                avatar_image_id=doc.get("avatar_image_id"),
                avatar_image_url=await self._get_avatar_url(doc.get("avatar_image_id", "")),
                model=doc.get("model", ""),
                persona=doc.get("persona", ""),
                tone=doc.get("tone", ""),
                tools=doc.get("tools", []),
            )
            for doc in documents
        ]
        return SearchAgentsResponse(agents=agents)

    async def delete_agent(self, id: str) -> DeleteAgentResponse:
        try:
            # Validate request
            if not ObjectId.is_valid(id):
                return DeleteAgentResponse(
                    success=False,
                    id=id,
                    message="Invalid agent ID"
                )

            # Retrieve agent document to get avatar image ID
            data = await get_document(AGENT_COLLECTION_NAME, id)
            if not data:
                return DeleteAgentResponse(
                    success=False,
                    id=id,
                    message="Agent not found"
                )

            avatar_image_id = data.get("avatar_image_id")

            # Delete the avatar image first (if it exists)
            if avatar_image_id and not is_empty_string(avatar_image_id):
                try:
                    await ImageService().delete_image(avatar_image_id, soft_delete=False)
                except Exception as avatar_exc:
                    logging.getLogger("uvicorn.warning").warning(
                        f"Failed to delete avatar image for agent {id}: {avatar_exc}"
                    )
                    # Continue with agent deletion even if avatar deletion fails

            # Delete the agent document
            agent_deleted = await delete_document(AGENT_COLLECTION_NAME, id)
            
            if agent_deleted:
                return DeleteAgentResponse(
                    success=True,
                    id=id,
                    message="Agent deleted successfully"
                )
            else:
                return DeleteAgentResponse(
                    success=False,
                    id=id,
                    message="Failed to delete agent from database"
                )

        except Exception as e:
            error_msg = f"Failed to delete agent {id}: {e}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return DeleteAgentResponse(
                success=False,
                id=id,
                message=error_msg
            )

    async def update_agent_avatar(self, agent_id: str, file_obj, filename: str) -> UpdateAgentAvatarResponse:
        """Upload a new avatar image and update the agent with the image ID"""
        try:
            # Validate request
            if is_empty_string(agent_id):
                return UpdateAgentAvatarResponse(
                    success=False,
                    agent_id=agent_id,
                    image_id="",
                    storage_url="",
                    message="Agent ID is required"
                )
            
            if not file_obj:
                return UpdateAgentAvatarResponse(
                    success=False,
                    agent_id=agent_id,
                    image_id="",
                    storage_url="",
                    message="File object is required"
                )
            
            if is_empty_string(filename):
                return UpdateAgentAvatarResponse(
                    success=False,
                    agent_id=agent_id,
                    image_id="",
                    storage_url="",
                    message="Filename is required"
                )

            # Verify agent exists
            try:
                current_agent = await self.get_agent(agent_id)
                old_avatar_image_id = current_agent.avatar_image_id
            except Exception:
                return UpdateAgentAvatarResponse(
                    success=False,
                    agent_id=agent_id,
                    image_id="",
                    storage_url="",
                    message="Agent not found"
                )

            # Read file content
            file_content = file_obj.read()

            # Create image request
            image_request = CreateImageRequest(
                filename=filename,
                original_filename=filename,
                title=f"Avatar for agent {agent_id}",
                description=f"Avatar image for agent {agent_id}",
                image_type=ImageType.AGENT_AVATAR,
                source_type=ImageSourceType.UPLOAD,
                entity_id=agent_id,
                entity_type="agent",
                file_data=file_content,
            )

            # Upload image using image service
            image_service = ImageService()
            image_response = await image_service.create_image(image_request)
            if not image_response.success:
                return UpdateAgentAvatarResponse(
                    success=False,
                    agent_id=agent_id,
                    image_id="",
                    storage_url="",
                    message=f"Failed to upload avatar image: {image_response.message}"
                )

            # Update agent document with new image ID
            await update_document(
                AGENT_COLLECTION_NAME,
                agent_id,
                {"avatar_image_id": image_response.image_id},
            )

            # Delete old avatar image if it exists
            if old_avatar_image_id and not is_empty_string(old_avatar_image_id):
                try:
                    await image_service.delete_image(old_avatar_image_id)
                except Exception as e:
                    warning = f"Failed to delete old avatar image {old_avatar_image_id}: {e}"
                    logging.getLogger("uvicorn.warning").warning(warning)

            return UpdateAgentAvatarResponse(
                success=True,
                agent_id=agent_id,
                image_id=image_response.image_id,
                storage_url=image_response.storage_url or "",
                message="Avatar updated successfully"
            )

        except Exception as e:
            error_msg = f"Failed to update avatar for agent {agent_id}: {e}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return UpdateAgentAvatarResponse(
                success=False,
                agent_id=agent_id,
                image_id="",
                storage_url="",
                message=error_msg
            )
