import pytest
import base64
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import UploadFile
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.services.chat.chat_service import ChatService
from app.services.agent.agent_service import AgentService
from app.classes.chat import ChatMessage, ChatRequest, ChatResponse, ChatFileContent
from app.classes.agent import AgentInfo
from app.core.constants import LLMModel


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
        mock_settings.openai_api_key = "test_key"
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service._get_chat_model(LLMModel.GPT_4O)
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.GPT_4O,
            model_provider="openai",
            api_key="test_key"
        )
        assert result == mock_model
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_gemini_model(self, mock_settings, mock_init_chat_model, chat_service):
        """Test getting Gemini model."""
        mock_settings.gemini_api_key = "test_gemini_key"
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service._get_chat_model(LLMModel.GEMINI_2_0_FLASH)
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.GEMINI_2_0_FLASH,
            model_provider="google_genai",
            api_key="test_gemini_key"
        )
        assert result == mock_model
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_claude_model(self, mock_settings, mock_init_chat_model, chat_service):
        """Test getting Claude model."""
        mock_settings.anthropic_api_key = "test_anthropic_key"
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service._get_chat_model(LLMModel.CLAUDE_SONNET_3_5)
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.CLAUDE_SONNET_3_5,
            model_provider="anthropic",
            api_key="test_anthropic_key"
        )
        assert result == mock_model
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_grok_model(self, mock_settings, mock_init_chat_model, chat_service):
        """Test getting Grok model."""
        mock_settings.xai_api_key = "test_xai_key"
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service._get_chat_model(LLMModel.GROK_3)
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.GROK_3,
            model_provider="xai",
            api_key="test_xai_key"
        )
        assert result == mock_model
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_mistral_model(self, mock_settings, mock_init_chat_model, chat_service):
        """Test getting Mistral model."""
        mock_settings.mistral_api_key = "test_mistral_key"
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service._get_chat_model(LLMModel.MISTRAL_LARGE_LATEST)
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.MISTRAL_LARGE_LATEST,
            model_provider="mistralai",
            api_key="test_mistral_key"
        )
        assert result == mock_model
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_nvidia_model(self, mock_settings, mock_init_chat_model, chat_service):
        """Test getting NVIDIA model."""
        mock_settings.nvidia_api_key = "test_nvidia_key"
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service._get_chat_model(LLMModel.NVIDIA_NEVA_22B)
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.NVIDIA_NEVA_22B,
            model_provider="nvidia",
            api_key="test_nvidia_key"
        )
        assert result == mock_model
    
    @patch('app.services.chat.chat_service.init_chat_model')
    @patch('app.services.chat.chat_service.settings')
    def test_get_unknown_model_defaults_to_gpt(self, mock_settings, mock_init_chat_model, chat_service):
        """Test that unknown model defaults to GPT_4O_MINI."""
        mock_settings.openai_api_key = "test_key"
        mock_model = MagicMock()
        mock_init_chat_model.return_value = mock_model
        
        result = chat_service._get_chat_model("unknown_model")
        
        mock_init_chat_model.assert_called_once_with(
            model=LLMModel.GPT_4O_MINI,
            model_provider="openai",
            api_key="test_key"
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
        mock_file.filename = "test.txt"
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
        mock_file.filename = "test.txt"
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
        mock_file.filename = "unknown_file"
        mock_file.read = AsyncMock(return_value=file_content)
        mock_file.seek = AsyncMock()
        
        with patch('mimetypes.guess_type', return_value=(None, None)):
            result = await chat_service._get_file_content(mock_file)
        
        assert result is not None
        assert result.mime_type == "application/octet-stream"
        assert result.type == "application"


class TestGenerateChatResponse:
    """Test generate_chat_response method."""
    
    @pytest.fixture
    def chat_service(self):
        ChatService._instance = None
        return ChatService()
    
    @pytest.fixture
    def sample_agent(self):
        return AgentInfo(
            id="test_agent",
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
            agent="test_agent",
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
        
        # Verify create_react_agent was called with the model and empty tools
        mock_create_agent.assert_called_once_with(mock_model, [])
        
        # Verify the graph was called
        mock_graph.ainvoke.assert_called_once()
        
        # Verify the correct arguments were passed to ainvoke
        call_args, call_kwargs = mock_graph.ainvoke.call_args
        assert "messages" in call_args[0]
        assert len(call_args[0]["messages"]) == 4  # system + 3 request messages
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_with_file(self, chat_service, sample_agent):
        """Test chat response generation with file upload."""
        # Create request with file
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.jpg"
        
        request_with_file = ChatRequest(
            messages=[ChatMessage(role="user", content="Analyze this image")],
            agent="test_agent",
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
        assert len(call_args[0]["messages"]) == 3  # system + user message + file message
    
    @pytest.mark.asyncio
    async def test_generate_chat_response_with_file_no_content(self, chat_service, sample_agent):
        """Test chat response when file processing returns None."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.jpg"
        
        request_with_file = ChatRequest(
            messages=[ChatMessage(role="user", content="Analyze this image")],
            agent="test_agent",
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
        assert len(call_args[0]["messages"]) == 2  # system + user message only
    
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