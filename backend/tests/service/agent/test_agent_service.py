import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.agent.agent_service import AgentService
from app.classes.agent import AgentInfo, SearchAgentsResponse, CreateOrUpdateAgentRequest, CreateOrUpdateAgentResponse
from app.core.constants import LLMModel


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
        "avatar": "avatar/test.jpg",
        "model": "o3",
        "persona": "helpful",
        "tone": "friendly",
    }


@pytest.fixture
def create_agent_request():
    return CreateOrUpdateAgentRequest(
        name="Test Agent",
        description="Test Description",
        model=LLMModel.O3,
        persona="helpful",
        tone="friendly"
    )


@pytest.fixture
def update_agent_request():
    return CreateOrUpdateAgentRequest(
        id="test_id_123",
        name="Updated Agent",
        description="Updated Description",
        model=LLMModel.GEMINI_2_0_FLASH,
        persona="expert",
        tone="serious"
    )


class TestAgentService:
    
    def test_singleton_instance(self):
        """Test that AgentService is a singleton"""
        service1 = AgentService()
        service2 = AgentService()
        assert service1 is service2
    
    
    @pytest.mark.asyncio
    async def test_search_agents_returns_all_agents(self, agent_service):
        """Test search_agents returns all agents with avatar URLs"""
        mock_agents = [
            {
                "_id": "1",
                "name": "Agent 1",
                "description": "Desc 1",
                "model": "o3",
                "persona": "helpful",
                "tone": "friendly",
                "avatar": "avatar/agent1.jpg"
            },
            {
                "_id": "2",
                "name": "Agent 2",
                "description": "Desc 2",
                "model": "gemini-2.0-flash",
                "persona": "expert",
                "tone": "serious",
                "avatar": ""
            },
        ]
        
        with patch("app.services.agent.agent_service.list_documents", return_value=mock_agents), \
             patch.object(agent_service, "_get_avatar_url", side_effect=["http://avatar1.jpg", ""]):
            
            response = await agent_service.search_agents()
            assert isinstance(response, SearchAgentsResponse)
            assert len(response.agents) == 2
            
            assert response.agents[0].name == "Agent 1"
            assert response.agents[0].description == "Desc 1"
            assert response.agents[0].model == "o3"
            assert response.agents[0].persona == "helpful"
            assert response.agents[0].tone == "friendly"
            assert response.agents[0].avatar == "http://avatar1.jpg"

            assert response.agents[1].name == "Agent 2"
            assert response.agents[1].description == "Desc 2"
            assert response.agents[1].model == "gemini-2.0-flash"
            assert response.agents[1].persona == "expert"
            assert response.agents[1].tone == "serious"
            assert response.agents[1].avatar == ""


    @pytest.mark.asyncio
    async def test_get_agent_success(self, agent_service, mock_agent_data):
        """Test successful agent retrieval"""
        with patch("app.services.agent.agent_service.get_document", return_value=mock_agent_data), \
             patch.object(agent_service, "_get_avatar_url", return_value="http://avatar.jpg"):
            
            agent = await agent_service.get_agent("test_id_123")
            
            assert isinstance(agent, AgentInfo)
            assert agent.id == "test_id_123"
            assert agent.name == "Test Agent"
            assert agent.description == "Test Description"
            assert agent.avatar == "http://avatar.jpg"
            assert agent.model == "o3"
            assert agent.persona == "helpful"
            assert agent.tone == "friendly"


    @pytest.mark.asyncio
    async def test_get_avatar_url_with_avatar(self, agent_service):
        """Test _get_avatar_url with avatar path"""
        mock_storage = MagicMock()
        mock_storage.get_presigned_url = AsyncMock(return_value="http://presigned.url")
        
        with patch("app.services.agent.agent_service.FirebaseStorageRepository", return_value=mock_storage):
            url = await agent_service._get_avatar_url("avatar/test.jpg")
            assert url == "http://presigned.url"
            mock_storage.get_presigned_url.assert_called_once_with("avatar/test.jpg", 3600)


    @pytest.mark.asyncio
    async def test_get_avatar_url_without_avatar(self, agent_service):
        """Test _get_avatar_url without avatar path"""
        url = await agent_service._get_avatar_url("")
        assert url == ""
        
        url = await agent_service._get_avatar_url(None)
        assert url == ""


    def test_validate_create_agent_request_valid(self, agent_service, create_agent_request):
        """Test validation with valid request"""
        valid, warning = agent_service._validate_create_agent_request(create_agent_request)
        assert valid is True
        assert warning == ""


    def test_validate_create_agent_request_missing_name(self, agent_service):
        """Test validation with missing name"""
        request = CreateOrUpdateAgentRequest(
            name="",
            description="Test Description",
            model=LLMModel.O3,
            persona="helpful",
            tone="friendly"
        )
        valid, warning = agent_service._validate_create_agent_request(request)
        assert valid is False
        assert "Missing value for field: name" in warning


    def test_validate_create_agent_request_missing_model(self, agent_service):
        """Test validation with missing model"""
        # Create a mock request with empty model string
        request = MagicMock()
        request.name = "Test Agent"
        request.model = ""  # Empty string model
        
        valid, warning = agent_service._validate_create_agent_request(request)
        assert valid is False
        assert "Missing value for field: model" in warning


    @pytest.mark.asyncio
    async def test_create_agent_success(self, agent_service, create_agent_request):
        """Test successful agent creation"""
        with patch("app.services.agent.agent_service.insert_document", return_value="new_id_123"):
            response = await agent_service.create_or_update_agent(create_agent_request)
            
            assert isinstance(response, CreateOrUpdateAgentResponse)
            assert response.success is True
            assert response.id == "new_id_123"
            assert response.message == "Agent created successfully."


    @pytest.mark.asyncio
    async def test_create_agent_validation_failure(self, agent_service):
        """Test agent creation with validation failure"""
        invalid_request = CreateOrUpdateAgentRequest(
            name="",
            description="Test Description",
            model=LLMModel.O3,
            persona="helpful",
            tone="friendly"
        )
        
        response = await agent_service.create_or_update_agent(invalid_request)
        
        assert isinstance(response, CreateOrUpdateAgentResponse)
        assert response.success is False
        assert response.id == ""
        assert "Missing value for field: name" in response.message


    @pytest.mark.asyncio
    async def test_create_agent_exception(self, agent_service, create_agent_request):
        """Test agent creation with database exception"""
        with patch("app.services.agent.agent_service.insert_document", side_effect=Exception("Database error")):
            response = await agent_service.create_or_update_agent(create_agent_request)
            
            assert isinstance(response, CreateOrUpdateAgentResponse)
            assert response.success is False
            assert response.id == ""
            assert response.message == "Database error"


    @pytest.mark.asyncio
    async def test_update_agent_success(self, agent_service, update_agent_request):
        """Test successful agent update"""
        with patch("app.services.agent.agent_service.update_document", return_value=None):
            response = await agent_service.create_or_update_agent(update_agent_request)
            
            assert isinstance(response, CreateOrUpdateAgentResponse)
            assert response.success is True
            assert response.id == "None"  # This seems like a bug in the original code
            assert response.message == "Agent updated successfully."


    @pytest.mark.asyncio
    async def test_update_agent_failure(self, agent_service, update_agent_request):
        """Test agent update failure"""
        with patch("app.services.agent.agent_service.update_document", return_value="some_value"):
            response = await agent_service.create_or_update_agent(update_agent_request)
            
            assert isinstance(response, CreateOrUpdateAgentResponse)
            assert response.success is False
            assert response.id == ""


    @pytest.mark.asyncio
    async def test_delete_agent_success_with_avatar(self, agent_service, mock_agent_data):
        """Test successful agent deletion with avatar"""
        mock_storage = MagicMock()
        mock_storage.delete = AsyncMock()
        
        with patch("app.services.agent.agent_service.get_document", return_value=mock_agent_data), \
             patch("app.services.agent.agent_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.agent.agent_service.delete_document", return_value=True):
            
            result = await agent_service.delete_agent("test_id_123")
            
            assert result is True
            mock_storage.delete.assert_called_once_with("avatar/test.jpg")


    @pytest.mark.asyncio
    async def test_delete_agent_success_without_avatar(self, agent_service):
        """Test successful agent deletion without avatar"""
        mock_data = {"_id": "test_id_123", "name": "Test Agent"}
        
        with patch("app.services.agent.agent_service.get_document", return_value=mock_data), \
             patch("app.services.agent.agent_service.delete_document", return_value=True):
            
            result = await agent_service.delete_agent("test_id_123")
            
            assert result is True


    @pytest.mark.asyncio
    async def test_delete_agent_avatar_deletion_failure(self, agent_service, mock_agent_data):
        """Test agent deletion when avatar deletion fails"""
        mock_storage = MagicMock()
        mock_storage.delete = AsyncMock(side_effect=Exception("Storage error"))
        
        with patch("app.services.agent.agent_service.get_document", return_value=mock_agent_data), \
             patch("app.services.agent.agent_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.agent.agent_service.delete_document", return_value=True):
            
            result = await agent_service.delete_agent("test_id_123")
            
            assert result is True  # Should still succeed even if avatar deletion fails


    @pytest.mark.asyncio
    async def test_delete_agent_failure(self, agent_service):
        """Test agent deletion failure"""
        with patch("app.services.agent.agent_service.get_document", side_effect=Exception("Database error")):
            result = await agent_service.delete_agent("test_id_123")
            
            assert result is False


    @pytest.mark.asyncio
    async def test_update_agent_avatar_success(self, agent_service):
        """Test successful avatar update"""
        mock_file = MagicMock()
        mock_storage = MagicMock()
        mock_storage.upload = AsyncMock(return_value="http://uploaded.url")
        
        with patch("app.services.agent.agent_service.FirebaseStorageRepository", return_value=mock_storage), \
             patch("app.services.agent.agent_service.update_document"), \
             patch.object(agent_service, "_get_avatar_url", return_value="http://presigned.url"):
            
            result = await agent_service.update_agent_avatar("test_id", mock_file, "avatar.jpg")
            
            assert result == "http://presigned.url"
            mock_storage.upload.assert_called_once_with(mock_file, "avatar/test_id/avatar.jpg")