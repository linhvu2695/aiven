import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock
from app.api.agent import router
from app.classes.agent import SearchAgentsResponse, AgentInfo
from app.core.constants import LLMModel

app = FastAPI()
app.include_router(router, prefix="/agents")

@pytest.mark.asyncio
async def test_search_agents_api():
    mock_response = SearchAgentsResponse(agents=[
        AgentInfo(id="1", name="Agent 1", description="Desc 1", model=LLMModel.GPT_3_5_TURBO, persona="helpful", tone="friendly", avatar="http://test/url/avatar1.jpg"),
        AgentInfo(id="2", name="Agent 2", description="Desc 2", model=LLMModel.GPT_4, persona="expert", tone="serious", avatar="http://test/url/avatar2.jpg"),
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