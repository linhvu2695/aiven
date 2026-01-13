import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
from app.services.graph.graphiti_service import GraphitiService
from app.classes.graph import AddTextEpisodeRequest, AddTextEpisodeResponse


@pytest.fixture
def graphiti_service():
    """Create a fresh instance for each test"""
    # Reset the singleton instance
    GraphitiService._instance = None
    with patch("app.services.graph.graphiti_service.Graphiti"):
        service = GraphitiService()
        return service


@pytest.fixture
def valid_request() -> AddTextEpisodeRequest:
    return AddTextEpisodeRequest(
        title="Test Episode",
        content="This is test content for the knowledge graph.",
        description="Test description",
        reference_time=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def request_without_optional_fields():
    return AddTextEpisodeRequest(
        title="Test Episode",
        content="This is test content.",
    )


class TestGraphitiService:

    def test_singleton_instance(self):
        """Test that GraphitiService is a singleton"""
        GraphitiService._instance = None
        with patch("app.services.graph.graphiti_service.Graphiti"):
            service1 = GraphitiService()
            service2 = GraphitiService()
            assert service1 is service2


    def test_validate_request_valid(self, graphiti_service: GraphitiService, valid_request):
        """Test validation with valid request"""
        valid, error_msg = graphiti_service._validate_add_text_episode_request(valid_request)
        assert valid is True
        assert error_msg == ""


    def test_validate_request_missing_title(self, graphiti_service: GraphitiService):
        """Test validation with missing title"""
        request = AddTextEpisodeRequest(
            title="",
            content="Test content",
        )
        valid, error_msg = graphiti_service._validate_add_text_episode_request(request)
        assert valid is False
        assert "Missing title" in error_msg


    def test_validate_request_missing_content(self, graphiti_service: GraphitiService):
        """Test validation with missing content"""
        request = AddTextEpisodeRequest(
            title="Test Title",
            content="",
        )
        valid, error_msg = graphiti_service._validate_add_text_episode_request(request)
        assert valid is False
        assert "Missing content" in error_msg


    def test_validate_request_whitespace_only_title(self, graphiti_service: GraphitiService):
        """Test validation with whitespace-only title"""
        request = AddTextEpisodeRequest(
            title="   ",
            content="Test content",
        )
        valid, error_msg = graphiti_service._validate_add_text_episode_request(request)
        assert valid is False
        assert "Missing title" in error_msg


    def test_validate_request_whitespace_only_content(self, graphiti_service: GraphitiService):
        """Test validation with whitespace-only content"""
        request = AddTextEpisodeRequest(
            title="Test Title",
            content="   ",
        )
        valid, error_msg = graphiti_service._validate_add_text_episode_request(request)
        assert valid is False
        assert "Missing content" in error_msg


    @pytest.mark.asyncio
    async def test_add_text_episode_success(self, graphiti_service: GraphitiService, valid_request: AddTextEpisodeRequest):
        """Test successful text episode addition"""
        # Mock the episode result
        mock_episode = MagicMock()
        mock_episode.uuid = "test-uuid-123"
        mock_result = MagicMock()
        mock_result.episode = mock_episode

        graphiti_service.graphiti.add_text_episode = AsyncMock(return_value=mock_result)

        response = await graphiti_service.add_text_episode(valid_request)

        assert isinstance(response, AddTextEpisodeResponse)
        assert response.success is True
        assert response.episode_uuid == "test-uuid-123"
        assert "successfully" in response.message

        # Verify the graphiti method was called with correct parameters
        graphiti_service.graphiti.add_text_episode.assert_called_once_with(
            name=valid_request.title,
            text=valid_request.content,
            description=valid_request.description,
            reference_time=valid_request.reference_time,
        )


    @pytest.mark.asyncio
    async def test_add_text_episode_success_without_optional_fields(
        self, graphiti_service: GraphitiService, request_without_optional_fields: AddTextEpisodeRequest
    ):
        """Test successful text episode addition without optional fields"""
        mock_episode = MagicMock()
        mock_episode.uuid = "test-uuid-456"
        mock_result = MagicMock()
        mock_result.episode = mock_episode

        graphiti_service.graphiti.add_text_episode = AsyncMock(return_value=mock_result)

        response = await graphiti_service.add_text_episode(request_without_optional_fields)

        assert isinstance(response, AddTextEpisodeResponse)
        assert response.success is True
        assert response.episode_uuid == "test-uuid-456"

        # Verify None is passed for optional fields
        graphiti_service.graphiti.add_text_episode.assert_called_once_with(
            name=request_without_optional_fields.title,
            text=request_without_optional_fields.content,
            description=None,
            reference_time=None,
        )


    @pytest.mark.asyncio
    async def test_add_text_episode_validation_failure_missing_title(
        self, graphiti_service: GraphitiService
    ):
        """Test text episode addition with validation failure - missing title"""
        request = AddTextEpisodeRequest(
            title="",
            content="Test content",
        )

        response = await graphiti_service.add_text_episode(request)

        assert isinstance(response, AddTextEpisodeResponse)
        assert response.success is False
        assert response.episode_uuid is None
        assert "Missing title" in response.message


    @pytest.mark.asyncio
    async def test_add_text_episode_validation_failure_missing_content(
        self, graphiti_service: GraphitiService
    ):
        """Test text episode addition with validation failure - missing content"""
        request = AddTextEpisodeRequest(
            title="Test Title",
            content="",
        )

        response = await graphiti_service.add_text_episode(request)

        assert isinstance(response, AddTextEpisodeResponse)
        assert response.success is False
        assert response.episode_uuid is None
        assert "Missing content" in response.message


    @pytest.mark.asyncio
    async def test_add_text_episode_exception(self, graphiti_service: GraphitiService, valid_request):
        """Test text episode addition with exception from Graphiti"""
        graphiti_service.graphiti.add_text_episode = AsyncMock(
            side_effect=Exception("Neo4j connection error")
        )

        response = await graphiti_service.add_text_episode(valid_request)

        assert isinstance(response, AddTextEpisodeResponse)
        assert response.success is False
        assert response.episode_uuid is None
        assert "Failed to add text episode" in response.message
        assert "Neo4j connection error" in response.message


    @pytest.mark.asyncio
    async def test_add_text_episode_null_result(self, graphiti_service: GraphitiService, valid_request):
        """Test text episode addition when result is None"""
        graphiti_service.graphiti.add_text_episode = AsyncMock(return_value=None)

        response = await graphiti_service.add_text_episode(valid_request)

        assert isinstance(response, AddTextEpisodeResponse)
        assert response.success is True
        assert response.episode_uuid is None
        assert "successfully" in response.message


    @pytest.mark.asyncio
    async def test_add_text_episode_null_episode_in_result(
        self, graphiti_service: GraphitiService, valid_request
    ):
        """Test text episode addition when result.episode is None"""
        mock_result = MagicMock()
        mock_result.episode = None

        graphiti_service.graphiti.add_text_episode = AsyncMock(return_value=mock_result)

        response = await graphiti_service.add_text_episode(valid_request)

        assert isinstance(response, AddTextEpisodeResponse)
        assert response.success is True
        assert response.episode_uuid is None
        assert "successfully" in response.message
