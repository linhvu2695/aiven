import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.agent.agent_service import AgentService
from app.classes.agent import AgentInfo, SearchAgentsResponse, CreateOrUpdateAgentRequest, CreateOrUpdateAgentResponse, DeleteAgentResponse, UpdateAgentAvatarResponse
from app.services.chat.chat_constants import LLMModel
from app.classes.image import ImageUrlInfo


@pytest.fixture
def agent_service():
    """Create a fresh instance for each test"""
    # Reset the singleton instance
    AgentService._instance = None
    return AgentService()


@pytest.fixture
def mock_agent_data():
    return {
        "_id": "test_id_123",
        "name": "Test Agent",
        "description": "Test Description",
        "avatar_image_id": "image_123",
        "model": "o3",
        "persona": "helpful",
        "tone": "friendly",
        "tools": ["agent-management", "chat", "knowledge-base"]
    }


@pytest.fixture
def create_agent_request():
    return CreateOrUpdateAgentRequest(
        name="Test Agent",
        description="Test Description",
        model=LLMModel.O3,
        persona="helpful",
        tone="friendly",
        tools=["chat", "system-health"]
    )


@pytest.fixture
def update_agent_request():
    return CreateOrUpdateAgentRequest(
        id="test_id_123",
        name="Updated Agent",
        description="Updated Description",
        model=LLMModel.GEMINI_2_0_FLASH,
        persona="expert",
        tone="serious",
        tools=["agent-management", "file-storage", "knowledge-base"]
    )


class TestAgentService:
    
    def test_singleton_instance(self):
        """Test that AgentService is a singleton"""
        service1 = AgentService()
        service2 = AgentService()
        assert service1 is service2
    
    
    @pytest.mark.asyncio
    async def test_search_agents_returns_all_agents(self, agent_service: AgentService):
        """Test search_agents returns all agents with avatar image IDs"""
        mock_agents = [
            {
                "_id": "1",
                "name": "Agent 1",
                "description": "Desc 1",
                "model": "o3",
                "persona": "helpful",
                "tone": "friendly",
                "avatar_image_id": "image_1",
                "tools": ["chat", "agent-management"]
            },
            {
                "_id": "2",
                "name": "Agent 2",
                "description": "Desc 2",
                "model": "gemini-2.0-flash",
                "persona": "expert",
                "tone": "serious",
                "avatar_image_id": None,
                "tools": ["knowledge-base", "file-storage", "system-health"]
            },
        ]
        
        with patch("app.services.agent.agent_service.list_documents", return_value=mock_agents), \
             patch.object(agent_service, "_get_avatar_url", side_effect=["http://test.com/image_1.jpg", ""]):
            
            response = await agent_service.search_agents()
            assert isinstance(response, SearchAgentsResponse)
            assert len(response.agents) == 2
            
            assert response.agents[0].name == "Agent 1"
            assert response.agents[0].description == "Desc 1"
            assert response.agents[0].model == "o3"
            assert response.agents[0].persona == "helpful"
            assert response.agents[0].tone == "friendly"
            assert response.agents[0].avatar_image_id == "image_1"
            assert response.agents[0].avatar_image_url == "http://test.com/image_1.jpg"
            assert response.agents[0].tools == ["chat", "agent-management"]

            assert response.agents[1].name == "Agent 2"
            assert response.agents[1].description == "Desc 2"
            assert response.agents[1].model == "gemini-2.0-flash"
            assert response.agents[1].persona == "expert"
            assert response.agents[1].tone == "serious"
            assert response.agents[1].avatar_image_id is None
            assert response.agents[1].avatar_image_url == ""
            assert response.agents[1].tools == ["knowledge-base", "file-storage", "system-health"]


    @pytest.mark.asyncio
    async def test_get_agent_success(self, agent_service: AgentService, mock_agent_data):
        """Test successful agent retrieval"""
        with patch("app.services.agent.agent_service.get_document", return_value=mock_agent_data), \
             patch.object(agent_service, "_get_avatar_url", return_value="http://avatar.jpg"):
            
            agent = await agent_service.get_agent("test_id_123")
            
            assert isinstance(agent, AgentInfo)
            assert agent.id == "test_id_123"
            assert agent.name == "Test Agent"
            assert agent.description == "Test Description"
            assert agent.avatar_image_id == "image_123"
            assert agent.avatar_image_url == "http://avatar.jpg"
            assert agent.model == "o3"
            assert agent.persona == "helpful"
            assert agent.tone == "friendly"
            assert agent.tools == ["agent-management", "chat", "knowledge-base"]


    @pytest.mark.asyncio
    async def test_get_avatar_url_with_avatar(self, agent_service: AgentService):
        """Test _get_avatar_url with avatar image ID"""        
        mock_image_service = MagicMock()
        mock_url_response = ImageUrlInfo(
            image_id="image_123",
            url="http://presigned.url",
            expires_at=None,
            success=True,
            message=""
        )
        mock_image_service.get_image_presigned_url = AsyncMock(return_value=mock_url_response)
        
        with patch("app.services.agent.agent_service.ImageService", return_value=mock_image_service):
            url = await agent_service._get_avatar_url("image_123")
            assert url == "http://presigned.url"
            mock_image_service.get_image_presigned_url.assert_called_once_with("image_123")


    @pytest.mark.asyncio
    async def test_get_avatar_url_without_avatar(self, agent_service: AgentService):
        """Test _get_avatar_url without avatar image ID"""
        url = await agent_service._get_avatar_url("")
        assert url == ""
        
        url = await agent_service._get_avatar_url("")
        assert url == ""


    def test_validate_create_agent_request_valid(self, agent_service: AgentService, create_agent_request: CreateOrUpdateAgentRequest):
        """Test validation with valid request"""
        valid, warning = agent_service._validate_create_agent_request(create_agent_request)
        assert valid is True
        assert warning == ""


    def test_validate_create_agent_request_missing_name(self, agent_service: AgentService):
        """Test validation with missing name"""
        request = CreateOrUpdateAgentRequest(
            name="",
            description="Test Description",
            model=LLMModel.O3,
            persona="helpful",
            tone="friendly",
            tools=["chat", "system-health"]
        )
        valid, warning = agent_service._validate_create_agent_request(request)
        assert valid is False
        assert "Missing value for field: name" in warning


    def test_validate_create_agent_request_missing_model(self, agent_service: AgentService):
        """Test validation with missing model"""
        # Create a mock request with empty model string
        request = MagicMock()
        request.name = "Test Agent"
        request.model = ""  # Empty string model
        
        valid, warning = agent_service._validate_create_agent_request(request)
        assert valid is False
        assert "Missing value for field: model" in warning


    @pytest.mark.asyncio
    async def test_create_agent_success(self, agent_service: AgentService, create_agent_request):
        """Test successful agent creation"""
        with patch("app.services.agent.agent_service.insert_document", return_value="new_id_123"):
            response = await agent_service.create_or_update_agent(create_agent_request)
            
            assert isinstance(response, CreateOrUpdateAgentResponse)
            assert response.success is True
            assert response.id == "new_id_123"
            assert response.message == "Agent created successfully."


    @pytest.mark.asyncio
    async def test_create_agent_validation_failure(self, agent_service: AgentService):
        """Test agent creation with validation failure"""
        invalid_request = CreateOrUpdateAgentRequest(
            name="",
            description="Test Description",
            model=LLMModel.O3,
            persona="helpful",
            tone="friendly",
            tools=["chat", "agent-management"]
        )
        
        response = await agent_service.create_or_update_agent(invalid_request)
        
        assert isinstance(response, CreateOrUpdateAgentResponse)
        assert response.success is False
        assert response.id == ""
        assert "Missing value for field: name" in response.message


    @pytest.mark.asyncio
    async def test_create_agent_exception(self, agent_service: AgentService, create_agent_request):
        """Test agent creation with database exception"""
        with patch("app.services.agent.agent_service.insert_document", side_effect=Exception("Database error")):
            response = await agent_service.create_or_update_agent(create_agent_request)
            
            assert isinstance(response, CreateOrUpdateAgentResponse)
            assert response.success is False
            assert response.id == ""
            assert response.message == "Database error"


    @pytest.mark.asyncio
    async def test_update_agent_success(self, agent_service: AgentService, update_agent_request):
        """Test successful agent update"""
        with patch("app.services.agent.agent_service.update_document", return_value="test_id_123"):
            response = await agent_service.create_or_update_agent(update_agent_request)
            
            assert isinstance(response, CreateOrUpdateAgentResponse)
            assert response.success is True
            assert response.id == "test_id_123"
            assert response.message == "Agent updated successfully."


    @pytest.mark.asyncio
    async def test_update_agent_failure(self, agent_service: AgentService, update_agent_request):
        """Test agent update failure"""
        with patch("app.services.agent.agent_service.update_document", side_effect=Exception("Database error")):
            response = await agent_service.create_or_update_agent(update_agent_request)
            
            assert isinstance(response, CreateOrUpdateAgentResponse)
            assert response.success is False
            assert response.id == ""
            assert response.message == "Database error"


    @pytest.mark.asyncio
    async def test_delete_agent_success_with_avatar(self, agent_service: AgentService, mock_agent_data):
        """Test successful agent deletion with avatar"""
        from bson import ObjectId
        
        # Use a valid ObjectId format
        valid_id = str(ObjectId())
        mock_agent_data["_id"] = valid_id
        
        mock_image_service = MagicMock()
        mock_image_service.delete_image = AsyncMock()
        
        with patch("app.services.agent.agent_service.get_document", return_value=mock_agent_data), \
             patch("app.services.agent.agent_service.ImageService", return_value=mock_image_service), \
             patch("app.services.agent.agent_service.delete_document", return_value=True):
            
            result = await agent_service.delete_agent(valid_id)
            
            assert isinstance(result, DeleteAgentResponse)
            assert result.success is True
            assert result.id == valid_id
            assert result.message == "Agent deleted successfully"
            mock_image_service.delete_image.assert_called_once_with("image_123", soft_delete=False)


    @pytest.mark.asyncio
    async def test_delete_agent_success_without_avatar(self, agent_service: AgentService):
        """Test successful agent deletion without avatar"""
        from bson import ObjectId
        
        # Use a valid ObjectId format
        valid_id = str(ObjectId())
        mock_data = {"_id": valid_id, "name": "Test Agent", "avatar_image_id": None}
        
        with patch("app.services.agent.agent_service.get_document", return_value=mock_data), \
             patch("app.services.agent.agent_service.delete_document", return_value=True):
            
            result = await agent_service.delete_agent(valid_id)
            
            assert isinstance(result, DeleteAgentResponse)
            assert result.success is True
            assert result.id == valid_id
            assert result.message == "Agent deleted successfully"


    @pytest.mark.asyncio
    async def test_delete_agent_avatar_deletion_failure(self, agent_service: AgentService, mock_agent_data):
        """Test agent deletion when avatar deletion fails"""
        from bson import ObjectId
        
        # Use a valid ObjectId format
        valid_id = str(ObjectId())
        mock_agent_data["_id"] = valid_id
        
        mock_image_service = MagicMock()
        mock_image_service.delete_image = AsyncMock(side_effect=Exception("Image service error"))
        
        with patch("app.services.agent.agent_service.get_document", return_value=mock_agent_data), \
             patch("app.services.agent.agent_service.ImageService", return_value=mock_image_service), \
             patch("app.services.agent.agent_service.delete_document", return_value=True):
            
            result = await agent_service.delete_agent(valid_id)
            
            assert isinstance(result, DeleteAgentResponse)
            assert result.success is True  # Should still succeed even if avatar deletion fails
            assert result.id == valid_id
            assert result.message == "Agent deleted successfully"


    @pytest.mark.asyncio
    async def test_delete_agent_failure(self, agent_service: AgentService):
        """Test agent deletion failure"""
        from bson import ObjectId
        
        # Use a valid ObjectId format
        valid_id = str(ObjectId())
        
        with patch("app.services.agent.agent_service.get_document", side_effect=Exception("Database error")):
            result = await agent_service.delete_agent(valid_id)
            
            assert isinstance(result, DeleteAgentResponse)
            assert result.success is False
            assert result.id == valid_id
            assert f"Failed to delete agent {valid_id}: Database error" in result.message

    @pytest.mark.asyncio
    async def test_delete_agent_not_found(self, agent_service: AgentService):
        """Test agent deletion when agent doesn't exist"""
        from bson import ObjectId
        
        # Use a valid ObjectId format
        valid_id = str(ObjectId())
        
        with patch("app.services.agent.agent_service.get_document", return_value=None):
            result = await agent_service.delete_agent(valid_id)
            
            assert isinstance(result, DeleteAgentResponse)
            assert result.success is False
            assert result.id == valid_id
            assert result.message == "Agent not found"

    @pytest.mark.asyncio
    async def test_delete_agent_invalid_id(self, agent_service: AgentService):
        """Test agent deletion with invalid ID"""
        result = await agent_service.delete_agent("invalid_id_format")
        
        assert isinstance(result, DeleteAgentResponse)
        assert result.success is False
        assert result.id == "invalid_id_format"
        assert result.message == "Invalid agent ID"

    @pytest.mark.asyncio
    async def test_delete_agent_empty_id(self, agent_service: AgentService):
        """Test agent deletion with empty ID"""
        result = await agent_service.delete_agent("")
        
        assert isinstance(result, DeleteAgentResponse)
        assert result.success is False
        assert result.id == ""
        assert result.message == "Invalid agent ID"

    @pytest.mark.asyncio
    async def test_delete_agent_database_deletion_failure(self, agent_service: AgentService):
        """Test when delete_document returns False"""
        from bson import ObjectId
        
        # Use a valid ObjectId format
        valid_id = str(ObjectId())
        mock_data = {"_id": valid_id, "name": "Test Agent", "avatar_image_id": None}
        
        with patch("app.services.agent.agent_service.get_document", return_value=mock_data), \
             patch("app.services.agent.agent_service.delete_document", return_value=False):
            
            result = await agent_service.delete_agent(valid_id)
            
            assert isinstance(result, DeleteAgentResponse)
            assert result.success is False
            assert result.id == valid_id
            assert result.message == "Failed to delete agent from database"


    @pytest.mark.asyncio
    async def test_update_agent_avatar_success(self, agent_service: AgentService):
        """Test successful avatar update"""
        from app.classes.image import ImageCreateResponse
        
        mock_file = MagicMock()
        mock_file.read = MagicMock(return_value=b"fake image data")
        
        # Mock agent exists
        mock_agent = AgentInfo(
            id="test_id",
            name="Test Agent",
            description="Test Description",
            avatar_image_id="old_image_123",
            avatar_image_url="",
            model=LLMModel.O3,
            persona="helpful",
            tone="friendly",
            tools=["chat"]
        )
        
        mock_image_service = MagicMock()
        mock_upload_response = ImageCreateResponse(
            success=True,
            image_id="new_image_123",
            storage_path="images/agent_test_id/avatar.jpg",
            storage_url="http://storage.url/image.jpg",
            message="Success"
        )
        mock_image_service.create_image = AsyncMock(return_value=mock_upload_response)
        mock_image_service.delete_image = AsyncMock()
        
        with patch.object(agent_service, "get_agent", return_value=mock_agent), \
             patch("app.services.agent.agent_service.ImageService", return_value=mock_image_service), \
             patch("app.services.agent.agent_service.update_document"):
            
            result = await agent_service.update_agent_avatar("test_id", mock_file, "avatar.jpg")
            
            assert isinstance(result, UpdateAgentAvatarResponse)
            assert result.success is True
            assert result.agent_id == "test_id"
            assert result.image_id == "new_image_123"
            assert result.storage_url == "http://storage.url/image.jpg"
            assert result.message == "Avatar updated successfully"
            mock_image_service.create_image.assert_called_once()
            mock_image_service.delete_image.assert_called_once_with("old_image_123")

    @pytest.mark.asyncio
    async def test_update_agent_avatar_empty_agent_id(self, agent_service: AgentService):
        """Test avatar update with empty agent ID"""
        mock_file = MagicMock()
        
        result = await agent_service.update_agent_avatar("", mock_file, "avatar.jpg")
        
        assert isinstance(result, UpdateAgentAvatarResponse)
        assert result.success is False
        assert result.agent_id == ""
        assert result.message == "Agent ID is required"

    @pytest.mark.asyncio
    async def test_update_agent_avatar_no_file(self, agent_service: AgentService):
        """Test avatar update with no file"""
        result = await agent_service.update_agent_avatar("test_id", None, "avatar.jpg")
        
        assert isinstance(result, UpdateAgentAvatarResponse)
        assert result.success is False
        assert result.agent_id == "test_id"
        assert result.message == "File object is required"

    @pytest.mark.asyncio
    async def test_update_agent_avatar_empty_filename(self, agent_service: AgentService):
        """Test avatar update with empty filename"""
        mock_file = MagicMock()
        
        result = await agent_service.update_agent_avatar("test_id", mock_file, "")
        
        assert isinstance(result, UpdateAgentAvatarResponse)
        assert result.success is False
        assert result.agent_id == "test_id"
        assert result.message == "Filename is required"

    @pytest.mark.asyncio
    async def test_update_agent_avatar_agent_not_found(self, agent_service: AgentService):
        """Test avatar update when agent doesn't exist"""
        mock_file = MagicMock()
        
        with patch.object(agent_service, "get_agent", side_effect=Exception("Agent not found")):
            result = await agent_service.update_agent_avatar("nonexistent_id", mock_file, "avatar.jpg")
            
            assert isinstance(result, UpdateAgentAvatarResponse)
            assert result.success is False
            assert result.agent_id == "nonexistent_id"
            assert result.message == "Agent not found"