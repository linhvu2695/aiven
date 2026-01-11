import logging
from app.classes.graph import AddTextEpisodeRequest, AddTextEpisodeResponse
from app.core.graph import Graphiti
from app.utils.string.string_utils import is_empty_string


class GraphitiService:
    """Service for managing Graphiti knowledge graph operations"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(GraphitiService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.graphiti = Graphiti()
        self._initialized = True

    def _validate_add_text_episode_request(
        self, request: AddTextEpisodeRequest
    ) -> tuple[bool, str]:
        """Validate add text episode request"""
        # Validate required fields
        if is_empty_string(request.title):
            return False, "Invalid request. Missing title"
        
        if is_empty_string(request.content):
            return False, "Invalid request. Missing content"

        return True, ""

    async def add_text_episode(
        self, request: AddTextEpisodeRequest
    ) -> AddTextEpisodeResponse:
        """
        Add a text episode to the knowledge graph.
        
        Args:
            request: AddTextEpisodeRequest containing title, content, and description
        
        Returns:
            AddTextEpisodeResponse with success status and episode UUID
        """
        valid, error_msg = self._validate_add_text_episode_request(request)
        if not valid:
            logging.getLogger("uvicorn.warning").warning(error_msg)
            return AddTextEpisodeResponse(
                success=False, episode_uuid=None, message=error_msg
            )

        try:
            result = await self.graphiti.add_text_episode(
                name=request.title,
                text=request.content,
                description=request.description,
                reference_time=request.reference_time,
            )
            
            episode_uuid = result.episode.uuid if result and result.episode else None
            
            return AddTextEpisodeResponse(
                success=True,
                episode_uuid=episode_uuid,
                message="Text episode added successfully to knowledge graph.",
            )
        except Exception as e:
            error_message = f"Failed to add text episode: {str(e)}"
            logging.getLogger("uvicorn.error").error(error_message)
            return AddTextEpisodeResponse(
                success=False, episode_uuid=None, message=error_message
            )
