import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.plant.plant_service import PlantService
from app.classes.plant import (
    HumidityPreference,
    LightRequirement,
    CreateOrUpdatePlantRequest,
    CreateOrUpdatePlantResponse,
    PlantResponse,
    PlantListResponse,
    AddPlantPhotoRequest,
    PlantPhotoResponse,
    PlantHealthStatus,
    PlantSpecies,
)
from app.classes.image import ImageType, ImageCreateResponse


@pytest.fixture
def plant_service():
    """Create a fresh instance for each test"""
    # Reset the singleton instance
    PlantService._instance = None
    return PlantService()


@pytest.fixture
def mock_plant_data():
    """Mock plant data for testing"""
    return {
        "_id": "test_plant_123",
        "id": "test_plant_123",  # Include both _id and id for PlantInfo model
        "name": "Test Plant",
        "species": PlantSpecies.SUCCULENT,
        "species_details": "Echeveria",
        "description": "A beautiful succulent",
        "location": "Living room",
        "acquisition_date": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "current_health_status": PlantHealthStatus.GOOD,
        "watering_frequency_days": 7,
        "light_requirements": LightRequirement.BRIGHT_INDIRECT,
        "humidity_preference": HumidityPreference.LOW,
        "temperature_range": "18-24°C",
        "photos": ["photo_123", "photo_456"],
        "ai_care_tips": ["Water sparingly", "Provide bright light"],
    }


@pytest.fixture
def create_plant_request():
    """Valid create plant request"""
    return CreateOrUpdatePlantRequest(
        name="New Plant",
        species=PlantSpecies.TROPICAL,
        species_details="Monstera deliciosa",
        description="A tropical plant",
        location="Bedroom",
        watering_frequency_days=5,
        light_requirements=LightRequirement.BRIGHT_INDIRECT,
        humidity_preference=HumidityPreference.HIGH,
        temperature_range="20-26°C",
    )


@pytest.fixture
def update_plant_request():
    """Valid update plant request"""
    return CreateOrUpdatePlantRequest(
        id="test_plant_123",
        name="Updated Plant",
        species=PlantSpecies.FLOWERING,
        species_details="Updated species",
        description="Updated description",
        location="Updated location",
        watering_frequency_days=3,
        light_requirements=LightRequirement.LOW,
        humidity_preference=HumidityPreference.MEDIUM,
        temperature_range="15-22°C",
    )


@pytest.fixture
def add_photo_request():
    """Valid add photo request"""
    return AddPlantPhotoRequest(
        plant_id="test_plant_123",
        filename="plant_photo.jpg",
        file_data=b"fake image data",
    )


class TestPlantServiceSingleton:

    def test_singleton_instance(self):
        """Test that PlantService is a singleton"""
        service1 = PlantService()
        service2 = PlantService()
        assert service1 is service2

class TestPlantServiceValidation:

    # Validation Tests
    def test_validate_create_plant_request_valid(self, plant_service, create_plant_request):
        """Test validation with valid create request"""
        valid, error_msg = plant_service._validate_create_plant_request(create_plant_request)
        assert valid is True
        assert error_msg == ""

    def test_validate_create_plant_request_missing_name(self, plant_service):
        """Test validation with missing name"""
        request = CreateOrUpdatePlantRequest(name="")
        valid, error_msg = plant_service._validate_create_plant_request(request)
        assert valid is False
        assert error_msg == "Plant name is required"

    def test_validate_create_plant_request_none_name(self, plant_service):
        """Test validation with None name"""
        request = CreateOrUpdatePlantRequest(name=None)
        valid, error_msg = plant_service._validate_create_plant_request(request)
        assert valid is False
        assert error_msg == "Plant name is required"

    def test_validate_create_plant_request_whitespace_name(self, plant_service):
        """Test validation with whitespace-only name"""
        request = CreateOrUpdatePlantRequest(name="   ")
        valid, error_msg = plant_service._validate_create_plant_request(request)
        assert valid is False
        assert error_msg == "Plant name is required"

    def test_validate_update_plant_request_valid(self, plant_service, update_plant_request):
        """Test validation with valid update request"""
        valid, error_msg = plant_service._validate_update_plant_request(update_plant_request)
        assert valid is True
        assert error_msg == ""

    def test_validate_update_plant_request_missing_id(self, plant_service):
        """Test validation with missing ID"""
        request = CreateOrUpdatePlantRequest(id="", name="Test Plant")
        valid, error_msg = plant_service._validate_update_plant_request(request)
        assert valid is False
        assert error_msg == "Plant ID is required"

    def test_validate_update_plant_request_none_id(self, plant_service):
        """Test validation with None ID"""
        request = CreateOrUpdatePlantRequest(id=None, name="Test Plant")
        valid, error_msg = plant_service._validate_update_plant_request(request)
        assert valid is False
        assert error_msg == "Plant ID is required"

class TestPlantServiceCreateOrUpdatePlant:

    @pytest.mark.asyncio
    async def test_create_plant_success(self, plant_service, create_plant_request):
        """Test successful plant creation"""
        with patch("app.services.plant.plant_service.insert_document", return_value="new_plant_123"):
            response = await plant_service.create_or_update_plant(create_plant_request)
            
            assert isinstance(response, CreateOrUpdatePlantResponse)
            assert response.success is True
            assert response.id == "new_plant_123"
            assert response.message == "Plant saved successfully"

    @pytest.mark.asyncio
    async def test_create_plant_validation_failure(self, plant_service):
        """Test plant creation with validation failure"""
        invalid_request = CreateOrUpdatePlantRequest(name="")
        
        response = await plant_service.create_or_update_plant(invalid_request)
        
        assert isinstance(response, CreateOrUpdatePlantResponse)
        assert response.success is False
        assert response.id == ""
        assert response.message == "Plant name is required"

    @pytest.mark.asyncio
    async def test_create_plant_with_default_values(self, plant_service):
        """Test plant creation with minimal data uses defaults"""
        request = CreateOrUpdatePlantRequest(name="Minimal Plant")
        
        with patch("app.services.plant.plant_service.insert_document", return_value="new_plant_123") as mock_insert:
            response = await plant_service.create_or_update_plant(request)
            
            assert response.success is True
            # Check that insert_document was called with proper defaults
            mock_insert.assert_called_once()
            plant_data = mock_insert.call_args[0][1]
            assert plant_data["name"] == "Minimal Plant"
            assert plant_data["species"] == PlantSpecies.OTHER.value
            assert plant_data["current_health_status"] == PlantHealthStatus.UNKNOWN.value
            assert plant_data["photos"] == []
            assert plant_data["ai_care_tips"] == []

    @pytest.mark.asyncio
    async def test_create_plant_exception(self, plant_service, create_plant_request):
        """Test plant creation with database exception"""
        with patch("app.services.plant.plant_service.insert_document", side_effect=Exception("Database error")):
            response = await plant_service.create_or_update_plant(create_plant_request)
            
            assert isinstance(response, CreateOrUpdatePlantResponse)
            assert response.success is False
            assert response.id == ""
            assert "Failed to save plant: Database error" in response.message

    # Update Plant Tests
    @pytest.mark.asyncio
    async def test_update_plant_success(self, plant_service, update_plant_request, mock_plant_data):
        """Test successful plant update"""
        with patch("app.services.plant.plant_service.MongoDB") as mock_mongodb_class, \
             patch("app.services.plant.plant_service.update_document") as mock_update, \
             patch("app.services.plant.plant_service.build_update_data", return_value={"name": "Updated Plant"}):
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_plant_data)
            
            response = await plant_service.create_or_update_plant(update_plant_request)
            
            assert isinstance(response, CreateOrUpdatePlantResponse)
            assert response.success is True
            assert response.id == "test_plant_123"
            assert response.message == "Plant saved successfully"
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_plant_not_found(self, plant_service, update_plant_request):
        """Test plant update when plant doesn't exist"""
        with patch("app.services.plant.plant_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=None)
            response = await plant_service.create_or_update_plant(update_plant_request)
            
            assert isinstance(response, CreateOrUpdatePlantResponse)
            assert response.success is False
            assert response.id == ""
            assert response.message == "Plant not found"

    @pytest.mark.asyncio
    async def test_update_plant_validation_failure(self, plant_service):
        """Test plant update with validation failure - empty string ID should be treated as create request"""
        # Empty string ID is treated as create request, not update, so it will fail create validation
        invalid_request = CreateOrUpdatePlantRequest(id="", name="")
        
        response = await plant_service.create_or_update_plant(invalid_request)
        
        assert isinstance(response, CreateOrUpdatePlantResponse)
        assert response.success is False
        assert response.id == ""
        assert response.message == "Plant name is required"
        
    @pytest.mark.asyncio 
    async def test_update_plant_with_none_id_validation_failure(self, plant_service):
        """Test plant update validation with None ID should be treated as create"""
        invalid_request = CreateOrUpdatePlantRequest(id=None, name="")
        
        response = await plant_service.create_or_update_plant(invalid_request)
        
        assert isinstance(response, CreateOrUpdatePlantResponse)
        assert response.success is False
        assert response.id == ""
        assert response.message == "Plant name is required"

    @pytest.mark.asyncio
    async def test_update_plant_exception(self, plant_service, update_plant_request, mock_plant_data):
        """Test plant update with database exception"""
        with patch("app.services.plant.plant_service.MongoDB") as mock_mongodb_class, \
             patch("app.services.plant.plant_service.update_document", side_effect=Exception("Database error")):
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_plant_data)
            
            response = await plant_service.create_or_update_plant(update_plant_request)
            
            assert isinstance(response, CreateOrUpdatePlantResponse)
            assert response.success is False
            assert response.id == ""
            assert "Failed to save plant: Database error" in response.message

class TestPlantServiceGetPlant:

    @pytest.mark.asyncio
    async def test_get_plant_success(self, plant_service, mock_plant_data):
        """Test successful plant retrieval"""
        with patch("app.services.plant.plant_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_plant_data)
            
            response = await plant_service.get_plant("test_plant_123")
            
            assert isinstance(response, PlantResponse)
            assert response.success is True
            assert response.plant is not None
            assert response.plant.id == "test_plant_123"
            assert response.plant.name == "Test Plant"
            assert response.plant.species == PlantSpecies.SUCCULENT
            assert response.message == "Plant retrieved successfully"

    @pytest.mark.asyncio
    async def test_get_plant_not_found(self, plant_service):
        """Test plant retrieval when plant doesn't exist"""
        with patch("app.services.plant.plant_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=None)
            
            response = await plant_service.get_plant("nonexistent_id")
            
            assert isinstance(response, PlantResponse)
            assert response.success is False
            assert response.plant is None
            assert response.message == "Plant not found"

    @pytest.mark.asyncio
    async def test_get_plant_exception(self, plant_service):
        """Test plant retrieval with database exception"""
        with patch("app.services.plant.plant_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(side_effect=Exception("Database error"))
            
            response = await plant_service.get_plant("test_plant_123")
            
            assert isinstance(response, PlantResponse)
            assert response.success is False
            assert response.plant is None
            assert "Failed to get plant: Database error" in response.message

class TestPlantServiceListPlants:

    @pytest.mark.asyncio
    async def test_list_plants_success(self, plant_service, mock_plant_data):
        """Test successful plants listing"""
        plants_data = [mock_plant_data, {**mock_plant_data, "_id": "plant_456", "name": "Plant 2"}]
        
        with patch("app.services.plant.plant_service.list_documents", return_value=plants_data):
            response = await plant_service.list_plants()
            
            assert isinstance(response, PlantListResponse)
            assert len(response.plants) == 2
            assert response.plants[0].name == "Test Plant"
            assert response.plants[1].name == "Plant 2"

    @pytest.mark.asyncio
    async def test_list_plants_empty(self, plant_service):
        """Test plants listing with no plants"""
        with patch("app.services.plant.plant_service.list_documents", return_value=[]):
            response = await plant_service.list_plants()
            
            assert isinstance(response, PlantListResponse)
            assert len(response.plants) == 0

    @pytest.mark.asyncio
    async def test_list_plants_exception(self, plant_service):
        """Test plants listing with database exception"""
        with patch("app.services.plant.plant_service.list_documents", side_effect=Exception("Database error")):
            response = await plant_service.list_plants()
            
            assert isinstance(response, PlantListResponse)
            assert len(response.plants) == 0

class TestPlantServiceAddPlantPhoto:
    
    @pytest.mark.asyncio
    async def test_add_plant_photo_success(self, plant_service, add_photo_request, mock_plant_data):
        """Test successful photo addition"""
        mock_image_service = MagicMock()
        mock_image_response = ImageCreateResponse(
            success=True,
            image_id="new_photo_789",
            storage_path="images/plants/photo.jpg",
            storage_url="http://storage.url/photo.jpg",
            message="Success"
        )
        mock_image_service.create_image = AsyncMock(return_value=mock_image_response)
        
        with patch("app.services.plant.plant_service.MongoDB") as mock_mongodb_class, \
             patch("app.services.plant.plant_service.ImageService", return_value=mock_image_service), \
             patch("app.services.plant.plant_service.update_document") as mock_update:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_plant_data)
            
            response = await plant_service.add_plant_photo("test_plant_123", add_photo_request)
            
            assert isinstance(response, PlantPhotoResponse)
            assert response.success is True
            assert response.photo_id == "new_photo_789"
            assert response.message == ""
            
            # Verify image service was called with correct parameters
            mock_image_service.create_image.assert_called_once()
            create_request = mock_image_service.create_image.call_args[0][0]
            assert create_request.filename == "plant_photo.jpg"
            assert create_request.image_type == ImageType.PLANT_PHOTO
            assert create_request.file_data == b"fake image data"
            
            # Verify plant was updated with new photo
            mock_update.assert_called_once()
            update_data = mock_update.call_args[0][2]
            assert "new_photo_789" in update_data["photos"]
            assert "last_photo_date" in update_data
            assert "updated_at" in update_data

    @pytest.mark.asyncio
    async def test_add_plant_photo_plant_not_found(self, plant_service, add_photo_request):
        """Test photo addition when plant doesn't exist"""
        with patch("app.services.plant.plant_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=None)
            
            response = await plant_service.add_plant_photo("nonexistent_id", add_photo_request)
            
            assert isinstance(response, PlantPhotoResponse)
            assert response.success is False
            assert response.photo_id == ""
            assert response.message == "Plant not found"

    @pytest.mark.asyncio
    async def test_add_plant_photo_image_upload_failure(self, plant_service, add_photo_request, mock_plant_data):
        """Test photo addition when image upload fails"""
        mock_image_service = MagicMock()
        mock_image_response = ImageCreateResponse(
            success=False,
            image_id="",
            storage_path="",
            storage_url="",
            message="Upload failed"
        )
        mock_image_service.create_image = AsyncMock(return_value=mock_image_response)
        
        with patch("app.services.plant.plant_service.MongoDB") as mock_mongodb_class, \
             patch("app.services.plant.plant_service.ImageService", return_value=mock_image_service):
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(return_value=mock_plant_data)
            
            response = await plant_service.add_plant_photo("test_plant_123", add_photo_request)
            
            assert isinstance(response, PlantPhotoResponse)
            assert response.success is False
            assert response.photo_id == ""
            assert "Failed to upload image: Upload failed" in response.message

    @pytest.mark.asyncio
    async def test_add_plant_photo_exception(self, plant_service, add_photo_request):
        """Test photo addition with exception"""
        with patch("app.services.plant.plant_service.MongoDB") as mock_mongodb_class:
            mock_mongodb_instance = MagicMock()
            mock_mongodb_class.return_value = mock_mongodb_instance
            mock_mongodb_instance.get_document = AsyncMock(side_effect=Exception("Database error"))
            
            response = await plant_service.add_plant_photo("test_plant_123", add_photo_request)
            
            assert isinstance(response, PlantPhotoResponse)
            assert response.success is False
            assert response.photo_id == ""
            assert "Failed to add photo: Database error" in response.message