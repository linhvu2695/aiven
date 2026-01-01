import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from app.services.agent.agent_eval_service import AgentEvalService
from app.services.agent.agent_service import AgentService
from app.services.tool.tool_service import ToolService
from app.services.chat.chat_service import ChatService
from app.classes.agent import (
    AgentInfo,
    EvaluateAgentRequest,
    EvaluateAgentResponse
)
from app.classes.chat import ChatMessage
from app.services.chat.chat_constants import LLMModel


# Test constants
TEST_AGENT_ID = "test-agent-id"
TEST_AGENT_NAME = "Test Agent"


@pytest.fixture
def agent_eval_service():
    """Create a fresh instance for each test"""
    # Reset the singleton instance
    AgentEvalService._instance = None
    return AgentEvalService()


@pytest.fixture
def sample_agent():
    """Sample agent for testing"""
    return AgentInfo(
        id=TEST_AGENT_ID,
        name=TEST_AGENT_NAME,
        description="Test description",
        model=LLMModel.GPT_4O,
        persona="You are a helpful assistant",
        tone="friendly",
        avatar_image_id="test_avatar_id",
        avatar_image_url="http://test.com/avatar.jpg",
        tools=[]
    )


@pytest.fixture
def sample_agent_with_tools():
    """Sample agent with tools for testing"""
    return AgentInfo(
        id=TEST_AGENT_ID,
        name=TEST_AGENT_NAME,
        description="Test description",
        model=LLMModel.GPT_4O,
        persona="You are a helpful assistant",
        tone="friendly",
        avatar_image_id="test_avatar_id",
        avatar_image_url="http://test.com/avatar.jpg",
        tools=["tool1", "tool2"]
    )


@pytest.fixture
def sample_input_messages():
    """Sample input messages for testing"""
    return [
        ChatMessage(role="user", content="Hello, how are you?")
    ]


@pytest.fixture
def sample_expected_trajectory():
    """Sample expected trajectory for testing"""
    return [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"}
    ]


@pytest.fixture
def sample_evaluate_request(sample_input_messages, sample_expected_trajectory):
    """Sample evaluate request for testing"""
    return EvaluateAgentRequest(
        agent_id=TEST_AGENT_ID,
        input_messages=sample_input_messages,
        expected_trajectory=sample_expected_trajectory
    )


class TestEvaluateAgentValidation:
    """Test validation errors in evaluate_agent"""

    @pytest.mark.asyncio
    async def test_evaluate_agent_empty_agent_id(self, agent_eval_service: AgentEvalService, sample_input_messages: list[ChatMessage], sample_expected_trajectory: list[dict]):
        """Test that empty agent_id returns validation error"""
        request = EvaluateAgentRequest(
            agent_id="",
            input_messages=sample_input_messages,
            expected_trajectory=sample_expected_trajectory
        )
        
        result = await agent_eval_service.evaluate_agent(request)
        
        assert result.success is False
        assert result.score is False
        assert result.key == "validation_error"
        assert result.comment is None
        assert result.actual_trajectory == []
        assert result.message == "Agent ID is required"

    @pytest.mark.asyncio
    async def test_evaluate_agent_no_input_messages(self, agent_eval_service: AgentEvalService, sample_expected_trajectory: list[dict]):
        """Test that missing input_messages returns validation error"""
        request = EvaluateAgentRequest(
            agent_id=TEST_AGENT_ID,
            input_messages=[],
            expected_trajectory=sample_expected_trajectory
        )
        
        result = await agent_eval_service.evaluate_agent(request)
        
        assert result.success is False
        assert result.score is False
        assert result.key == "validation_error"
        assert result.comment is None
        assert result.actual_trajectory == []
        assert result.message == "Input messages are required"

    @pytest.mark.asyncio
    async def test_evaluate_agent_no_expected_trajectory(self, agent_eval_service: AgentEvalService, sample_input_messages: list[ChatMessage]):
        """Test that missing expected_trajectory returns validation error"""
        request = EvaluateAgentRequest(
            agent_id=TEST_AGENT_ID,
            input_messages=sample_input_messages,
            expected_trajectory=[]
        )
        
        result = await agent_eval_service.evaluate_agent(request)
        
        assert result.success is False
        assert result.score is False
        assert result.key == "validation_error"
        assert result.comment is None
        assert result.message == "Expected trajectory is required"
        assert result.actual_trajectory == []


class TestEvaluateAgentSuccess:
    """Test successful evaluation scenarios"""

    @pytest.mark.asyncio
    async def test_evaluate_agent_success_without_tools(
        self,
        agent_eval_service: AgentEvalService,
        sample_agent: AgentInfo,
        sample_evaluate_request: EvaluateAgentRequest
    ):
        """Test successful evaluation without tools"""
        mock_model = MagicMock()
        mock_graph = AsyncMock()
        
        # Mock actual trajectory response
        mock_ai_message = AIMessage(content="I'm doing well, thank you!")
        mock_graph.ainvoke.return_value = {"messages": [HumanMessage(content="Hello"), mock_ai_message]}
        
        # Mock evaluation result (dict format)
        mock_evaluation_result = {
            "score": True,
            "key": "trajectory_strict_match",
            "comment": "Trajectory matches perfectly"
        }
        
        mock_get_agent = AsyncMock(return_value=sample_agent)
        with patch.object(AgentService, 'get_agent', new=mock_get_agent), \
             patch.object(ChatService, 'get_chat_model', return_value=mock_model), \
             patch('app.services.agent.agent_eval_service.create_react_agent', return_value=mock_graph), \
             patch.object(ChatService, '_get_agent_system_prompt', new=AsyncMock(return_value="System prompt")), \
             patch('app.utils.chat.chat_utils.convert_chat_messages', return_value=[HumanMessage(content="Hello")]), \
             patch.object(ChatService, 'jsonify_langchain_messages', return_value=[
                 {"role": "user", "content": "Hello"},
                 {"role": "assistant", "content": "I'm doing well, thank you!"}
             ]), \
             patch('app.services.agent.agent_eval_service.create_trajectory_match_evaluator') as mock_create_evaluator:
            
            mock_evaluator = MagicMock()
            mock_evaluator.return_value = mock_evaluation_result
            mock_create_evaluator.return_value = mock_evaluator
            
            result = await agent_eval_service.evaluate_agent(sample_evaluate_request)
        
        assert result.success is True
        assert result.score is True
        assert result.key == "trajectory_strict_match"
        assert result.comment == "Trajectory matches perfectly"
        assert len(result.actual_trajectory) == 2
        assert "Evaluation completed successfully" in result.message
        
        # Verify AgentService.get_agent was called
        mock_get_agent.assert_called_once_with(TEST_AGENT_ID)
        
        # Verify graph was invoked
        mock_graph.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_evaluate_agent_success_with_tools(
        self,
        agent_eval_service: AgentEvalService,
        sample_agent_with_tools: AgentInfo,
        sample_evaluate_request: EvaluateAgentRequest
    ):
        """Test successful evaluation with tools"""
        mock_model = MagicMock()
        mock_graph = AsyncMock()
        mock_tools = [MagicMock(), MagicMock()]
        
        # Mock actual trajectory response
        mock_ai_message = AIMessage(content="I used tools to help you")
        mock_graph.ainvoke.return_value = {"messages": [HumanMessage(content="Hello"), mock_ai_message]}
        
        # Mock evaluation result
        mock_evaluation_result = {
            "score": True,
            "key": "trajectory_strict_match",
            "comment": "Trajectory matches"
        }
        
        mock_load_mcp_functions = AsyncMock(return_value=mock_tools)
        with patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent_with_tools)), \
             patch.object(ChatService, 'get_chat_model', return_value=mock_model), \
             patch.object(ToolService, 'load_mcp_functions', new=mock_load_mcp_functions), \
             patch('app.services.agent.agent_eval_service.create_react_agent', return_value=mock_graph) as mock_create_agent, \
             patch.object(ChatService, '_get_agent_system_prompt', new=AsyncMock(return_value="System prompt")), \
             patch('app.utils.chat.chat_utils.convert_chat_messages', return_value=[HumanMessage(content="Hello")]), \
             patch.object(ChatService, 'jsonify_langchain_messages', return_value=[
                 {"role": "user", "content": "Hello"},
                 {"role": "assistant", "content": "I used tools to help you"}
             ]), \
             patch('app.services.agent.agent_eval_service.create_trajectory_match_evaluator') as mock_create_evaluator:
            
            mock_evaluator = MagicMock()
            mock_evaluator.return_value = mock_evaluation_result
            mock_create_evaluator.return_value = mock_evaluator
            
            result = await agent_eval_service.evaluate_agent(sample_evaluate_request)
        
        assert result.success is True
        assert result.score is True
        
        # Verify tools were loaded
        mock_load_mcp_functions.assert_called_once_with(["tool1", "tool2"])
        
        # Verify create_react_agent was called with tools
        mock_create_agent.assert_called_once()
        call_args = mock_create_agent.call_args
        assert call_args[0][1] == mock_tools

    @pytest.mark.asyncio
    async def test_evaluate_agent_score_false(
        self,
        agent_eval_service: AgentEvalService,
        sample_agent: AgentInfo,
        sample_evaluate_request: EvaluateAgentRequest
    ):
        """Test evaluation when score is False"""
        mock_model = MagicMock()
        mock_graph = AsyncMock()
        
        mock_ai_message = AIMessage(content="Different response")
        mock_graph.ainvoke.return_value = {"messages": [HumanMessage(content="Hello"), mock_ai_message]}
        
        # Mock evaluation result with score=False
        mock_evaluation_result = {
            "score": False,
            "key": "trajectory_mismatch",
            "comment": "Trajectory does not match expected"
        }
        
        with patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch.object(ChatService, 'get_chat_model', return_value=mock_model), \
             patch('app.services.agent.agent_eval_service.create_react_agent', return_value=mock_graph), \
             patch.object(ChatService, '_get_agent_system_prompt', new=AsyncMock(return_value="System prompt")), \
             patch('app.utils.chat.chat_utils.convert_chat_messages', return_value=[HumanMessage(content="Hello")]), \
             patch.object(ChatService, 'jsonify_langchain_messages', return_value=[
                 {"role": "user", "content": "Hello"},
                 {"role": "assistant", "content": "Different response"}
             ]), \
             patch('app.services.agent.agent_eval_service.create_trajectory_match_evaluator') as mock_create_evaluator:
            
            mock_evaluator = MagicMock()
            mock_evaluator.return_value = mock_evaluation_result
            mock_create_evaluator.return_value = mock_evaluator
            
            result = await agent_eval_service.evaluate_agent(sample_evaluate_request)
        
        assert result.success is True
        assert result.score is False
        assert result.key == "trajectory_mismatch"
        assert result.comment is not None
        assert "Trajectory does not match expected" in result.comment

    @pytest.mark.asyncio
    async def test_evaluate_agent_score_true(
        self,
        agent_eval_service: AgentEvalService,
        sample_agent: AgentInfo,
        sample_evaluate_request: EvaluateAgentRequest,
    ):
        """Test handling of list evaluation result format"""
        mock_model = MagicMock()
        mock_graph = AsyncMock()
        
        mock_ai_message = AIMessage(content="Response")
        mock_graph.ainvoke.return_value = {"messages": [HumanMessage(content="Hello"), mock_ai_message]}
        
        # Mock evaluation result as list (edge case)
        mock_evaluation_result = {
            "score": True,
            "key": "trajectory_match",
            "comment": "Match"
        }
        
        with patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch.object(ChatService, 'get_chat_model', return_value=mock_model), \
             patch('app.services.agent.agent_eval_service.create_react_agent', return_value=mock_graph), \
             patch.object(ChatService, '_get_agent_system_prompt', new=AsyncMock(return_value="System prompt")), \
             patch('app.utils.chat.chat_utils.convert_chat_messages', return_value=[HumanMessage(content="Hello")]), \
             patch.object(ChatService, 'jsonify_langchain_messages', return_value=[
                 {"role": "user", "content": "Hello"},
                 {"role": "assistant", "content": "Response"}
             ]), \
             patch('app.services.agent.agent_eval_service.create_trajectory_match_evaluator') as mock_create_evaluator:
            
            mock_evaluator = MagicMock()
            mock_evaluator.return_value = mock_evaluation_result
            mock_create_evaluator.return_value = mock_evaluator
            
            result = await agent_eval_service.evaluate_agent(sample_evaluate_request)
        
        assert result.success is True
        assert result.score is True
        assert result.key == "trajectory_match"
        assert result.comment == "Match"


class TestEvaluateAgentErrors:
    """Test error handling scenarios"""

    @pytest.mark.asyncio
    async def test_evaluate_agent_get_agent_error(
        self,
        agent_eval_service: AgentEvalService,
        sample_evaluate_request: EvaluateAgentRequest,
    ):
        """Test error when AgentService.get_agent raises exception"""
        error_message = "Agent not found"
        
        with patch.object(AgentService, 'get_agent', new=AsyncMock(side_effect=Exception(error_message))):
            result = await agent_eval_service.evaluate_agent(sample_evaluate_request)
        
        assert result.success is False
        assert result.score is False
        assert result.key == "error"
        assert result.comment is None
        assert result.actual_trajectory == []
        assert "Failed to evaluate agent" in result.message
        assert error_message in result.message

    @pytest.mark.asyncio
    async def test_evaluate_agent_graph_invoke_error(
        self,
        agent_eval_service: AgentEvalService,
        sample_agent: AgentInfo,
        sample_evaluate_request: EvaluateAgentRequest,
    ):
        """Test error when graph.ainvoke raises exception"""
        mock_model = MagicMock()
        mock_graph = AsyncMock()
        mock_graph.ainvoke.side_effect = Exception("Graph invocation failed")
        
        with patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch.object(ChatService, 'get_chat_model', return_value=mock_model), \
             patch('app.services.agent.agent_eval_service.create_react_agent', return_value=mock_graph), \
             patch.object(ChatService, '_get_agent_system_prompt', new=AsyncMock(return_value="System prompt")), \
             patch('app.utils.chat.chat_utils.convert_chat_messages', return_value=[HumanMessage(content="Hello")]):
            
            result = await agent_eval_service.evaluate_agent(sample_evaluate_request)
        
        assert result.success is False
        assert result.score is False
        assert result.key == "error"
        assert result.comment is None
        assert result.actual_trajectory == []
        assert "Failed to evaluate agent" in result.message
        assert "Graph invocation failed" in result.message

    @pytest.mark.asyncio
    async def test_evaluate_agent_evaluator_error(
        self,
        agent_eval_service: AgentEvalService,
        sample_agent: AgentInfo,
        sample_evaluate_request: EvaluateAgentRequest,
    ):
        """Test error when evaluator raises exception"""
        mock_model = MagicMock()
        mock_graph = AsyncMock()
        
        mock_ai_message = AIMessage(content="Response")
        mock_graph.ainvoke.return_value = {"messages": [HumanMessage(content="Hello"), mock_ai_message]}
        
        with patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch.object(ChatService, 'get_chat_model', return_value=mock_model), \
             patch('app.services.agent.agent_eval_service.create_react_agent', return_value=mock_graph), \
             patch.object(ChatService, '_get_agent_system_prompt', new=AsyncMock(return_value="System prompt")), \
             patch('app.utils.chat.chat_utils.convert_chat_messages', return_value=[HumanMessage(content="Hello")]), \
             patch.object(ChatService, 'jsonify_langchain_messages', return_value=[
                 {"role": "user", "content": "Hello"},
                 {"role": "assistant", "content": "Response"}
             ]), \
             patch('app.services.agent.agent_eval_service.create_trajectory_match_evaluator') as mock_create_evaluator:
            
            mock_evaluator = MagicMock()
            mock_evaluator.side_effect = Exception("Evaluator failed")
            mock_create_evaluator.return_value = mock_evaluator
            
            result = await agent_eval_service.evaluate_agent(sample_evaluate_request)
        
        assert result.success is False
        assert result.score is False
        assert result.key == "error"
        assert result.comment is None
        assert "Failed to evaluate agent" in result.message
        assert "Evaluator failed" in result.message

    @pytest.mark.asyncio
    async def test_evaluate_agent_empty_tools_list(
        self,
        agent_eval_service: AgentEvalService,
        sample_agent: AgentInfo,
        sample_evaluate_request: EvaluateAgentRequest,
    ):
        """Test evaluation with agent that has empty tools list"""
        mock_model = MagicMock()
        mock_graph = AsyncMock()
        
        mock_ai_message = AIMessage(content="Response")
        mock_graph.ainvoke.return_value = {"messages": [HumanMessage(content="Hello"), mock_ai_message]}
        
        mock_evaluation_result = {
            "score": True,
            "key": "trajectory_match",
            "comment": "Match"
        }
        
        with patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch.object(ChatService, 'get_chat_model', return_value=mock_model), \
             patch('app.services.agent.agent_eval_service.create_react_agent', return_value=mock_graph), \
             patch.object(ChatService, '_get_agent_system_prompt', new=AsyncMock(return_value="System prompt")), \
             patch('app.utils.chat.chat_utils.convert_chat_messages', return_value=[HumanMessage(content="Hello")]), \
             patch.object(ChatService, 'jsonify_langchain_messages', return_value=[
                 {"role": "user", "content": "Hello"},
                 {"role": "assistant", "content": "Response"}
             ]), \
             patch('app.services.agent.agent_eval_service.create_trajectory_match_evaluator') as mock_create_evaluator:
            
            mock_evaluator = MagicMock()
            mock_evaluator.return_value = mock_evaluation_result
            mock_create_evaluator.return_value = mock_evaluator
            
            result = await agent_eval_service.evaluate_agent(sample_evaluate_request)
        
        assert result.success is True

