import pytest
import json
import io
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock
from app.api.chat_api import router
from app.classes.chat import ChatRequest, ChatResponse

app = FastAPI()
app.include_router(router, prefix="/chat")


@pytest.fixture
def sample_chat_message():
    return {"role": "user", "content": "How are you?"}


@pytest.fixture  
def sample_session_id():
    return "test-session-id"


@pytest.fixture
def sample_chat_response():
    return ChatResponse(response="I'm doing well, thank you for asking!")


@pytest.fixture
def sample_models_response():
    return {
        "openai": [
            {"value": "gpt-3.5-turbo", "label": "gpt-3.5-turbo"},
            {"value": "gpt-4", "label": "gpt-4"}
        ],
        "google_genai": [
            {"value": "gemini-pro", "label": "gemini-pro"}
        ],
        "anthropic": [
            {"value": "claude-3-haiku", "label": "claude-3-haiku"}
        ]
    }


class TestChatEndpointJSON:
    """Test cases for the chat endpoint with JSON payload"""

    @pytest.mark.asyncio
    async def test_chat_endpoint_json_success(self, sample_chat_message, sample_session_id, sample_chat_response):
        """Test successful chat endpoint with JSON payload"""
        with patch("app.services.chat.chat_service.ChatService.generate_chat_response", new=AsyncMock(return_value=sample_chat_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                payload = {
                    "message": sample_chat_message,
                    "agent": "test-agent-123",
                    "session_id": sample_session_id
                }
                response = await ac.post("/chat/", json=payload)
                
                assert response.status_code == 200
                data = response.json()
                assert "response" in data
                assert data["response"] == "I'm doing well, thank you for asking!"

    @pytest.mark.asyncio
    async def test_chat_endpoint_json_missing_message(self):
        """Test chat endpoint with missing message in JSON payload"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {"agent": "test-agent-123"}
            response = await ac.post("/chat/", json=payload)
            
            assert response.status_code == 400
            data = response.json()
            assert "Message and agent are required" in data["detail"]

    @pytest.mark.asyncio
    async def test_chat_endpoint_json_missing_agent(self, sample_chat_message):
        """Test chat endpoint with missing agent in JSON payload"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {"message": sample_chat_message}
            response = await ac.post("/chat/", json=payload)
            
            assert response.status_code == 400
            data = response.json()
            assert "Message and agent are required" in data["detail"]

    @pytest.mark.asyncio
    async def test_chat_endpoint_json_empty_message_content(self):
        """Test chat endpoint with empty message content"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {
                "message": {"role": "user", "content": ""},
                "agent": "test-agent-123"
            }
            response = await ac.post("/chat/", json=payload)
            
            # This should still succeed as empty content might be valid
            # The validation would be handled by the service layer
            assert response.status_code in [200, 400]


class TestChatEndpointFormData:
    """Test cases for the chat endpoint with FormData (multipart/form-data)"""

    @pytest.mark.asyncio
    async def test_chat_endpoint_formdata_success(self, sample_chat_message, sample_session_id, sample_chat_response):
        """Test successful chat endpoint with FormData including file upload"""
        with patch("app.services.chat.chat_service.ChatService.generate_chat_response", new=AsyncMock(return_value=sample_chat_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                # Create a test file
                test_file_content = b"This is a test file content"
                test_file = io.BytesIO(test_file_content)
                
                files = {"files": ("test.txt", test_file, "text/plain")}
                data = {
                    "message": json.dumps(sample_chat_message),
                    "agent": "test-agent-123",
                    "session_id": sample_session_id
                }
                
                response = await ac.post("/chat/", files=files, data=data)
                
                assert response.status_code == 200
                response_data = response.json()
                assert "response" in response_data
                assert response_data["response"] == "I'm doing well, thank you for asking!"

    @pytest.mark.asyncio
    async def test_chat_endpoint_formdata_missing_message(self):
        """Test chat endpoint FormData with missing message"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Use a real file to trigger multipart/form-data
            test_file_content = b"This is a test file"
            test_file = io.BytesIO(test_file_content)
            
            files = {"files": ("test.txt", test_file, "text/plain")}
            data = {"agent": "test-agent-123"}  # Missing message
            
            response = await ac.post("/chat/", files=files, data=data)
            
            assert response.status_code == 400
            response_data = response.json()
            assert "Message and agent are required" in response_data["detail"]

    @pytest.mark.asyncio
    async def test_chat_endpoint_formdata_missing_agent(self, sample_chat_message):
        """Test chat endpoint FormData with missing agent"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Use a real file to trigger multipart/form-data
            test_file_content = b"This is a test file"
            test_file = io.BytesIO(test_file_content)
            
            files = {"files": ("test.txt", test_file, "text/plain")}
            data = {"message": json.dumps(sample_chat_message)}  # Missing agent
            
            response = await ac.post("/chat/", files=files, data=data)
            
            assert response.status_code == 400
            response_data = response.json()
            assert "Message and agent are required" in response_data["detail"]

    @pytest.mark.asyncio
    async def test_chat_endpoint_formdata_invalid_json(self):
        """Test chat endpoint FormData with invalid JSON in message"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Use a real file to trigger multipart/form-data
            test_file_content = b"This is a test file"
            test_file = io.BytesIO(test_file_content)
            
            files = {"files": ("test.txt", test_file, "text/plain")}
            data = {
                "message": "invalid json {",
                "agent": "test-agent-123"
            }
            
            response = await ac.post("/chat/", files=files, data=data)
            
            assert response.status_code == 400
            response_data = response.json()
            assert "Invalid message format" in response_data["detail"]


class TestChatEndpointErrorHandling:
    """Test cases for error handling scenarios"""

    @pytest.mark.asyncio
    async def test_chat_endpoint_unsupported_content_type(self, sample_chat_message):
        """Test chat endpoint with unsupported content type"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/chat/",
                content=json.dumps({"message": sample_chat_message, "agent": "test-agent"}),
                headers={"content-type": "text/plain"}
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "Invalid request format" in data["detail"]

    @pytest.mark.asyncio
    async def test_chat_endpoint_service_exception(self, sample_chat_message):
        """Test chat endpoint when ChatService raises an exception"""
        with patch("app.services.chat.chat_service.ChatService.generate_chat_response", new=AsyncMock(side_effect=Exception("Service error"))):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                payload = {
                    "message": sample_chat_message,
                    "agent": "test-agent-123"
                }
                # Expect the exception to be raised (FastAPI's default behavior)
                with pytest.raises(Exception, match="Service error"):
                    await ac.post("/chat/", json=payload)


class TestModelsEndpoint:
    """Test cases for the /models endpoint"""

    @pytest.mark.asyncio
    async def test_get_models_success(self, sample_models_response):
        """Test successful retrieval of available models"""
        with patch("app.services.chat.chat_service.ChatService.get_models", new=AsyncMock(return_value=sample_models_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/chat/models")
                
                assert response.status_code == 200
                data = response.json()
                
                assert "openai" in data
                assert "google_genai" in data
                assert "anthropic" in data
                
                assert len(data["openai"]) == 2
                assert data["openai"][0]["value"] == "gpt-3.5-turbo"
                assert data["openai"][0]["label"] == "gpt-3.5-turbo"
                
                assert len(data["google_genai"]) == 1
                assert data["google_genai"][0]["value"] == "gemini-pro"

    @pytest.mark.asyncio
    async def test_get_models_service_exception(self):
        """Test models endpoint when ChatService raises an exception"""
        with patch("app.services.chat.chat_service.ChatService.get_models", new=AsyncMock(side_effect=Exception("Service error"))):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                # Expect the exception to be raised (FastAPI's default behavior)
                with pytest.raises(Exception, match="Service error"):
                    await ac.get("/chat/models")


class TestChatRequestValidation:
    """Test cases for ChatRequest validation and message parsing"""

    @pytest.mark.asyncio
    async def test_chat_message_validation_success(self, sample_chat_message, sample_session_id, sample_chat_response):
        """Test that ChatMessage objects are properly created from request data"""
        # Mock ChatService to capture the ChatRequest that was passed
        captured_request = None
        async def capture_request(request):
            nonlocal captured_request
            captured_request = request
            return sample_chat_response
        
        with patch("app.services.chat.chat_service.ChatService.generate_chat_response", new=AsyncMock(side_effect=capture_request)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                payload = {
                    "message": sample_chat_message,
                    "agent": "test-agent-123",
                    "session_id": sample_session_id
                }
                response = await ac.post("/chat/", json=payload)
                
                assert response.status_code == 200
                assert captured_request is not None
                assert isinstance(captured_request, ChatRequest)
                assert captured_request.message == "How are you?"
                assert captured_request.agent == "test-agent-123"
                assert captured_request.session_id == sample_session_id
                assert captured_request.file_contents is None

    @pytest.mark.asyncio
    async def test_chat_request_with_files(self, sample_chat_message, sample_session_id, sample_chat_response):
        """Test that files are properly included in ChatRequest"""
        captured_request = None
        async def capture_request(request):
            nonlocal captured_request
            captured_request = request
            return sample_chat_response
        
        with patch("app.services.chat.chat_service.ChatService.generate_chat_response", new=AsyncMock(side_effect=capture_request)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                test_file_content = b"This is a test file"
                test_file = io.BytesIO(test_file_content)
                
                files = {"files": ("test.txt", test_file, "text/plain")}
                data = {
                    "message": json.dumps(sample_chat_message),
                    "agent": "test-agent-123",
                    "session_id": sample_session_id
                }
                
                response = await ac.post("/chat/", files=files, data=data)
                
                assert response.status_code == 200
                assert captured_request is not None
                assert isinstance(captured_request, ChatRequest)
                assert captured_request.file_contents is not None
                assert len(captured_request.file_contents) == 1
                assert captured_request.file_contents[0].type == "text" 