import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock, MagicMock
from app.api.agent import router
from app.classes.agent import SearchAgentsResponse, AgentInfo, CreateOrUpdateAgentRequest, CreateOrUpdateAgentResponse
from app.core.constants import LLMModel
import io

app = FastAPI()
app.include_router(router, prefix="/agents")

@pytest.mark.asyncio
async def test_search_agents_api():
    mock_response = SearchAgentsResponse(agents=[
        AgentInfo(id="1", name="Agent 1", description="Desc 1", model=LLMModel.GPT_3_5_TURBO, persona="helpful", tone="friendly", avatar="http://test/url/avatar1.jpg", tools=["chat", "agent-management"]),
        AgentInfo(id="2", name="Agent 2", description="Desc 2", model=LLMModel.GPT_4, persona="expert", tone="serious", avatar="http://test/url/avatar2.jpg", tools=["knowledge-base", "file-storage", "system-health"]),
    ])
    
    with patch("app.services.agent.agent_service.AgentService.search_agents", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/agents/search")
            assert response.status_code == 200
            data = response.json()
            assert "agents" in data
            assert len(data["agents"]) == 2
            assert data["agents"][0]["name"] == "Agent 1"
            assert data["agents"][0]["description"] == "Desc 1"
            assert data["agents"][0]["model"] == LLMModel.GPT_3_5_TURBO
            assert data["agents"][0]["persona"] == "helpful"
            assert data["agents"][0]["tone"] == "friendly"
            assert data["agents"][0]["avatar"] == "http://test/url/avatar1.jpg"
            
            assert data["agents"][1]["name"] == "Agent 2"
            assert data["agents"][1]["description"] == "Desc 2"
            assert data["agents"][1]["model"] == LLMModel.GPT_4
            assert data["agents"][1]["persona"] == "expert"
            assert data["agents"][1]["tone"] == "serious"
            assert data["agents"][1]["avatar"] == "http://test/url/avatar2.jpg"


@pytest.mark.asyncio
async def test_get_agent_api():
    mock_agent = AgentInfo(
        id="test_id",
        name="Test Agent",
        description="Test Description",
        model=LLMModel.GPT_4,
        persona="helpful",
        tone="friendly",
        avatar="http://test/url/avatar.jpg",
        tools=["chat", "agent-management"]
    )
    
    with patch("app.services.agent.agent_service.AgentService.get_agent", new=AsyncMock(return_value=mock_agent)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/agents/id=test_id")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "test_id"
            assert data["name"] == "Test Agent"
            assert data["description"] == "Test Description"
            assert data["model"] == LLMModel.GPT_4
            assert data["persona"] == "helpful"
            assert data["tone"] == "friendly"
            assert data["avatar"] == "http://test/url/avatar.jpg"


@pytest.mark.asyncio
async def test_create_agent_api():
    request_data = {
        "name": "New Agent",
        "description": "New Description",
        "model": LLMModel.GPT_3_5_TURBO,
        "persona": "helpful",
        "tone": "friendly",
        "tools": ["chat", "agent-management"]
    }
    
    mock_response = CreateOrUpdateAgentResponse(
        success=True,
        id="new_agent_id",
        message="Agent created successfully."
    )
    
    with patch("app.services.agent.agent_service.AgentService.create_or_update_agent", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/agents/", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["id"] == "new_agent_id"
            assert data["message"] == "Agent created successfully."


@pytest.mark.asyncio
async def test_update_agent_api():
    request_data = {
        "id": "existing_id",
        "name": "Updated Agent",
        "description": "Updated Description",
        "model": LLMModel.GPT_4,
        "persona": "expert",
        "tone": "serious",
        "tools": ["knowledge-base", "file-storage"]
    }
    
    mock_response = CreateOrUpdateAgentResponse(
        success=True,
        id="existing_id",
        message="Agent updated successfully."
    )
    
    with patch("app.services.agent.agent_service.AgentService.create_or_update_agent", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/agents/", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["id"] == "existing_id"
            assert data["message"] == "Agent updated successfully."


@pytest.mark.asyncio
async def test_create_agent_api_failure():
    request_data = {
        "name": "",  # Invalid empty name
        "description": "Test Description",
        "model": LLMModel.GPT_3_5_TURBO,
        "persona": "helpful",
        "tone": "friendly",
        "tools": ["chat"]
    }
    
    mock_response = CreateOrUpdateAgentResponse(
        success=False,
        id="",
        message="Invalid agent info. Missing value for field: name"
    )
    
    with patch("app.services.agent.agent_service.AgentService.create_or_update_agent", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/agents/", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert data["id"] == ""
            assert "Missing value for field: name" in data["message"]


@pytest.mark.asyncio
async def test_delete_agent_api_success():
    with patch("app.services.agent.agent_service.AgentService.delete_agent", new=AsyncMock(return_value=True)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/agents/delete", params={"id": "test_id"})
            assert response.status_code == 200
            data = response.json()
            assert data is True


@pytest.mark.asyncio
async def test_delete_agent_api_failure():
    with patch("app.services.agent.agent_service.AgentService.delete_agent", new=AsyncMock(return_value=False)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/agents/delete", params={"id": "nonexistent_id"})
            assert response.status_code == 200
            data = response.json()
            assert data is False


@pytest.mark.asyncio
async def test_update_agent_avatar_api_success():
    mock_url = "http://test/url/avatar.jpg"
    
    # Create a mock file
    file_content = b"fake image content"
    file_like = io.BytesIO(file_content)
    
    with patch("app.services.agent.agent_service.AgentService.update_agent_avatar", new=AsyncMock(return_value=mock_url)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            files = {"avatar": ("test_avatar.jpg", file_like, "image/jpeg")}
            response = await ac.post("/agents/avatar", params={"id": "test_id"}, files=files)
            assert response.status_code == 200
            data = response.json()
            assert data["url"] == mock_url


@pytest.mark.asyncio
async def test_update_agent_avatar_api_with_exception():
    # Create a mock file
    file_content = b"fake image content"
    file_like = io.BytesIO(file_content)
    
    with patch("app.services.agent.agent_service.AgentService.update_agent_avatar", new=AsyncMock(side_effect=Exception("Storage error"))):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            files = {"avatar": ("test_avatar.jpg", file_like, "image/jpeg")}
            response = await ac.post("/agents/avatar", params={"id": "test_id"}, files=files)
            assert response.status_code == 500
            data = response.json()
            assert data["detail"] == "Storage error"


@pytest.mark.asyncio
async def test_update_agent_avatar_api_validation_error():
    # Test file upload validation error
    file_content = b"fake image content"
    file_like = io.BytesIO(file_content)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        files = {"avatar": ("", file_like, "image/jpeg")}  # Empty filename causes validation error
        response = await ac.post("/agents/avatar", params={"id": "test_id"}, files=files)
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data