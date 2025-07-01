import pytest
from unittest.mock import patch
from app.services.agent.agent_service import AgentService
from app.classes.agent import AgentInfo, SearchAgentsResponse

@pytest.mark.asyncio
async def test_search_agents_returns_all_agents():
    mock_agents = [
        {
            "_id": "1",
            "name": "Agent 1",
            "description": "Desc 1",
            "model": "o3",
            "persona": "helpful",
            "tone": "friendly",
        },
        {
            "_id": "2",
            "name": "Agent 2",
            "description": "Desc 2",
            "model": "gemini-2.0-flash",
            "persona": "expert",
            "tone": "serious",
        },
    ]
    
    with patch("app.services.agent.agent_service.list_documents", return_value=mock_agents):
        response = await AgentService().search_agents()
        assert isinstance(response, SearchAgentsResponse)
        assert len(response.agents) == 2
        
        assert response.agents[0].name == "Agent 1"
        assert response.agents[0].description == "Desc 1"
        assert response.agents[0].model == "o3"
        assert response.agents[0].persona == "helpful"
        assert response.agents[0].tone == "friendly"

        assert response.agents[1].name == "Agent 2"
        assert response.agents[1].description == "Desc 2"
        assert response.agents[1].model == "gemini-2.0-flash"
        assert response.agents[1].persona == "expert"
        assert response.agents[1].tone == "serious"