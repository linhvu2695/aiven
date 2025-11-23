import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.chat.chat_service import ChatService
from app.services.agent.agent_service import AgentService
from app.classes.chat import ChatMessage, ChatRequest, ChatResponse, ChatFileContent, ChatStreamChunk
from app.classes.agent import AgentInfo
from app.services.chat.chat_constants import LLMModel

# Test constants
TEST_SESSION_ID = "507f1f77bcf86cd799439011"  # Valid 24-character hex MongoDB ObjectId
TEST_NEW_SESSION_ID = "test-new-session-id"
TEST_AGENT_ID = "test-agent"
TEST_OPENAI_API_KEY = "test-openai-key"
TEST_GEMINI_API_KEY = "test-gemini-key"
TEST_ANTHROPIC_API_KEY = "test-anthropic-key"
TEST_XAI_API_KEY = "test-xai-key"
TEST_MISTRAL_API_KEY = "test-mistral-key"
TEST_NVIDIA_API_KEY = "test-nvidia-key"
TEST_TEXT_FILE = "test.txt"
TEST_IMAGE_FILE = "test.jpg"
TEST_UNKNOWN_FILE = "unknown_file"
TEST_ALTERNATE_SESSION_ID = "test-alternate-session-id"


# Mock token classes for testing streaming responses
class MockToolResultToken:
    """Mock token representing a tool execution result with tool_call_id and name attributes."""
    def __init__(self, message_id, tool_call_id, tool_name, content):
        self.id = message_id
        self.tool_call_id = tool_call_id
        self.name = tool_name
        self.content = content


class MockTextToken:
    """Mock token representing a regular AI text response."""
    def __init__(self, message_id, content):
        self.id = message_id
        self.content = content


class TestChatServiceSingleton:
    """Test ChatService singleton pattern."""
    
    def test_singleton_instance(self):
        """Test that ChatService follows singleton pattern."""
        # Reset singleton
        ChatService._instance = None
        
        service1 = ChatService()
        service2 = ChatService()
        
        assert service1 is service2
        assert id(service1) == id(service2)


class TestGetChatModel:
    """Test get_chat_model method."""
    
    @pytest.fixture
    def chat_service(self):
        ChatService._instance = None
        return ChatService()
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_openai_model(self, mock_settings, mock_init_chat_model, chat_service):
        """Test getting OpenAI model."""
        mock_settings.openai_api_key = TEST_OPENAI_API_KEY
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service.get_chat_model(LLMModel.GPT_4O)
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.GPT_4O,
            model_provider="openai",
            api_key=TEST_OPENAI_API_KEY
        )
        assert result == mock_model
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_gemini_model(self, mock_settings, mock_init_chat_model, chat_service):
        """Test getting Gemini model."""
        mock_settings.gemini_api_key = TEST_GEMINI_API_KEY
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service.get_chat_model(LLMModel.GEMINI_2_0_FLASH)
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.GEMINI_2_0_FLASH,
            model_provider="google_genai",
            api_key=TEST_GEMINI_API_KEY
        )
        assert result == mock_model
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_claude_model(self, mock_settings, mock_init_chat_model, chat_service):
        """Test getting Claude model."""
        mock_settings.anthropic_api_key = TEST_ANTHROPIC_API_KEY
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service.get_chat_model(LLMModel.CLAUDE_SONNET_3_5)
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.CLAUDE_SONNET_3_5,
            model_provider="anthropic",
            api_key=TEST_ANTHROPIC_API_KEY
        )
        assert result == mock_model
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_grok_model(self, mock_settings, mock_init_chat_model, chat_service):
        """Test getting Grok model."""
        mock_settings.xai_api_key = TEST_XAI_API_KEY
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service.get_chat_model(LLMModel.GROK_3)
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.GROK_3,
            model_provider="xai",
            api_key=TEST_XAI_API_KEY
        )
        assert result == mock_model
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_mistral_model(self, mock_settings, mock_init_chat_model, chat_service):
        """Test getting Mistral model."""
        mock_settings.mistral_api_key = TEST_MISTRAL_API_KEY
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service.get_chat_model(LLMModel.MISTRAL_LARGE_LATEST)
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.MISTRAL_LARGE_LATEST,
            model_provider="mistralai",
            api_key=TEST_MISTRAL_API_KEY
        )
        assert result == mock_model
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_nvidia_model(self, mock_settings, mock_init_chat_model, chat_service):
        """Test getting NVIDIA model."""
        mock_settings.nvidia_api_key = TEST_NVIDIA_API_KEY
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service.get_chat_model(LLMModel.NVIDIA_NEVA_22B)
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.NVIDIA_NEVA_22B,
            model_provider="nvidia",
            api_key=TEST_NVIDIA_API_KEY
        )
        assert result == mock_model
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_unknown_model_defaults_to_gpt(self, mock_settings, mock_init_chat_model, chat_service):
        """Test that unknown model defaults to GPT_4O_MINI."""
        mock_settings.openai_api_key = TEST_OPENAI_API_KEY
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service.get_chat_model("unknown_model")
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.GPT_4O_MINI,
            model_provider="openai",
            api_key=TEST_OPENAI_API_KEY
        )
        assert result == mock_model


class TestParseFormatError:
    """Test _parse_format_error method."""
    
    @pytest.fixture
    def chat_service(self):
        ChatService._instance = None
        return ChatService()
    
    def test_parse_format_error_with_image_formats(self, chat_service):
        """Test parsing error with image format information."""
        error_message = "Unsupported media type. Supported types: 'image/jpeg', 'image/png', 'image/gif'"
        
        result = chat_service._parse_format_error(error_message)
        
        assert "❌ File Upload Error" in result
        assert "JPEG, PNG, GIF" in result
        assert "Supported formats:" in result
    
    def test_parse_format_error_with_single_format(self, chat_service):
        """Test parsing error with single format."""
        error_message = "Unsupported format: 'image/webp'"
        
        result = chat_service._parse_format_error(error_message)
        
        assert "❌ File Upload Error" in result
        assert "WEBP" in result
    
    def test_parse_format_error_generic_media_type(self, chat_service):
        """Test parsing generic media_type error."""
        error_message = "Invalid media_type provided"
        
        result = chat_service._parse_format_error(error_message)
        
        assert "❌ File Upload Error" in result
        assert "not supported by this model" in result
    
    def test_parse_format_error_fallback(self, chat_service):
        """Test parsing error fallback for unrecognized errors."""
        error_message = "Some random error"
        
        result = chat_service._parse_format_error(error_message)
        
        assert "❌ File Upload Error: Some random error" == result


class TestGetAgentSystemPrompt:
    """Test _get_agent_system_prompt method."""
    
    @pytest.fixture
    def chat_service(self):
        ChatService._instance = None
        return ChatService()
    
    @pytest.fixture
    def sample_agent(self):
        return AgentInfo(
            id=TEST_AGENT_ID,
            name="Test Agent",
            description="A helpful test assistant",
            model=LLMModel.GPT_4O,
            persona="You are a friendly and knowledgeable assistant",
            tone="professional",
            avatar_image_id="test_avatar_id",
            avatar_image_url="http://test.com/avatar.jpg",
            tools=[]
        )
    
    @pytest.mark.asyncio
    async def test_get_agent_system_prompt_with_complete_agent(self, chat_service, sample_agent):
        """Test system prompt generation includes all agent fields."""
        result = await chat_service._get_agent_system_prompt(sample_agent)
        
        # Test basic structure and type
        assert isinstance(result, str)
        assert len(result.strip()) > 0
        
        # Test that all agent fields are included in the prompt
        assert sample_agent.name in result
        assert sample_agent.description in result
        assert sample_agent.persona in result
        assert sample_agent.tone in result
    
    @pytest.mark.asyncio
    async def test_get_agent_system_prompt_with_empty_values(self, chat_service):
        """Test system prompt generation handles empty string values gracefully."""
        agent = AgentInfo(
            id="empty_agent",
            name="",
            description="",
            model=LLMModel.GPT_4O,
            persona="",
            tone="",
            avatar_image_id=None,
            avatar_image_url="",
            tools=[]
        )
        
        result = await chat_service._get_agent_system_prompt(agent)
        
        # Test basic structure and type
        assert isinstance(result, str)
        assert len(result.strip()) > 0
        
        # Test that empty values don't break the formatting
        # The prompt should still be a valid string structure
        lines = result.strip().split('\n')
        assert len(lines) > 0
    
    @pytest.mark.asyncio
    async def test_get_agent_system_prompt_with_special_characters(self, chat_service):
        """Test system prompt generation preserves special characters."""
        agent = AgentInfo(
            id="special_agent",
            name="Agent & Co.",
            description="An agent with <special> characters & symbols",
            model=LLMModel.GPT_4O,
            persona="You are an assistant with 'quotes' and \"double quotes\"",
            tone="casual & friendly",
            avatar_image_id="special_avatar_id",
            avatar_image_url="http://test.com/special_avatar.jpg",
            tools=[]
        )
        
        result = await chat_service._get_agent_system_prompt(agent)
        
        # Test basic structure and type
        assert isinstance(result, str)
        assert len(result.strip()) > 0
        
        # Test that special characters are preserved in the output
        assert "Agent & Co." in result
        assert "<special>" in result
        assert "& symbols" in result
        assert "'quotes'" in result
        assert "\"double quotes\"" in result
        assert "casual & friendly" in result
    
    @pytest.mark.asyncio
    async def test_get_agent_system_prompt_with_multiline_values(self, chat_service):
        """Test system prompt generation handles multiline values correctly."""
        agent = AgentInfo(
            id="multiline_agent",
            name="Multiline Agent",
            description="First line\nSecond line\nThird line",
            model=LLMModel.GPT_4O,
            persona="You are helpful.\nYou are knowledgeable.\nYou are friendly.",
            tone="professional\nand courteous",
            avatar_image_id="multiline_avatar_id",
            avatar_image_url="http://test.com/multiline_avatar.jpg",
            tools=[]
        )
        
        result = await chat_service._get_agent_system_prompt(agent)
        
        # Test basic structure and type
        assert isinstance(result, str)
        assert len(result.strip()) > 0
        
        # Test that multiline content is preserved
        assert "Multiline Agent" in result
        assert "First line" in result
        assert "Second line" in result
        assert "Third line" in result
        assert "You are helpful." in result
        assert "You are knowledgeable." in result
        assert "You are friendly." in result
        assert "professional" in result
        assert "and courteous" in result


class TestGenerateChatResponse:
    """Test generate_chat_response method."""
    
    @pytest.fixture
    def chat_service(self):
        ChatService._instance = None
        return ChatService()
    
    @pytest.fixture
    def sample_agent(self):
        return AgentInfo(
            id=TEST_AGENT_ID,
            name="Test Agent",
            description="Test description",
            model=LLMModel.GPT_4O,
            persona="You are a helpful assistant",
            tone="friendly",
            avatar_image_id="test_avatar_id",
            avatar_image_url="http://test.com/avatar.jpg",
            tools=[]
        )
    
    @pytest.fixture
    def sample_chat_request(self):
        return ChatRequest(
            message="Hello",
            agent=TEST_AGENT_ID
        )
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_success(self, chat_service, sample_agent, sample_chat_request):
        """Test successful chat response generation."""
        # Create a more comprehensive mock
        mock_model = MagicMock()
        
        # Create a mock response message with the expected structure
        mock_response_message = MagicMock()
        mock_response_message.content = "I'm doing well, thank you!"
        mock_response_message.tool_call_id = None
        mock_response_message.name = None
        
        # Create a mock graph with complete mocking
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {"messages": [mock_response_message]}
        
        # Mock existing chat history with 2 previous messages + 1 new message to simulate ongoing conversation
        from langchain_core.messages import HumanMessage, AIMessage
        all_messages = [
            HumanMessage(content="Hi there!"),
            AIMessage(content="Hello! How can I help you?"),
            HumanMessage(content="Hello")  # This will be the new message from the request
        ]
        
        # Mock the chat history to return all messages (including new one after aadd_messages is called)
        mock_history = AsyncMock()
        mock_history.aget_messages.return_value = all_messages
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history):
            
            # Set up the mock to return our mock graph
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(sample_chat_request)
        
        assert isinstance(result, ChatResponse)
        assert result.response == "I'm doing well, thank you!"
        
        # Verify create_react_agent was called with the model, empty tools, and a prompt
        mock_create_agent.assert_called_once()
        
        # Verify the graph was called
        mock_graph.ainvoke.assert_called_once()
        
        # Verify the correct arguments were passed to ainvoke
        call_args, call_kwargs = mock_graph.ainvoke.call_args
        assert "messages" in call_args[0]
        assert len(call_args[0]["messages"]) == 4  # 4 messages (3 from history + 1 new message added by service)
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_with_file(self, chat_service, sample_agent):
        """Test chat response generation with file upload."""
        # Create mock file content since file handling is now done via file_contents
        mock_file_content = ChatFileContent(
            type="image",
            source_type="base64", 
            data="base64_data",
            mime_type="image/jpeg"
        )
        
        request_with_file = ChatRequest(
            message="Analyze this image",
            agent=TEST_AGENT_ID,
            file_contents=[mock_file_content]
        )
        
        # Set up mocks
        mock_model = MagicMock()
        mock_response_message = MagicMock()
        mock_response_message.content = "I can see the image"
        mock_response_message.tool_call_id = None
        mock_response_message.name = None
        
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {"messages": [mock_response_message]}
        
        # Mock history to return the user message that would be added
        from langchain_core.messages import HumanMessage
        user_message = HumanMessage(content="Analyze this image")
        mock_history = AsyncMock()
        mock_history.aget_messages.return_value = [user_message]
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history):
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(request_with_file)
        
        assert isinstance(result, ChatResponse)
        assert result.response == "I can see the image"
        
        # Verify the graph was called
        mock_graph.ainvoke.assert_called_once()
        
        # Verify that file message was added to the messages
        call_args, call_kwargs = mock_graph.ainvoke.call_args
        assert "messages" in call_args[0]
        assert len(call_args[0]["messages"]) == 2  # user message + file message (no system message since it's passed separately)
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_with_file_no_content(self, chat_service, sample_agent):
        """Test chat response when no file content is provided."""
        request_with_file = ChatRequest(
            message="Analyze this image",
            agent=TEST_AGENT_ID,
            file_contents=[]
        )
        
        # Set up mocks
        mock_model = MagicMock()
        mock_response_message = MagicMock()
        mock_response_message.content = "No image provided"
        mock_response_message.tool_call_id = None
        mock_response_message.name = None
        
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {"messages": [mock_response_message]}
        
        # Mock history to return the user message that would be added
        from langchain_core.messages import HumanMessage
        user_message = HumanMessage(content="Analyze this image")
        mock_history = AsyncMock()
        mock_history.aget_messages.return_value = [user_message]
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history):
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(request_with_file)
        
        assert isinstance(result, ChatResponse)
        assert result.response == "No image provided"
        
        # Verify that no file message was added
        call_args, call_kwargs = mock_graph.ainvoke.call_args
        assert "messages" in call_args[0]
        assert len(call_args[0]["messages"]) == 2  # 2 messages (1 from history + 1 new message added by service)
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_format_error(self, chat_service, sample_agent, sample_chat_request):
        """Test handling of format-related errors."""
        mock_model = MagicMock()
        
        # Mock the graph to raise a format-related exception
        mock_graph = AsyncMock()
        mock_graph.ainvoke.side_effect = Exception("Unsupported media_type: image/webp")
        
        mock_history = AsyncMock()
        mock_history.aget_messages.return_value = []
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history), \
             patch.object(chat_service, '_parse_format_error', return_value="Format error message") as mock_parse:
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(sample_chat_request)
        
        assert isinstance(result, ChatResponse)
        assert result.response == "Format error message"
        mock_parse.assert_called_once_with("Unsupported media_type: image/webp")
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_bad_request_error(self, chat_service, sample_agent, sample_chat_request):
        """Test handling of BadRequestError."""
        mock_model = MagicMock()
        
        class MockBadRequestError(Exception):
            pass
        
        MockBadRequestError.__name__ = "BadRequestError"
        
        # Mock the graph to raise a BadRequestError
        mock_graph = AsyncMock()
        mock_graph.ainvoke.side_effect = MockBadRequestError("Bad request")
        
        mock_history = AsyncMock()
        mock_history.aget_messages.return_value = []
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history):
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(sample_chat_request)
        
        assert isinstance(result, ChatResponse)
        assert "❌ Request Error" in result.response
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_generic_error(self, chat_service, sample_agent, sample_chat_request):
        """Test handling of generic errors."""
        mock_model = MagicMock()
        
        # Mock the graph to raise a generic exception
        mock_graph = AsyncMock()
        mock_graph.ainvoke.side_effect = Exception("Generic error")
        
        mock_history = AsyncMock()
        mock_history.aget_messages.return_value = []
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history):
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(sample_chat_request)
        
        assert isinstance(result, ChatResponse)
        assert "❌ An error occurred" in result.response
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_with_tool_result(self, chat_service, sample_agent, sample_chat_request):
        """Test chat response with tool execution result."""
        mock_model = MagicMock()
        
        # Use shared MockToolResultToken class
        mock_tool_result = MockToolResultToken("msg-tool-result", "tool-call-123", "calculate", "The result is 42")
        
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {"messages": [mock_tool_result]}
        
        mock_history = AsyncMock()
        mock_history.aget_messages.return_value = []
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history):
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(sample_chat_request)
        
        assert isinstance(result, ChatResponse)
        assert result.response == "Call `calculate`"
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_with_multiple_tool_results(self, chat_service, sample_agent, sample_chat_request):
        """Test chat response with multiple tool execution results."""
        mock_model = MagicMock()
        
        # Use shared MockToolResultToken class
        mock_tool_result_1 = MockToolResultToken("msg-1", "tool-call-1", "get_weather", "Temperature: 72°F")
        mock_tool_result_2 = MockToolResultToken("msg-2", "tool-call-2", "get_time", "12:30 PM")
        
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {"messages": [mock_tool_result_1, mock_tool_result_2]}
        
        mock_history = AsyncMock()
        mock_history.aget_messages.return_value = []
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history):
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(sample_chat_request)
        
        assert isinstance(result, ChatResponse)
        # Should return the last message (get_time)
        assert result.response == "Call `get_time`"
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_with_tool_result_and_ai_response(self, chat_service, sample_agent, sample_chat_request):
        """Test chat response with tool result followed by AI text response."""
        mock_model = MagicMock()
        
        # Use shared mock classes
        mock_tool_result = MockToolResultToken("msg-tool", "tool-call-1", "search", "Search completed")
        
        # For AI response, use MagicMock with spec to ensure no tool_call_id attribute
        mock_ai_response = MagicMock(spec=['id', 'content'])
        mock_ai_response.id = "msg-ai"
        mock_ai_response.content = "Based on the search results, here's what I found..."
        
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {"messages": [mock_tool_result, mock_ai_response]}
        
        mock_history = AsyncMock()
        mock_history.aget_messages.return_value = []
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history):
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(sample_chat_request)
        
        assert isinstance(result, ChatResponse)
        # Should return the last message (AI response)
        assert result.response == "Based on the search results, here's what I found..."
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_with_tool_result_without_content(self, chat_service, sample_agent, sample_chat_request):
        """Test chat response with tool result that has no text content."""
        mock_model = MagicMock()
        
        # Use shared MockToolResultToken class with None content
        mock_tool_result = MockToolResultToken("msg-tool", "tool-call-1", "get_data", None)
        
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {"messages": [mock_tool_result]}
        
        mock_history = AsyncMock()
        mock_history.aget_messages.return_value = []
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history):
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(sample_chat_request)
        
        assert isinstance(result, ChatResponse)
        # Should still format as tool call even without content
        assert result.response == "Call `get_data`"
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_with_tool_result_empty_name(self, chat_service, sample_agent, sample_chat_request):
        """Test chat response with tool result that has empty tool name (edge case)."""
        mock_model = MagicMock()
        
        # Use shared MockToolResultToken class with empty name
        mock_tool_result = MockToolResultToken("msg-tool", "tool-call-1", "", "Tool execution completed")
        
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {"messages": [mock_tool_result]}
        
        mock_history = AsyncMock()
        mock_history.aget_messages.return_value = []
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history):
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(sample_chat_request)
        
        assert isinstance(result, ChatResponse)
        # Should use regular content when tool name is empty
        assert result.response == "Tool execution completed"
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_with_mixed_messages(self, chat_service, sample_agent, sample_chat_request):
        """Test chat response with mixed regular and tool result messages."""
        mock_model = MagicMock()
        
        # Create a sequence of mixed messages using spec to control attributes for AI messages
        mock_ai_msg_1 = MagicMock(spec=['id', 'content'])
        mock_ai_msg_1.id = "msg-ai-1"
        mock_ai_msg_1.content = "Let me search for that information."
        
        # Use shared MockToolResultToken class
        mock_tool_result = MockToolResultToken("msg-tool", "tool-call-1", "search_web", "Search completed")
        
        mock_ai_msg_2 = MagicMock(spec=['id', 'content'])
        mock_ai_msg_2.id = "msg-ai-2"
        mock_ai_msg_2.content = "Here's what I found from the search."
        
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {"messages": [mock_ai_msg_1, mock_tool_result, mock_ai_msg_2]}
        
        mock_history = AsyncMock()
        mock_history.aget_messages.return_value = []
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history):
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(sample_chat_request)
        
        assert isinstance(result, ChatResponse)
        # Should return the last message
        assert result.response == "Here's what I found from the search."


class TestGenerateStreamingChatResponse:
    """Test generate_streaming_chat_response method."""
    
    @pytest.fixture
    def chat_service(self):
        ChatService._instance = None
        return ChatService()
    
    @pytest.fixture
    def sample_agent(self):
        return AgentInfo(
            id=TEST_AGENT_ID,
            name="Test Agent",
            description="Test description",
            model=LLMModel.GPT_4O,
            persona="You are a helpful assistant",
            tone="friendly",
            avatar_image_id="test_avatar_id",
            avatar_image_url="http://test.com/avatar.jpg",
            tools=[]
        )
    
    @pytest.fixture
    def sample_chat_request(self):
        return ChatRequest(
            message="Hello",
            agent=TEST_AGENT_ID,
            session_id=TEST_SESSION_ID  # Valid MongoDB ObjectId format
        )
    
    async def collect_stream(self, async_gen):
        """Helper method to collect content from ChatStreamChunk objects."""
        content_items = []
        chunks = []
        async for chunk in async_gen:
            chunks.append(chunk)
            if isinstance(chunk, ChatStreamChunk) and chunk.content:
                content_items.append(chunk.content)
        return content_items, chunks
    
    def setup_base_mocks(self, chat_service, mock_model, sample_agent, session_id=TEST_SESSION_ID):
        """Helper method to setup common mocks for streaming tests."""
        mock_history = AsyncMock()
        mock_history._session_id = session_id
        mock_history.aget_messages.return_value = []
        
        return {
            'history_patch': patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history),
            'model_patch': patch.object(chat_service, 'get_chat_model', return_value=mock_model),
            'agent_patch': patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)),
            'mock_history': mock_history
        }
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_success_string_tokens(self, chat_service, sample_agent, sample_chat_request):
        """Test successful streaming with string tokens."""
        mock_model = MagicMock()
        
        # Mock the async generator for astream
        async def mock_astream(*args, **kwargs):
            tokens = ["Hello", " there", "!", " How", " can", " I", " help", "?"]
            for token in tokens:
                yield token, {}  # token, metadata
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        expected_tokens = ["Hello", " there", "!", " How", " can", " I", " help", "?"]
        assert content_items == expected_tokens
        
        # Verify we got ChatStreamChunk objects
        assert len(chunks) > len(expected_tokens)  # Should include completion chunk
        content_chunks = [c for c in chunks if c.content]
        assert all(isinstance(chunk, ChatStreamChunk) for chunk in chunks)
        assert chunks[0].session_id == TEST_SESSION_ID  # First chunk should have session_id
        
        # Verify create_react_agent was called
        mock_create_agent.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_success_object_tokens(self, chat_service, sample_agent, sample_chat_request):
        """Test successful streaming with object tokens containing content."""
        mock_model = MagicMock()
        
        # Create mock token objects with content
        class MockToken:
            def __init__(self, content):
                self.content = content
        
        async def mock_astream(*args, **kwargs):
            tokens = [
                MockToken("Hello"),
                MockToken(" world"),
                MockToken("!")
            ]
            for token in tokens:
                yield token, {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        expected_tokens = ["Hello", " world", "!"]
        assert content_items == expected_tokens
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_list_content(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming with list content containing text items."""
        mock_model = MagicMock()
        
        class MockToken:
            def __init__(self, content):
                self.content = content
        
        async def mock_astream(*args, **kwargs):
            # Token with list content containing strings and dict with text
            token_with_list = MockToken([
                "First part",
                {"text": " second part"},
                " third part"
            ])
            yield token_with_list, {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        # List content should be concatenated into a single token
        expected_tokens = ["First part second part third part"]
        assert content_items == expected_tokens
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_with_file(self, chat_service, sample_agent):
        """Test streaming with file upload."""
        mock_file_content = ChatFileContent(
            type="image",
            source_type="base64",
            data="base64_data",
            mime_type="image/jpeg"
        )
        
        request_with_file = ChatRequest(
            message="Analyze this image",
            agent=TEST_AGENT_ID,
            session_id=TEST_SESSION_ID,
            file_contents=[mock_file_content]
        )
        
        mock_model = MagicMock()
        
        async def mock_astream(*args, **kwargs):
            yield "I can see", {}
            yield " the image", {}
            yield " clearly", {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(request_with_file)
            )
        
        expected_tokens = ["I can see", " the image", " clearly"]
        assert content_items == expected_tokens
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_empty_stream(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming when no tokens are produced."""
        mock_model = MagicMock()
        
        async def mock_astream(*args, **kwargs):
            # Empty generator - no tokens yielded
            return
            yield  # This won't be reached but helps with typing
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        assert content_items == []
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_mixed_token_types(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming with mixed token types."""
        mock_model = MagicMock()
        
        class MockToken:
            def __init__(self, content):
                self.content = content
        
        async def mock_astream(*args, **kwargs):
            # Mix of string tokens and object tokens
            yield "Hello", {}
            yield MockToken(" world"), {}
            yield "!", {}
            yield MockToken(" How are"), {}
            yield " you?", {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        expected_tokens = ["Hello", " world", "!", " How are", " you?"]
        assert content_items == expected_tokens
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_format_error(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming with format-related error."""
        mock_model = MagicMock()
        
        # Create a proper async generator that raises an exception during iteration
        async def mock_astream(*args, **kwargs):
            if False:  # This makes it an async generator
                yield
            raise Exception("Unsupported media_type: image/webp")
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch.object(chat_service, '_parse_format_error', return_value="Format error message") as mock_parse:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        assert content_items == ["Format error message"]
        # Should have error chunk with session_id
        error_chunks = [c for c in chunks if c.content == "Format error message"]
        assert len(error_chunks) == 1
        assert error_chunks[0].is_complete == True
        mock_parse.assert_called_once_with("Unsupported media_type: image/webp")
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_bad_request_error(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming with BadRequestError."""
        mock_model = MagicMock()
        
        async def mock_astream(*args, **kwargs):
            if False:  # This makes it an async generator
                yield
            raise Exception("400 Bad Request: Invalid input")
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        assert len(content_items) == 1
        assert "❌ Request Error" in content_items[0]
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_bad_request_error_type(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming with actual BadRequestError exception type."""
        mock_model = MagicMock()
        
        # Create a mock exception that has "BadRequestError" in its type name
        class BadRequestError(Exception):
            pass
        
        async def mock_astream(*args, **kwargs):
            if False:  # This makes it an async generator
                yield
            raise BadRequestError("Bad request")
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        assert len(content_items) == 1
        assert "❌ Request Error" in content_items[0]
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_generic_error(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming with generic error."""
        mock_model = MagicMock()
        
        async def mock_astream(*args, **kwargs):
            if False:  # This makes it an async generator
                yield
            raise Exception("Generic error")
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        assert len(content_items) == 1
        assert "❌ An error occurred" in content_items[0]
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_with_tools(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming with agent that has tools configured."""
        # Modify agent to have tools
        agent_with_tools = AgentInfo(
            id=TEST_AGENT_ID,
            name="Test Agent",
            description="Test description",
            model=LLMModel.GPT_4O,
            persona="You are a helpful assistant",
            tone="friendly",
            avatar_image_id="test_avatar_id",
            avatar_image_url="http://test.com/avatar.jpg",
            tools=["tool1", "tool2"]
        )
        
        mock_model = MagicMock()
        mock_tools = [MagicMock(), MagicMock()]
        
        async def mock_astream(*args, **kwargs):
            yield "Using tools to", {}
            yield " help you", {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, agent_with_tools)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch.object(chat_service, '_load_mcp_tools', new=AsyncMock(return_value=mock_tools)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        expected_tokens = ["Using tools to", " help you"]
        assert content_items == expected_tokens
        
        # Verify create_react_agent was called with tools
        mock_create_agent.assert_called_once()
        call_args = mock_create_agent.call_args[0]
        assert call_args[1] == mock_tools  # tools parameter
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_token_without_content(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming when tokens don't have content attribute."""
        mock_model = MagicMock()
        
        class MockTokenNoContent:
            pass  # No content attribute
        
        async def mock_astream(*args, **kwargs):
            yield MockTokenNoContent(), {}
            yield "Valid token", {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        # Should only get the valid token, not the one without content
        assert content_items == ["Valid token"]
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_session_id_management(self, chat_service, sample_agent):
        """Test session ID management in streaming response."""
        mock_model = MagicMock()
        
        # Test with empty session_id (new conversation)
        empty_session_request = ChatRequest(
            message="Hello",
            agent=TEST_AGENT_ID,
            session_id=""
        )
        
        # Mock MongoDB chat history for new conversation
        mock_history = AsyncMock()
        mock_history._session_id = TEST_ALTERNATE_SESSION_ID  # Different valid ObjectId
        mock_history.aget_messages.return_value = []
        
        async def mock_astream(*args, **kwargs):
            yield "Hello", {}
            yield " user", {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        with patch.object(chat_service, 'get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
             patch('app.services.chat.chat_service.MongoDBChatHistory', return_value=mock_history):
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(empty_session_request)
            )
        
        # Verify content
        assert content_items == ["Hello", " user"]
        
        # Verify session ID behavior
        content_chunks = [c for c in chunks if c.content]
        completion_chunks = [c for c in chunks if c.is_complete]
        
        # First content chunk should have session_id
        assert content_chunks[0].session_id == TEST_ALTERNATE_SESSION_ID
        # Other content chunks should not have session_id
        for chunk in content_chunks[1:]:
            assert chunk.session_id == ""
        
        # Completion chunk should have session_id
        assert len(completion_chunks) == 1
        assert completion_chunks[0].session_id == TEST_ALTERNATE_SESSION_ID
        assert completion_chunks[0].is_complete == True
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_token_with_empty_content(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming when token has empty content."""
        mock_model = MagicMock()
        
        class MockToken:
            def __init__(self, content):
                self.content = content
        
        async def mock_astream(*args, **kwargs):
            yield MockToken(""), {}  # Empty content
            yield MockToken(None), {}  # None content
            yield MockToken("Valid content"), {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        # Should only get the token with valid content
        assert content_items == ["Valid content"]
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_with_tool_call_result(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming when tool execution returns a result message."""
        mock_model = MagicMock()
        
        async def mock_astream(*args, **kwargs):
            # Simulate tool result (output from tool execution)
            yield MockToolResultToken("msg-tool-result", "tool-call-123", "calculate", "The result is 42"), {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        # Should have tool result formatted
        assert content_items == ["Called `calculate`"]
        
        # Verify chunk has tool_name
        content_chunks = [c for c in chunks if c.content]
        assert len(content_chunks) == 1
        assert content_chunks[0].tool_name == "calculate"
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_with_multiple_tool_results(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming with multiple sequential tool results."""
        mock_model = MagicMock()
        
        async def mock_astream(*args, **kwargs):
            # Multiple tool results from different tool executions
            yield MockToolResultToken("msg-1", "tool-call-1", "get_weather", "Temperature: 72°F"), {}
            yield MockToolResultToken("msg-2", "tool-call-2", "get_time", "12:30 PM"), {}
            yield MockToolResultToken("msg-3", "tool-call-3", "search_web", "Found 5 results"), {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        # Should have all three tool results formatted
        expected = ["Called `get_weather`", "Called `get_time`", "Called `search_web`"]
        assert content_items == expected
        
        # Verify each chunk has correct tool_name
        content_chunks = [c for c in chunks if c.content]
        assert len(content_chunks) == 3
        assert content_chunks[0].tool_name == "get_weather"
        assert content_chunks[1].tool_name == "get_time"
        assert content_chunks[2].tool_name == "search_web"
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_tool_result_with_ai_response(self, chat_service, sample_agent, sample_chat_request):
        """Test streaming with tool result followed by AI text response."""
        mock_model = MagicMock()
        
        async def mock_astream(*args, **kwargs):
            # Tool result
            yield MockToolResultToken("msg-tool", "tool-call-1", "get_weather", "Temperature: 72°F"), {}
            # AI response after processing tool result
            yield MockTextToken("msg-text", "The weather"), {}
            yield MockTextToken("msg-text", " is sunny"), {}
            yield MockTextToken("msg-text", " today!"), {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        # Should have tool result followed by text response
        expected = ["Called `get_weather`", "The weather", " is sunny", " today!"]
        assert content_items == expected
        
        # Verify tool chunk has tool_name but text chunks don't
        content_chunks = [c for c in chunks if c.content]
        assert content_chunks[0].tool_name == "get_weather"
        assert content_chunks[1].tool_name == ""
        assert content_chunks[2].tool_name == ""
        assert content_chunks[3].tool_name == ""
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_tool_result_with_message_id_change(self, chat_service, sample_agent, sample_chat_request):
        """Test message accumulation when message_id changes during tool results and AI responses."""
        mock_model = MagicMock()
        
        async def mock_astream(*args, **kwargs):
            # First message - tool result
            yield MockToolResultToken("msg-1", "tool-1", "search", "Search completed"), {}
            # Second message - AI response
            yield MockTextToken("msg-2", "Based on"), {}
            yield MockTextToken("msg-2", " the search"), {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        # Verify content
        expected = ["Called `search`", "Based on", " the search"]
        assert content_items == expected
        
        # Verify message_id tracking
        content_chunks = [c for c in chunks if c.content]
        assert content_chunks[0].message_id == "msg-1"
        assert content_chunks[1].message_id == "msg-2"
        assert content_chunks[2].message_id == "msg-2"
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_tool_result_without_text_content(self, chat_service, sample_agent, sample_chat_request):
        """Test tool result tokens that don't have text content (only have tool metadata)."""
        mock_model = MagicMock()
        
        async def mock_astream(*args, **kwargs):
            yield MockToolResultToken("msg-123", "tool-1", "get_data", None), {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        # Should still generate formatted tool result even with None content
        assert content_items == ["Called `get_data`"]
        assert chunks[0].tool_name == "get_data"
    
    @pytest.mark.asyncio
    async def test_generate_streaming_chat_response_tool_result_with_empty_name(self, chat_service, sample_agent, sample_chat_request):
        """Test handling of tool result tokens with empty tool name (edge case)."""
        mock_model = MagicMock()
        
        class MockTokenWithEmptyToolName:
            def __init__(self):
                self.id = "msg-123"
                self.tool_call_id = "tool-1"
                self.name = ""  # Empty name
                self.content = "Tool execution completed"
        
        async def mock_astream(*args, **kwargs):
            yield MockTokenWithEmptyToolName(), {}
            yield "normal text", {}
        
        mock_graph = AsyncMock()
        mock_graph.astream = mock_astream
        
        mocks = self.setup_base_mocks(chat_service, mock_model, sample_agent)
        
        with mocks['model_patch'], mocks['agent_patch'], mocks['history_patch'], \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            content_items, chunks = await self.collect_stream(
                chat_service.generate_streaming_chat_response(sample_chat_request)
            )
        
        # Should use regular content when tool name is empty (not formatted as tool result)
        assert content_items == ["Tool execution completed", "normal text"]
        assert chunks[0].tool_name == ""
    
    
class TestGetModels:
    """Test get_models method."""
    
    @pytest.fixture
    def chat_service(self):
        ChatService._instance = None
        return ChatService()
    
    @pytest.mark.asyncio
    async def test_get_models(self, chat_service):
        """Test getting models returns correct structure."""
        result = await chat_service.get_models()
        
        assert isinstance(result, dict)
        assert "openai" in result
        assert "google_genai" in result
        assert "anthropic" in result
        assert "xai" in result
        assert "mistralai" in result
        assert "nvidia" in result
        
        # Test that each provider has models
        for provider, models in result.items():
            assert isinstance(models, list)
            assert len(models) > 0
            
            # Test model structure
            for model in models:
                assert isinstance(model, dict)
                assert "value" in model
                assert "label" in model
                assert isinstance(model["value"], str)
                assert isinstance(model["label"], str)
        
        # Test specific models exist
        openai_models = result["openai"]
        openai_values = [model["value"] for model in openai_models]
        assert LLMModel.GPT_4O.value in openai_values
        assert LLMModel.GPT_4O_MINI.value in openai_values
        
        gemini_models = result["google_genai"]
        gemini_values = [model["value"] for model in gemini_models]
        assert LLMModel.GEMINI_2_0_FLASH.value in gemini_values


class TestConversationNaming:
    """Test conversation naming functionality."""
    
    @pytest.fixture
    def chat_service(self):
        ChatService._instance = None
        return ChatService()
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.MongoDB')
    @patch('app.services.chat.chat_service.MongoDB')
    @patch('app.services.agent.agent_service.AgentService.get_agent')
    async def test_generate_conversation_name_if_needed_for_new_conversation(
        self, mock_get_agent, mock_mongodb_class_chat_service, mock_mongodb_class, chat_service
    ):
        """Test that conversation names are generated for new conversations."""
        from app.classes.conversation import Conversation
        from langchain_core.messages import HumanMessage, AIMessage
        from datetime import datetime, timezone
        
        # Mock agent
        mock_agent = AgentInfo(
            id=TEST_AGENT_ID,
            name="Test Agent",
            description="Test description",
            avatar_image_id="test_avatar_id",
            avatar_image_url="http://test.com/test-avatar.jpg",
            persona="Test persona",
            tone="friendly",
            model=LLMModel.GPT_4O_MINI,
            tools=[]
        )
        mock_get_agent.return_value = mock_agent
        
        # Mock conversation data with 2 messages (should trigger naming)
        mock_conversation_data = {
            "_id": TEST_SESSION_ID,
            "name": "",  # Empty name
            "messages": [
                HumanMessage(content="Hello, can you help me with Python?").model_dump(),
                AIMessage(content="Of course! I'd be happy to help you with Python.").model_dump()
            ],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value=mock_conversation_data)
        
        # Mock the update_document for chat_service
        mock_mongodb_instance_chat_service = MagicMock()
        mock_mongodb_class_chat_service.return_value = mock_mongodb_instance_chat_service
        mock_mongodb_instance_chat_service.update_document = AsyncMock()
        
        # Mock the chat model and AI response
        mock_ai_response = MagicMock()
        mock_ai_response.content = "Python Help Session"
        
        with patch.object(chat_service, 'get_chat_model') as mockget_chat_model:
            # Create a mock for the model that supports ainvoke
            mock_model = AsyncMock()
            mock_model.ainvoke = AsyncMock(return_value=mock_ai_response)
            mockget_chat_model.return_value = mock_model
            
            # Create mock history and call the naming method
            mock_history = AsyncMock()
            mock_history._session_id = TEST_SESSION_ID
            mock_history._aget_conversation.return_value = Conversation(
                id=TEST_SESSION_ID,
                name="",
                agent_id=TEST_AGENT_ID,
                messages=mock_conversation_data["messages"],
                created_at=mock_conversation_data["created_at"],
                updated_at=mock_conversation_data["updated_at"]
            )
            
            await chat_service._generate_conversation_name_if_needed(mock_history, TEST_AGENT_ID)
        
        # Verify that the update was called with the generated name
        mock_mongodb_instance_chat_service.update_document.assert_called_once()
        args, kwargs = mock_mongodb_instance_chat_service.update_document.call_args
        assert args[0] == "conversation"
        assert args[1] == TEST_SESSION_ID
        assert "name" in args[2]
        assert args[2]["name"] == "Python Help Session"
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.MongoDB')
    @patch('app.services.chat.chat_service.MongoDB')
    async def test_generate_conversation_name_if_needed_skips_existing_name(
        self, mock_mongodb_class_chat_service, mock_mongodb_class, chat_service
    ):
        """Test that naming is skipped for conversations that already have names."""
        from app.classes.conversation import Conversation
        from langchain_core.messages import HumanMessage, AIMessage
        from datetime import datetime, timezone
        
        # Mock conversation data with existing name
        mock_conversation_data = {
            "_id": TEST_SESSION_ID,
            "name": "Existing Name",  # Already has a name
            "messages": [
                HumanMessage(content="Hello").model_dump(),
                AIMessage(content="Hi there!").model_dump()
            ],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value=mock_conversation_data)
        
        # Mock the update_document for chat_service
        mock_mongodb_instance_chat_service = MagicMock()
        mock_mongodb_class_chat_service.return_value = mock_mongodb_instance_chat_service
        mock_mongodb_instance_chat_service.update_document = AsyncMock()
        
        # Create mock history and call the naming method
        mock_history = AsyncMock()
        mock_history._session_id = TEST_SESSION_ID
        mock_history._aget_conversation.return_value = Conversation(
            id=TEST_SESSION_ID,
            name="Existing Name",
            agent_id=TEST_AGENT_ID,
            messages=mock_conversation_data["messages"],
            created_at=mock_conversation_data["created_at"],
            updated_at=mock_conversation_data["updated_at"]
        )
        
        await chat_service._generate_conversation_name_if_needed(mock_history, TEST_AGENT_ID)
        
        # Verify that update was NOT called
        mock_mongodb_instance_chat_service.update_document.assert_not_called()
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.MongoDB')
    @patch('app.services.chat.chat_service.MongoDB')
    async def test_generate_conversation_name_if_needed_skips_too_few_messages(
        self, mock_mongodb_class_chat_service, mock_mongodb_class, chat_service
    ):
        """Test that naming is skipped for conversations with too few messages."""
        from app.classes.conversation import Conversation
        from langchain_core.messages import HumanMessage
        from datetime import datetime, timezone
        
        # Mock conversation data with only 1 message
        mock_conversation_data = {
            "_id": TEST_SESSION_ID,
            "name": "",
            "messages": [
                HumanMessage(content="Hello").model_dump()
            ],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value=mock_conversation_data)
        
        # Mock the update_document for chat_service
        mock_mongodb_instance_chat_service = MagicMock()
        mock_mongodb_class_chat_service.return_value = mock_mongodb_instance_chat_service
        mock_mongodb_instance_chat_service.update_document = AsyncMock()
        
        # Create mock history and call the naming method
        mock_history = AsyncMock()
        mock_history._session_id = TEST_SESSION_ID
        mock_history._aget_conversation.return_value = Conversation(
            id=TEST_SESSION_ID,
            name="",
            agent_id=TEST_AGENT_ID,
            messages=mock_conversation_data["messages"],
            created_at=mock_conversation_data["created_at"],
            updated_at=mock_conversation_data["updated_at"]
        )
        
        await chat_service._generate_conversation_name_if_needed(mock_history, TEST_AGENT_ID)
        
        # Verify that update was NOT called
        mock_mongodb_instance_chat_service.update_document.assert_not_called() 