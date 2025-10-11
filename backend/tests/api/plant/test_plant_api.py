import pytest
import io
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock
from app.api.plant_api import router
from app.classes.plant import (
    CreateOrUpdatePlantResponse,
    PlantResponse,
    PlantListResponse,
    PlantPhotoResponse,
    PlantInfo,
    PlantSpecies,
    PlantHealthStatus,
    LightRequirement,
    HumidityPreference,
)

app = FastAPI()
app.include_router(router, prefix="/plants")


@pytest.fixture
def sample_plant_info():
    """Sample plant info for testing"""
    return PlantInfo(
        id="test_plant_id",
        name="Monstera Deliciosa",
        species=PlantSpecies.TROPICAL,
        species_details="Swiss Cheese Plant",
        description="Beautiful tropical houseplant",
        location="Living room",
        acquisition_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        current_health_status=PlantHealthStatus.GOOD,
        watering_frequency_days=7,
        light_requirements=LightRequirement.BRIGHT_INDIRECT,
        humidity_preference=HumidityPreference.HIGH,
        temperature_range="18-24°C",
        photos=["photo_1", "photo_2"],
        ai_care_tips=["Keep soil slightly moist", "Provide bright indirect light"],
    )


@pytest.fixture
def sample_create_plant_request():
    """Sample create plant request for testing"""
    return {
        "name": "Fiddle Leaf Fig",
        "species": PlantSpecies.TROPICAL.value,
        "species_details": "Ficus lyrata",
        "description": "Popular houseplant with large leaves",
        "location": "Living room corner",
        "watering_frequency_days": 10,
        "light_requirements": LightRequirement.BRIGHT_INDIRECT.value,
        "humidity_preference": HumidityPreference.MEDIUM.value,
        "temperature_range": "18-26°C",
    }


@pytest.fixture
def sample_update_plant_request():
    """Sample update plant request for testing"""
    return {
        "id": "existing_plant_id",
        "name": "Updated Fiddle Leaf Fig",
        "description": "Updated description",
        "location": "New location",
        "watering_frequency_days": 14,
        "last_watered": datetime.now(timezone.utc).isoformat(),
    }


class TestCreatePlantEndpoint:
    """Test cases for creating plants"""

    @pytest.mark.asyncio
    async def test_create_plant_success(self, sample_create_plant_request):
        """Test successful plant creation"""
        mock_response = CreateOrUpdatePlantResponse(
            success=True,
            id="new_plant_id",
            message="Plant saved successfully"
        )
        
        with patch("app.services.plant.plant_service.PlantService.create_or_update_plant", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/plants/", json=sample_create_plant_request)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["id"] == "new_plant_id"
                assert data["message"] == "Plant saved successfully"

    @pytest.mark.asyncio
    async def test_create_plant_minimal_data(self):
        """Test creating plant with minimal required data"""
        minimal_request = {
            "name": "Simple Plant"
        }
        
        mock_response = CreateOrUpdatePlantResponse(
            success=True,
            id="minimal_plant_id",
            message="Plant saved successfully"
        )
        
        with patch("app.services.plant.plant_service.PlantService.create_or_update_plant", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/plants/", json=minimal_request)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["id"] == "minimal_plant_id"

    @pytest.mark.asyncio
    async def test_create_plant_validation_failure(self):
        """Test plant creation with validation failure"""
        invalid_request = {
            "name": ""  # Empty name should fail validation
        }
        
        mock_response = CreateOrUpdatePlantResponse(
            success=False,
            id="",
            message="Plant name is required"
        )
        
        with patch("app.services.plant.plant_service.PlantService.create_or_update_plant", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/plants/", json=invalid_request)
                
                # The API returns 500 for business logic failures, not 400
                assert response.status_code == 500
                data = response.json()
                assert "Plant name is required" in data["detail"]

    @pytest.mark.asyncio
    async def test_create_plant_service_exception(self, sample_create_plant_request):
        """Test plant creation when service raises exception"""
        with patch("app.services.plant.plant_service.PlantService.create_or_update_plant", new=AsyncMock(side_effect=Exception("Database error"))):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/plants/", json=sample_create_plant_request)
                
                assert response.status_code == 500
                data = response.json()
                assert "Failed to create or update plant" in data["detail"]
                assert "Database error" in data["detail"]


class TestUpdatePlantEndpoint:
    """Test cases for updating plants"""

    @pytest.mark.asyncio
    async def test_update_plant_success(self, sample_update_plant_request):
        """Test successful plant update"""
        mock_response = CreateOrUpdatePlantResponse(
            success=True,
            id="existing_plant_id",
            message="Plant saved successfully"
        )
        
        with patch("app.services.plant.plant_service.PlantService.create_or_update_plant", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/plants/", json=sample_update_plant_request)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["id"] == "existing_plant_id"
                assert data["message"] == "Plant saved successfully"

    @pytest.mark.asyncio
    async def test_update_plant_not_found(self):
        """Test updating non-existent plant"""
        update_request = {
            "id": "nonexistent_plant_id",
            "name": "Updated Plant"
        }
        
        mock_response = CreateOrUpdatePlantResponse(
            success=False,
            id="",
            message="Plant not found"
        )
        
        with patch("app.services.plant.plant_service.PlantService.create_or_update_plant", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/plants/", json=update_request)
                
                # The API returns 500 for business logic failures, not 400
                assert response.status_code == 500
                data = response.json()
                assert "Plant not found" in data["detail"]

    @pytest.mark.asyncio
    async def test_update_plant_partial_data(self):
        """Test updating plant with partial data"""
        partial_update = {
            "id": "existing_plant_id",
            "location": "New location only"
        }
        
        mock_response = CreateOrUpdatePlantResponse(
            success=True,
            id="existing_plant_id",
            message="Plant saved successfully"
        )
        
        with patch("app.services.plant.plant_service.PlantService.create_or_update_plant", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/plants/", json=partial_update)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True


class TestGetPlantEndpoint:
    """Test cases for getting individual plants"""

    @pytest.mark.asyncio
    async def test_get_plant_success(self, sample_plant_info):
        """Test successful plant retrieval"""
        mock_response = PlantResponse(
            success=True,
            plant=sample_plant_info,
            message="Plant retrieved successfully"
        )
        
        with patch("app.services.plant.plant_service.PlantService.get_plant", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/plants/test_plant_id")
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["plant"]["id"] == "test_plant_id"
                assert data["plant"]["name"] == "Monstera Deliciosa"
                assert data["plant"]["species"] == PlantSpecies.TROPICAL.value
                assert data["message"] == "Plant retrieved successfully"

    @pytest.mark.asyncio
    async def test_get_plant_not_found(self):
        """Test getting non-existent plant"""
        mock_response = PlantResponse(
            success=False,
            plant=None,
            message="Plant not found"
        )
        
        with patch("app.services.plant.plant_service.PlantService.get_plant", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/plants/nonexistent_id")
                
                assert response.status_code == 404
                data = response.json()
                assert "Plant not found" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_plant_service_exception(self):
        """Test get plant when service raises exception"""
        with patch("app.services.plant.plant_service.PlantService.get_plant", new=AsyncMock(side_effect=Exception("Database error"))):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                # The get_plant endpoint doesn't catch exceptions, so the exception will be raised
                with pytest.raises(Exception, match="Database error"):
                    await ac.get("/plants/test_id")


class TestListPlantsEndpoint:
    """Test cases for listing plants"""

    @pytest.mark.asyncio
    async def test_list_plants_success(self, sample_plant_info):
        """Test successful plants listing"""
        plant2 = PlantInfo(
            id="plant_2",
            name="Snake Plant",
            species=PlantSpecies.SUCCULENT,
            description="Low maintenance plant",
            location="Bedroom",
            acquisition_date=datetime(2024, 1, 15, tzinfo=timezone.utc),
            created_at=datetime(2024, 1, 15, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 15, tzinfo=timezone.utc),
            current_health_status=PlantHealthStatus.EXCELLENT,
        )
        
        mock_response = PlantListResponse(plants=[sample_plant_info, plant2])
        
        with patch("app.services.plant.plant_service.PlantService.list_plants", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/plants/")
                
                assert response.status_code == 200
                data = response.json()
                assert "plants" in data
                assert len(data["plants"]) == 2
                assert data["plants"][0]["name"] == "Monstera Deliciosa"
                assert data["plants"][1]["name"] == "Snake Plant"

    @pytest.mark.asyncio
    async def test_list_plants_empty(self):
        """Test listing plants when no plants exist"""
        mock_response = PlantListResponse(plants=[])
        
        with patch("app.services.plant.plant_service.PlantService.list_plants", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/plants/")
                
                assert response.status_code == 200
                data = response.json()
                assert "plants" in data
                assert len(data["plants"]) == 0

    @pytest.mark.asyncio
    async def test_list_plants_service_exception(self):
        """Test list plants when service raises exception"""
        with patch("app.services.plant.plant_service.PlantService.list_plants", new=AsyncMock(side_effect=Exception("Database error"))):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                # The list_plants endpoint doesn't catch exceptions, so the exception will be raised
                with pytest.raises(Exception, match="Database error"):
                    await ac.get("/plants/")


class TestAddPlantPhotoEndpoint:
    """Test cases for adding plant photos"""

    @pytest.mark.asyncio
    async def test_add_plant_photo_success(self):
        """Test successful photo upload"""
        mock_response = PlantPhotoResponse(
            success=True,
            photo_id="new_photo_id",
            message="Photo uploaded successfully"
        )
        
        # Create a test image file
        test_image_content = b"fake image content for testing"
        test_image = io.BytesIO(test_image_content)
        
        with patch("app.services.plant.plant_service.PlantService.add_plant_photo", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                files = {"file": ("plant_photo.jpg", test_image, "image/jpeg")}
                response = await ac.post("/plants/test_plant_id/photo", files=files)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["photo_id"] == "new_photo_id"
                assert data["message"] == "Photo uploaded successfully"

    @pytest.mark.asyncio
    async def test_add_plant_photo_empty_plant_id(self):
        """Test photo upload with empty plant ID via parameter validation"""
        test_image_content = b"fake image content"
        test_image = io.BytesIO(test_image_content)
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            files = {"file": ("plant_photo.jpg", test_image, "image/jpeg")}
            # Use space character as plant ID which should fail validation
            response = await ac.post("/plants/ /photo", files=files)  
            
            assert response.status_code == 400
            data = response.json()
            assert "Plant ID is required" in data["detail"]

    @pytest.mark.asyncio
    async def test_add_plant_photo_invalid_route(self):
        """Test photo upload with malformed URL"""
        test_image_content = b"fake image content"
        test_image = io.BytesIO(test_image_content)
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            files = {"file": ("plant_photo.jpg", test_image, "image/jpeg")}
            response = await ac.post("/plants//photo", files=files)  # Empty plant ID in URL
            
            # This will return 404 for invalid URL route
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_add_plant_photo_no_file(self):
        """Test photo upload without file"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/plants/test_plant_id/photo")
            
            assert response.status_code == 422  # Validation error for missing file

    @pytest.mark.asyncio
    async def test_add_plant_photo_plant_not_found(self):
        """Test photo upload for non-existent plant"""
        mock_response = PlantPhotoResponse(
            success=False,
            photo_id="",
            message="Plant not found"
        )
        
        test_image_content = b"fake image content"
        test_image = io.BytesIO(test_image_content)
        
        with patch("app.services.plant.plant_service.PlantService.add_plant_photo", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                files = {"file": ("plant_photo.jpg", test_image, "image/jpeg")}
                response = await ac.post("/plants/nonexistent_id/photo", files=files)
                
                # The API returns 500 for business logic failures, not 400
                assert response.status_code == 500
                data = response.json()
                assert "Plant not found" in data["detail"]

    @pytest.mark.asyncio
    async def test_add_plant_photo_service_exception(self):
        """Test photo upload when service raises exception"""
        test_image_content = b"fake image content"
        test_image = io.BytesIO(test_image_content)
        
        with patch("app.services.plant.plant_service.PlantService.add_plant_photo", new=AsyncMock(side_effect=Exception("Storage error"))):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                files = {"file": ("plant_photo.jpg", test_image, "image/jpeg")}
                response = await ac.post("/plants/test_plant_id/photo", files=files)
                
                assert response.status_code == 500
                data = response.json()
                assert "Failed to upload photo" in data["detail"]
                assert "Storage error" in data["detail"]


class TestPlantAPIEdgeCases:
    """Test cases for edge cases and validation"""

    @pytest.mark.asyncio
    async def test_create_plant_with_all_enum_values(self):
        """Test creating plant with all possible enum values"""
        for species in PlantSpecies:
            for light_req in LightRequirement:
                for humidity in HumidityPreference:
                    request_data = {
                        "name": f"Test Plant {species.value}",
                        "species": species.value,
                        "light_requirements": light_req.value,
                        "humidity_preference": humidity.value,
                    }
                    
                    mock_response = CreateOrUpdatePlantResponse(
                        success=True,
                        id=f"plant_{species.value}",
                        message="Plant saved successfully"
                    )
                    
                    with patch("app.services.plant.plant_service.PlantService.create_or_update_plant", new=AsyncMock(return_value=mock_response)):
                        transport = ASGITransport(app=app)
                        async with AsyncClient(transport=transport, base_url="http://test") as ac:
                            response = await ac.post("/plants/", json=request_data)
                            
                            assert response.status_code == 200
                            data = response.json()
                            assert data["success"] is True

    @pytest.mark.asyncio
    async def test_add_photo_with_various_file_types(self):
        """Test adding photos with different file types"""
        file_types = [
            ("test.jpg", "image/jpeg"),
            ("test.png", "image/png"),
            ("test.gif", "image/gif"),
            ("test.webp", "image/webp"),
        ]
        
        for filename, content_type in file_types:
            mock_response = PlantPhotoResponse(
                success=True,
                photo_id=f"photo_{filename}",
                message="Photo uploaded successfully"
            )
            
            test_image_content = b"fake image content"
            test_image = io.BytesIO(test_image_content)
            
            with patch("app.services.plant.plant_service.PlantService.add_plant_photo", new=AsyncMock(return_value=mock_response)):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as ac:
                    files = {"file": (filename, test_image, content_type)}
                    response = await ac.post("/plants/test_plant_id/photo", files=files)
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True
                    assert data["photo_id"] == f"photo_{filename}"

    @pytest.mark.asyncio
    async def test_plant_api_with_special_characters(self):
        """Test plant operations with special characters"""
        request_data = {
            "name": "植物 with émojis 🌱 and symbols ❤️",
            "species": PlantSpecies.OTHER.value,
            "description": "Test with üñíçödé characters & symbols",
            "location": "Côté fenêtre près de l'étagère"
        }
        
        mock_response = CreateOrUpdatePlantResponse(
            success=True,
            id="unicode_plant_id",
            message="Plant saved successfully"
        )
        
        with patch("app.services.plant.plant_service.PlantService.create_or_update_plant", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/plants/", json=request_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["id"] == "unicode_plant_id"
