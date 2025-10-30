import pytest
from unittest.mock import patch, MagicMock
from google.genai import types

from app.services.image.image_gen.image_gen_gemini import ImageGenGemini
from app.classes.image import GenImageRequest, GenImageResponse
from app.services.image.image_constants import ImageGenModel


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton instance before and after each test"""
    ImageGenGemini._instance = None
    yield
    ImageGenGemini._instance = None


@pytest.fixture
def mock_gemini_client():
    """Create a mock Gemini client"""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def sample_image_data():
    """Create sample image data for testing"""
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'


@pytest.fixture
def mock_chunk_with_image(sample_image_data):
    """Create a mock chunk with image data"""
    chunk = MagicMock()
    chunk.candidates = [MagicMock()]
    chunk.candidates[0].content = MagicMock()
    chunk.candidates[0].content.parts = [MagicMock()]
    
    # Setup inline_data
    inline_data = MagicMock()
    inline_data.data = sample_image_data
    inline_data.mime_type = "image/png"
    
    chunk.candidates[0].content.parts[0].inline_data = inline_data
    chunk.text = ""
    
    return chunk


@pytest.fixture
def mock_chunk_with_text():
    """Create a mock chunk with text data"""
    chunk = MagicMock()
    chunk.candidates = [MagicMock()]
    chunk.candidates[0].content = MagicMock()
    chunk.candidates[0].content.parts = [MagicMock()]
    chunk.candidates[0].content.parts[0].inline_data = None
    chunk.text = "Generated image description"
    
    return chunk


class TestImageGenGeminiSingleton:
    
    def test_singleton_instance(self):
        """Test that ImageGenGemini is a singleton"""
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client"):
            service1 = ImageGenGemini(api_key="test-api-key")
            service2 = ImageGenGemini(api_key="test-api-key")
            assert service1 is service2


class TestImageGenGeminiInitialization:
    
    def test_init_with_valid_api_key(self):
        """Test initialization with valid API key"""
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client") as mock_client_class:
            service = ImageGenGemini(api_key="test-api-key")
            
            assert service is not None
            mock_client_class.assert_called_once_with(api_key="test-api-key")
    
    def test_init_uses_settings_api_key(self):
        """Test initialization uses API key from settings when not provided"""
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client") as mock_client_class:
            with patch("app.services.image.image_gen.image_gen_gemini.settings.gemini_api_key", "test-api-key"):
                service = ImageGenGemini()
                assert service is not None
    
    def test_init_with_empty_api_key(self):
        """Test initialization with empty API key raises ValueError"""
        with pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
            ImageGenGemini(api_key="")


class TestImageGenGeminiGenerateImage:
    
    def test_generate_image_success_with_both_image_and_text(self, mock_gemini_client, mock_chunk_with_image, mock_chunk_with_text, sample_image_data):
        """Test successful image generation with both image and text"""
        # Setup mock stream response
        mock_gemini_client.models.generate_content_stream.return_value = [
            mock_chunk_with_text,
            mock_chunk_with_image
        ]
        
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client", return_value=mock_gemini_client):
            service = ImageGenGemini(api_key="test-api-key")
            response = service.generate_image(GenImageRequest(
                prompt="Generate a beautiful landscape", 
                model=ImageGenModel.GEMINI_2_5_FLASH_IMAGE)
                )
            
            assert isinstance(response, GenImageResponse)
            assert response.image_data == sample_image_data
            assert response.text_data == "Generated image description"
            assert response.mimetype == ".png"
            assert response.message == ""
    
    def test_generate_image_success_with_image_only(self, mock_gemini_client, mock_chunk_with_image, sample_image_data):
        """Test successful image generation with image only"""
        mock_gemini_client.models.generate_content_stream.return_value = [mock_chunk_with_image]
        
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client", return_value=mock_gemini_client):
            service = ImageGenGemini(api_key="test-api-key")
            response = service.generate_image(GenImageRequest(
                prompt="Generate a sunset", 
                model=ImageGenModel.GEMINI_2_5_FLASH_IMAGE)
                )
            
            assert isinstance(response, GenImageResponse)
            assert response.image_data == sample_image_data
            assert response.text_data == ""
            assert response.mimetype == ".png"
            assert response.message == ""
    
    
    def test_generate_image_with_text_only_no_image(self, mock_gemini_client, mock_chunk_with_text):
        """Test image generation when API returns text only (no image data)"""
        mock_gemini_client.models.generate_content_stream.return_value = [mock_chunk_with_text]
        
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client", return_value=mock_gemini_client):
            service = ImageGenGemini(api_key="test-api-key")
            response = service.generate_image(GenImageRequest(
                prompt="Generate a forest", 
                model=ImageGenModel.GEMINI_2_5_FLASH_IMAGE)
                )
            
            assert isinstance(response, GenImageResponse)
            assert response.image_data is None
            assert response.text_data == "Generated image description"
            assert response.mimetype == ""
            assert response.message == ""
    
    def test_generate_image_with_multiple_text_chunks(self, mock_gemini_client):
        """Test image generation with multiple text chunks"""
        # Create multiple text chunks
        chunk1 = MagicMock()
        chunk1.candidates = [MagicMock()]
        chunk1.candidates[0].content = MagicMock()
        chunk1.candidates[0].content.parts = [MagicMock()]
        chunk1.candidates[0].content.parts[0].inline_data = None
        chunk1.text = "Part 1 "
        
        chunk2 = MagicMock()
        chunk2.candidates = [MagicMock()]
        chunk2.candidates[0].content = MagicMock()
        chunk2.candidates[0].content.parts = [MagicMock()]
        chunk2.candidates[0].content.parts[0].inline_data = None
        chunk2.text = "Part 2"
        
        # Create image chunk
        chunk3 = MagicMock()
        chunk3.candidates = [MagicMock()]
        chunk3.candidates[0].content = MagicMock()
        chunk3.candidates[0].content.parts = [MagicMock()]
        inline_data = MagicMock()
        inline_data.data = b"imagedata"
        inline_data.mime_type = "image/jpeg"
        chunk3.candidates[0].content.parts[0].inline_data = inline_data
        chunk3.text = ""
        
        mock_gemini_client.models.generate_content_stream.return_value = [chunk1, chunk2, chunk3]
        
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client", return_value=mock_gemini_client):
            service = ImageGenGemini(api_key="test-api-key")
            response = service.generate_image(GenImageRequest(
                prompt="Generate an image", 
                model=ImageGenModel.GEMINI_2_5_FLASH_IMAGE)
                )
            
            assert isinstance(response, GenImageResponse)
            assert response.text_data == "Part 1 Part 2"
            assert response.image_data == b"imagedata"
            assert response.mimetype == ".jpg"  # mimetypes.guess_extension returns .jpg for image/jpeg
            assert response.message == ""
    
    def test_generate_image_with_none_candidates(self, mock_gemini_client):
        """Test image generation with None candidates returns empty response"""
        chunk = MagicMock()
        chunk.candidates = None
        
        mock_gemini_client.models.generate_content_stream.return_value = [chunk]
        
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client", return_value=mock_gemini_client):
            service = ImageGenGemini(api_key="test-api-key")
            response = service.generate_image(GenImageRequest(
                prompt="Generate an image", 
                model=ImageGenModel.GEMINI_2_5_FLASH_IMAGE)
                )
            
            assert isinstance(response, GenImageResponse)
            assert response.image_data is None
            assert response.text_data == ""
            assert response.mimetype == ""
            assert response.message == ""
    
    def test_generate_image_with_none_content(self, mock_gemini_client):
        """Test image generation with None content returns empty response"""
        chunk = MagicMock()
        chunk.candidates = [MagicMock()]
        chunk.candidates[0].content = None
        
        mock_gemini_client.models.generate_content_stream.return_value = [chunk]
        
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client", return_value=mock_gemini_client):
            service = ImageGenGemini(api_key="test-api-key")
            response = service.generate_image(GenImageRequest(
                prompt="Generate an image", 
                model=ImageGenModel.GEMINI_2_5_FLASH_IMAGE)
                )
            
            assert isinstance(response, GenImageResponse)
            assert response.image_data is None
            assert response.text_data == ""
            assert response.mimetype == ""
            assert response.message == ""
    
    def test_generate_image_with_none_parts(self, mock_gemini_client):
        """Test image generation with None parts returns empty response"""
        chunk = MagicMock()
        chunk.candidates = [MagicMock()]
        chunk.candidates[0].content = MagicMock()
        chunk.candidates[0].content.parts = None
        
        mock_gemini_client.models.generate_content_stream.return_value = [chunk]
        
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client", return_value=mock_gemini_client):
            service = ImageGenGemini(api_key="test-api-key")
            response = service.generate_image(GenImageRequest(
                prompt="Generate an image", 
                model=ImageGenModel.GEMINI_2_5_FLASH_IMAGE)
                )
            
            assert isinstance(response, GenImageResponse)
            assert response.image_data is None
            assert response.text_data == ""
            assert response.mimetype == ""
            assert response.message == ""
    
    def test_generate_image_with_empty_inline_data(self, mock_gemini_client):
        """Test image generation with inline_data but no data returns text only"""
        chunk = MagicMock()
        chunk.candidates = [MagicMock()]
        chunk.candidates[0].content = MagicMock()
        chunk.candidates[0].content.parts = [MagicMock()]
        
        inline_data = MagicMock()
        inline_data.data = None
        chunk.candidates[0].content.parts[0].inline_data = inline_data
        chunk.text = "Text only"
        
        mock_gemini_client.models.generate_content_stream.return_value = [chunk]
        
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client", return_value=mock_gemini_client):
            service = ImageGenGemini(api_key="test-api-key")
            response = service.generate_image(GenImageRequest(
                prompt="Generate an image", 
                model=ImageGenModel.GEMINI_2_5_FLASH_IMAGE)
                )
            
            assert isinstance(response, GenImageResponse)
            assert response.image_data is None
            assert response.text_data == "Text only"
            assert response.mimetype == ""
            assert response.message == ""
    
    def test_generate_image_calls_api_with_correct_config(self, mock_gemini_client, mock_chunk_with_image):
        """Test that generate_image calls API with correct configuration"""
        mock_gemini_client.models.generate_content_stream.return_value = [mock_chunk_with_image]
        
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client", return_value=mock_gemini_client):
            service = ImageGenGemini(api_key="test-api-key")
            service.generate_image(GenImageRequest(
                prompt="test prompt", 
                model=ImageGenModel.GEMINI_2_5_FLASH_IMAGE)
                )
            
            # Verify the API was called with correct parameters
            mock_gemini_client.models.generate_content_stream.assert_called_once()
            call_args = mock_gemini_client.models.generate_content_stream.call_args
            
            assert call_args.kwargs["contents"] is not None
            assert len(call_args.kwargs["contents"]) == 1
            assert call_args.kwargs["contents"][0].role == "user"
            assert call_args.kwargs["contents"][0].parts[0].text == "test prompt"
            
            # Verify config has correct response modalities
            config = call_args.kwargs["config"]
            assert isinstance(config, types.GenerateContentConfig)
            assert config.response_modalities == ["IMAGE", "TEXT"]
    
    def test_generate_image_with_different_mime_types(self, mock_gemini_client):
        """Test image generation with different MIME types"""
        mime_types_to_extensions = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/webp": ".webp",
            "image/gif": ".gif"
        }
        
        for mime_type, expected_extension in mime_types_to_extensions.items():
            # Reset singleton for each iteration
            ImageGenGemini._instance = None
            
            chunk = MagicMock()
            chunk.candidates = [MagicMock()]
            chunk.candidates[0].content = MagicMock()
            chunk.candidates[0].content.parts = [MagicMock()]
            
            inline_data = MagicMock()
            inline_data.data = b"imagedata"
            inline_data.mime_type = mime_type
            
            chunk.candidates[0].content.parts[0].inline_data = inline_data
            chunk.text = ""
            
            mock_gemini_client.models.generate_content_stream.return_value = [chunk]
            
            with patch("app.services.image.image_gen.image_gen_gemini.genai.Client", return_value=mock_gemini_client):
                service = ImageGenGemini(api_key="test-api-key")
                response = service.generate_image(GenImageRequest(
                    prompt="Generate an image", 
                    model=ImageGenModel.GEMINI_2_5_FLASH_IMAGE)
                    )
                
                assert response.mimetype == expected_extension
                assert response.message == ""
    
    def test_generate_image_exception_handling(self, mock_gemini_client):
        """Test that exceptions from API are caught and returned in DTO"""
        mock_gemini_client.models.generate_content_stream.side_effect = Exception("API error")
        
        with patch("app.services.image.image_gen.image_gen_gemini.genai.Client", return_value=mock_gemini_client):
            service = ImageGenGemini(api_key="test-api-key")
            response = service.generate_image(GenImageRequest(
                prompt="Generate an image", 
                model=ImageGenModel.GEMINI_2_5_FLASH_IMAGE)
                )
            
            assert isinstance(response, GenImageResponse)
            assert response.image_data is None
            assert response.text_data is None
            assert response.mimetype is None
            assert response.message == "API error"

