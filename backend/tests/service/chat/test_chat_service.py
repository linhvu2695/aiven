import pytest
import base64
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import UploadFile

from app.services.chat.chat_service import ChatService
from app.services.agent.agent_service import AgentService
from app.classes.chat import ChatMessage, ChatRequest, ChatResponse, ChatFileContent, ChatStreamChunk
from app.classes.agent import AgentInfo
from app.core.constants import LLMModel

# Test constants
TEST_SESSION_ID = "test-session-id"
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
    """Test _get_chat_model method."""
    
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
        
        result = chat_service._get_chat_model(LLMModel.GPT_4O)
        
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
        
        result = chat_service._get_chat_model(LLMModel.GEMINI_2_0_FLASH)
        
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
        
        result = chat_service._get_chat_model(LLMModel.CLAUDE_SONNET_3_5)
        
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
        
        result = chat_service._get_chat_model(LLMModel.GROK_3)
        
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
        
        result = chat_service._get_chat_model(LLMModel.MISTRAL_LARGE_LATEST)
        
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
        
        result = chat_service._get_chat_model(LLMModel.NVIDIA_NEVA_22B)
        
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
        
        result = chat_service._get_chat_model("unknown_model")
        
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


class TestGetFileTypeCategory:
    """Test _get_file_type_category method."""
    
    @pytest.fixture
    def chat_service(self):
        ChatService._instance = None
        return ChatService()
    
    def test_image_mime_type(self, chat_service):
        """Test image mime type categorization."""
        assert chat_service._get_file_type_category("image/jpeg") == "image"
        assert chat_service._get_file_type_category("image/png") == "image"
        assert chat_service._get_file_type_category("image/gif") == "image"
    
    def test_audio_mime_type(self, chat_service):
        """Test audio mime type categorization."""
        assert chat_service._get_file_type_category("audio/mp3") == "audio"
        assert chat_service._get_file_type_category("audio/wav") == "audio"
    
    def test_video_mime_type(self, chat_service):
        """Test video mime type categorization."""
        assert chat_service._get_file_type_category("video/mp4") == "video"
        assert chat_service._get_file_type_category("video/avi") == "video"
    
    def test_text_mime_type(self, chat_service):
        """Test text mime type categorization."""
        assert chat_service._get_file_type_category("text/plain") == "text"
        assert chat_service._get_file_type_category("text/html") == "text"
    
    def test_document_mime_type(self, chat_service):
        """Test document mime type categorization."""
        assert chat_service._get_file_type_category("application/pdf") == "document"
    
    def test_application_mime_type(self, chat_service):
        """Test application mime type categorization."""
        assert chat_service._get_file_type_category("application/json") == "application"
        assert chat_service._get_file_type_category("application/zip") == "application"
    
    def test_unknown_mime_type(self, chat_service):
        """Test unknown mime type categorization."""
        assert chat_service._get_file_type_category("unknown/type") == "file"
        assert chat_service._get_file_type_category("") == "file"
        assert chat_service._get_file_type_category(None) == "file"


class TestGetFileContent:
    """Test _get_file_content method."""
    
    @pytest.fixture
    def chat_service(self):
        ChatService._instance = None
        return ChatService()
    
    @pytest.mark.asyncio
    async def test_get_file_content_success(self, chat_service):
        """Test successful file content processing."""
        # Create mock file
        file_content = b"test file content"
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = TEST_TEXT_FILE
        mock_file.read = AsyncMock(return_value=file_content)
        mock_file.seek = AsyncMock()
        
        with patch('mimetypes.guess_type', return_value=('text/plain', None)):
            result = await chat_service._get_file_content(mock_file)
        
        assert result is not None
        assert isinstance(result, ChatFileContent)
        assert result.type == "text"
        assert result.source_type == "base64"
        assert result.mime_type == "text/plain"
        assert result.data == base64.b64encode(file_content).decode('utf-8')
        
        mock_file.read.assert_called_once()
        mock_file.seek.assert_called_once_with(0)
    
    @pytest.mark.asyncio
    async def test_get_file_content_no_file(self, chat_service):
        """Test handling of None file."""
        result = await chat_service._get_file_content(None)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_file_content_no_filename(self, chat_service):
        """Test handling of file without filename."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = None
        
        result = await chat_service._get_file_content(mock_file)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_file_content_empty_filename(self, chat_service):
        """Test handling of file with empty filename."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = ""
        
        result = await chat_service._get_file_content(mock_file)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_file_content_exception(self, chat_service):
        """Test handling of exception during file processing."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = TEST_TEXT_FILE
        mock_file.read = AsyncMock(side_effect=Exception("File read error"))
        
        with patch('builtins.print') as mock_print:
            result = await chat_service._get_file_content(mock_file)
        
        assert result is None
        mock_print.assert_called_once_with("Error processing file test.txt: File read error")
    
    @pytest.mark.asyncio
    async def test_get_file_content_unknown_mime_type(self, chat_service):
        """Test handling of unknown mime type."""
        file_content = b"unknown content"
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = TEST_UNKNOWN_FILE
        mock_file.read = AsyncMock(return_value=file_content)
        mock_file.seek = AsyncMock()
        
        with patch('mimetypes.guess_type', return_value=(None, None)):
            result = await chat_service._get_file_content(mock_file)
        
        assert result is not None
        assert result.mime_type == "application/octet-stream"
        assert result.type == "application"


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
            avatar="test_avatar",
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
            avatar="",
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
            avatar="special_avatar",
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
            avatar="multiline_avatar",
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
            avatar="test_avatar",
            tools=[]
        )
    
    @pytest.fixture
    def sample_chat_request(self):
        return ChatRequest(
            messages=[
                ChatMessage(role="user", content="Hello"),
                ChatMessage(role="assistant", content="Hi there!"),
                ChatMessage(role="user", content="How are you?")
            ],
            agent=TEST_AGENT_ID,
            files=None
        )
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_success(self, chat_service, sample_agent, sample_chat_request):
        """Test successful chat response generation."""
        # Create a more comprehensive mock
        mock_model = MagicMock()
        
        # Create a mock response message with the expected structure
        mock_response_message = MagicMock()
        mock_response_message.content = "I'm doing well, thank you!"
        
        # Create a mock graph with complete mocking
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {"messages": [mock_response_message]}
        
        with patch.object(chat_service, '_get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
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
        assert len(call_args[0]["messages"]) == 3  # 3 request messages (no system message since it's passed separately)
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_with_file(self, chat_service, sample_agent):
        """Test chat response generation with file upload."""
        # Create request with file
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = TEST_IMAGE_FILE
        
        request_with_file = ChatRequest(
            messages=[ChatMessage(role="user", content="Analyze this image")],
            agent=TEST_AGENT_ID,
            files=[mock_file]
        )
        
        mock_file_content = ChatFileContent(
            type="image",
            source_type="base64",
            data="base64_data",
            mime_type="image/jpeg"
        )
        
        # Set up mocks
        mock_model = MagicMock()
        mock_response_message = MagicMock()
        mock_response_message.content = "I can see the image"
        
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {"messages": [mock_response_message]}
        
        with patch.object(chat_service, '_get_chat_model', return_value=mock_model), \
             patch.object(chat_service, '_get_file_content', new=AsyncMock(return_value=mock_file_content)), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
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
        """Test chat response when file processing returns None."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = TEST_IMAGE_FILE
        
        request_with_file = ChatRequest(
            messages=[ChatMessage(role="user", content="Analyze this image")],
            agent=TEST_AGENT_ID,
            files=[mock_file]
        )
        
        # Set up mocks
        mock_model = MagicMock()
        mock_response_message = MagicMock()
        mock_response_message.content = "No image provided"
        
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {"messages": [mock_response_message]}
        
        with patch.object(chat_service, '_get_chat_model', return_value=mock_model), \
             patch.object(chat_service, '_get_file_content', new=AsyncMock(return_value=None)), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(request_with_file)
        
        assert isinstance(result, ChatResponse)
        assert result.response == "No image provided"
        
        # Verify that no file message was added
        call_args, call_kwargs = mock_graph.ainvoke.call_args
        assert "messages" in call_args[0]
        assert len(call_args[0]["messages"]) == 1  # user message only (no system message since it's passed separately)
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_format_error(self, chat_service, sample_agent, sample_chat_request):
        """Test handling of format-related errors."""
        mock_model = MagicMock()
        
        # Mock the graph to raise a format-related exception
        mock_graph = AsyncMock()
        mock_graph.ainvoke.side_effect = Exception("Unsupported media_type: image/webp")
        
        with patch.object(chat_service, '_get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent, \
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
        
        with patch.object(chat_service, '_get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
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
        
        with patch.object(chat_service, '_get_chat_model', return_value=mock_model), \
             patch.object(AgentService, 'get_agent', new=AsyncMock(return_value=sample_agent)), \
             patch('app.services.chat.chat_service.create_react_agent') as mock_create_agent:
            
            mock_create_agent.return_value = mock_graph
            
            result = await chat_service.generate_chat_response(sample_chat_request)
        
        assert isinstance(result, ChatResponse)
        assert "❌ An error occurred" in result.response


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
            avatar="test_avatar",
            tools=[]
        )
    
    @pytest.fixture
    def sample_chat_request(self):
        return ChatRequest(
            messages=[
                ChatMessage(role="user", content="Hello"),
                ChatMessage(role="assistant", content="Hi there!"),
                ChatMessage(role="user", content="How are you?")
            ],
            agent=TEST_AGENT_ID,
            session_id=TEST_SESSION_ID,  # Valid MongoDB ObjectId format
            files=None
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
            'model_patch': patch.object(chat_service, '_get_chat_model', return_value=mock_model),
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
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = TEST_IMAGE_FILE
        
        request_with_file = ChatRequest(
            messages=[ChatMessage(role="user", content="Analyze this image")],
            agent=TEST_AGENT_ID,
            session_id=TEST_SESSION_ID,
            files=[mock_file]
        )
        
        mock_file_content = ChatFileContent(
            type="image",
            source_type="base64",
            data="base64_data",
            mime_type="image/jpeg"
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
             patch.object(chat_service, '_get_file_content', new=AsyncMock(return_value=mock_file_content)), \
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
            avatar="test_avatar",
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
            messages=[ChatMessage(role="user", content="Hello")],
            agent=TEST_AGENT_ID,
            session_id="",
            files=None
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
        
        with patch.object(chat_service, '_get_chat_model', return_value=mock_model), \
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