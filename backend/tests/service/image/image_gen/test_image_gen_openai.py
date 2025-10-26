import pytest
import base64
from unittest.mock import patch, MagicMock

from app.services.image.image_gen.image_gen_openai import ImageGenOpenAI
from app.services.image.image_gen.image_gen_aspect_ratio import ImageGenAspectRatio
from app.classes.image import GenImageRequest, GenImageResponse


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton instance before and after each test"""
    ImageGenOpenAI._instance = None
    yield
    ImageGenOpenAI._instance = None


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client"""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def sample_image_data():
    """Create sample image data for testing"""
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'


@pytest.fixture
def sample_base64_image():
    """Create sample base64 encoded image"""
    return base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01').decode()


@pytest.fixture
def mock_openai_response(sample_base64_image):
    """Create a mock OpenAI API response"""
    response = MagicMock()
    image_data = MagicMock()
    image_data.b64_json = sample_base64_image
    image_data.revised_prompt = "A beautiful landscape with mountains and lakes"
    response.data = [image_data]
    return response


class TestImageGenOpenAISingleton:
    
    def test_singleton_instance(self):
        """Test that ImageGenOpenAI is a singleton"""
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI"):
            service1 = ImageGenOpenAI(api_key="test-api-key")
            service2 = ImageGenOpenAI(api_key="test-api-key")
            assert service1 is service2


class TestImageGenOpenAIInitialization:
    
    def test_init_with_valid_api_key(self):
        """Test initialization with valid API key"""
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI") as mock_client_class:
            service = ImageGenOpenAI(api_key="test-api-key")
            
            assert service is not None
            mock_client_class.assert_called_once_with(api_key="test-api-key")
    
    def test_init_uses_settings_api_key(self):
        """Test initialization uses API key from settings when not provided"""
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI") as mock_client_class:
            with patch("app.services.image.image_gen.image_gen_openai.settings.openai_api_key", "test-api-key"):
                service = ImageGenOpenAI()
                assert service is not None
    
    def test_init_with_empty_api_key(self):
        """Test initialization with empty API key raises ValueError"""
        with pytest.raises(ValueError, match="OPENAI_API_KEY is not set"):
            ImageGenOpenAI(api_key="")


class TestImageGenOpenAIAspectRatioMapping:
    
    def test_aspect_ratio_1_1_maps_to_square(self):
        """Test 1:1 aspect ratio maps to 1024x1024"""
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI"):
            service = ImageGenOpenAI(api_key="test-api-key")
            size = service._map_aspect_ratio_to_size(ImageGenAspectRatio.RATIO_1_1)
            assert size == "1024x1024"
    
    def test_aspect_ratio_9_16_maps_to_portrait(self):
        """Test 9:16 aspect ratio maps to 1024x1536"""
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI"):
            service = ImageGenOpenAI(api_key="test-api-key")
            size = service._map_aspect_ratio_to_size(ImageGenAspectRatio.RATIO_9_16)
            assert size == "1024x1536"
    
    def test_aspect_ratio_16_9_maps_to_landscape(self):
        """Test 16:9 aspect ratio maps to 1536x1024"""
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI"):
            service = ImageGenOpenAI(api_key="test-api-key")
            size = service._map_aspect_ratio_to_size(ImageGenAspectRatio.RATIO_16_9)
            assert size == "1536x1024"
    
    def test_all_aspect_ratios_map_to_valid_sizes(self):
        """Test that all aspect ratios map to valid gpt-image-1 sizes"""
        valid_sizes = {"1024x1024", "1024x1536", "1536x1024"}
        
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI"):
            service = ImageGenOpenAI(api_key="test-api-key")
            
            for aspect_ratio in ImageGenAspectRatio:
                size = service._map_aspect_ratio_to_size(aspect_ratio)
                assert size in valid_sizes


class TestImageGenOpenAIGenerateImage:
    
    def test_generate_image_success(self, mock_openai_client, mock_openai_response):
        """Test successful image generation"""
        mock_openai_client.images.generate.return_value = mock_openai_response
        
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI", return_value=mock_openai_client):
            service = ImageGenOpenAI(api_key="test-api-key")
            request = GenImageRequest(prompt="Generate a beautiful landscape")
            response = service.generate_image(request)
            
            assert response.success is True
            assert response.image_data is not None
            assert response.mimetype == ".png"
            assert response.message == ""
    
    def test_generate_image_with_empty_prompt(self, mock_openai_client):
        """Test image generation with empty prompt returns error"""
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI", return_value=mock_openai_client):
            service = ImageGenOpenAI(api_key="test-api-key")
            request = GenImageRequest(prompt="")
            response = service.generate_image(request)
            
            assert response.success is False
            assert response.message == "Prompt is required"
            assert response.image_data is None
            assert response.text_data is None
            assert response.mimetype is None
    
    def test_generate_image_with_aspect_ratio(self, mock_openai_client, mock_openai_response):
        """Test image generation with custom aspect ratio"""
        mock_openai_client.images.generate.return_value = mock_openai_response
        
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI", return_value=mock_openai_client):
            service = ImageGenOpenAI(api_key="test-api-key")
            request = GenImageRequest(
                prompt="Generate a landscape",
                aspect_ratio=ImageGenAspectRatio.RATIO_16_9
            )
            response = service.generate_image(request)
            
            assert response.success is True
            # Verify the API was called with correct size
            call_args = mock_openai_client.images.generate.call_args
            assert call_args.kwargs["size"] == "1536x1024"
    
    def test_generate_image_with_image_data_logs_warning(self, mock_openai_client, mock_openai_response, sample_image_data):
        """Test that providing image_data logs a warning since gpt-image-1 doesn't support it"""
        mock_openai_client.images.generate.return_value = mock_openai_response
        
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI", return_value=mock_openai_client):
            service = ImageGenOpenAI(api_key="test-api-key")
            request = GenImageRequest(
                prompt="Generate a landscape",
                image_data=sample_image_data
            )
            
            with patch.object(service.logger, 'warning') as mock_warning:
                response = service.generate_image(request)
                
                assert response.success is True
                mock_warning.assert_called_once()
                assert "does not support image-to-image generation" in mock_warning.call_args[0][0]
    
    def test_generate_image_without_revised_prompt(self, mock_openai_client, sample_base64_image):
        """Test image generation when API doesn't return revised prompt"""
        response = MagicMock()
        image_data = MagicMock()
        image_data.b64_json = sample_base64_image
        image_data.revised_prompt = None
        response.data = [image_data]
        
        mock_openai_client.images.generate.return_value = response
        
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI", return_value=mock_openai_client):
            service = ImageGenOpenAI(api_key="test-api-key")
            request = GenImageRequest(prompt="Generate a landscape")
            response = service.generate_image(request)
            
            assert response.success is True
            assert response.text_data == ""
    
    def test_generate_image_with_no_data_in_response(self, mock_openai_client):
        """Test image generation when API returns no data"""
        response = MagicMock()
        response.data = []
        
        mock_openai_client.images.generate.return_value = response
        
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI", return_value=mock_openai_client):
            service = ImageGenOpenAI(api_key="test-api-key")
            request = GenImageRequest(prompt="Generate a landscape")
            response = service.generate_image(request)
            
            assert response.success is False
            assert response.message == "No image data returned from OpenAI"
            assert response.image_data is None
    
    def test_generate_image_with_no_b64_json(self, mock_openai_client):
        """Test image generation when API returns data without b64_json"""
        response = MagicMock()
        image_data = MagicMock()
        image_data.b64_json = None
        response.data = [image_data]
        
        mock_openai_client.images.generate.return_value = response
        
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI", return_value=mock_openai_client):
            service = ImageGenOpenAI(api_key="test-api-key")
            request = GenImageRequest(prompt="Generate a landscape")
            response = service.generate_image(request)
            
            assert response.success is False
            assert response.message == "No base64 image data in response"
            assert response.image_data is None
    
    def test_generate_image_calls_api_with_correct_config(self, mock_openai_client, mock_openai_response):
        """Test that generate_image calls API with correct configuration"""
        mock_openai_client.images.generate.return_value = mock_openai_response
        
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI", return_value=mock_openai_client):
            service = ImageGenOpenAI(api_key="test-api-key")
            request = GenImageRequest(
                prompt="test prompt",
                aspect_ratio=ImageGenAspectRatio.RATIO_1_1
            )
            service.generate_image(request)
            
            # Verify the API was called with correct parameters
            mock_openai_client.images.generate.assert_called_once()
            call_args = mock_openai_client.images.generate.call_args
            
            assert call_args.kwargs["model"] == "gpt-image-1"
            assert call_args.kwargs["prompt"] == "test prompt"
            assert call_args.kwargs["size"] == "1024x1024"
            assert call_args.kwargs["quality"] == "medium"
            assert call_args.kwargs["n"] == 1
    
    def test_generate_image_exception_handling(self, mock_openai_client):
        """Test that exceptions from API are caught and returned in response"""
        mock_openai_client.images.generate.side_effect = Exception("API error")
        
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI", return_value=mock_openai_client):
            service = ImageGenOpenAI(api_key="test-api-key")
            request = GenImageRequest(prompt="Generate an image")
            response = service.generate_image(request)
            
            assert response.success is False
            assert response.image_data is None
            assert response.text_data is None
            assert response.mimetype is None
            assert "Failed to generate image with OpenAI: API error" in response.message
    
    def test_generate_image_with_default_aspect_ratio(self, mock_openai_client, mock_openai_response):
        """Test that default aspect ratio is 1:1"""
        mock_openai_client.images.generate.return_value = mock_openai_response
        
        with patch("app.services.image.image_gen.image_gen_openai.OpenAI", return_value=mock_openai_client):
            service = ImageGenOpenAI(api_key="test-api-key")
            request = GenImageRequest(prompt="Generate a landscape")
            service.generate_image(request)
            
            # Verify the API was called with default size
            call_args = mock_openai_client.images.generate.call_args
            assert call_args.kwargs["size"] == "1024x1024"

