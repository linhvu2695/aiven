import base64
import logging
from datetime import datetime, timezone
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from app.classes.plant import (
    HumidityPreference,
    LightRequirement,
    PlantAutofillResponseFormat,
    PlantInfo,
    CreateOrUpdatePlantRequest,
    CreateOrUpdatePlantResponse,
    PlantResponse,
    PlantListResponse,
    AddPlantPhotoRequest,
    PlantPhotoResponse,
    AutofillPlantInfoResponse,
    PlantHealthStatus,
    PlantSpecies,
)
from app.classes.image import ImageType, CreateImageRequest
from app.core.database import (
    insert_document,
    MongoDB,
    update_document,
    list_documents,
)
from app.services.image.image_service import ImageService
from app.utils.string.string_utils import is_empty_string
from app.utils.request.request_utils import build_update_data
from app.services.chat.chat_constants import LLMModel
from app.services.chat.chat_service import ChatService
from app.classes.chat import ChatFileContent
from app.utils.image.image_utils import detect_image_mime_type

PLANT_COLLECTION_NAME = "plants"


class PlantService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(PlantService, cls).__new__(cls)
        return cls._instance

    def _validate_create_plant_request(
        self, request: CreateOrUpdatePlantRequest
    ) -> tuple[bool, str]:
        """Validate create plant request"""
        if not request.name or request.name.strip() == "":
            return False, "Plant name is required"
        return True, ""

    def _validate_update_plant_request(
        self, request: CreateOrUpdatePlantRequest
    ) -> tuple[bool, str]:
        """Validate update plant request"""
        if not request.id or request.id.strip() == "":
            return False, "Plant ID is required"
        return True, ""
        
    async def create_or_update_plant(
        self, request: CreateOrUpdatePlantRequest
    ) -> CreateOrUpdatePlantResponse:
        """Create a new plant or update an existing one"""
        try:
            now = datetime.now(timezone.utc)
            is_update = request.id and not is_empty_string(request.id)

            if is_update:
                # Validate update request
                is_valid, error_msg = self._validate_update_plant_request(request)
                if not is_valid:
                    return CreateOrUpdatePlantResponse(
                        success=False, id="", message=error_msg
                    )

                # Check if plant exists before updating
                existing_plant = await MongoDB().get_document(
                    PLANT_COLLECTION_NAME, str(request.id)
                )
                if not existing_plant:
                    return CreateOrUpdatePlantResponse(
                        success=False, id="", message="Plant not found"
                    )

                # Update plant
                update_data = build_update_data(
                    request=request,
                    fields=[
                        "name",
                        "species",
                        "species_details",
                        "description",
                        "location",
                        "watering_frequency_days",
                        "light_requirements",
                        "humidity_preference",
                        "temperature_range",
                        "last_watered",
                        "last_fertilized",
                    ],
                )
                update_data["updated_at"] = now.isoformat()
                await update_document(
                    PLANT_COLLECTION_NAME, str(request.id), update_data
                )
                plant_id = str(request.id)

            else:
                # Validate create request
                is_valid, error_msg = self._validate_create_plant_request(request)
                if not is_valid:
                    return CreateOrUpdatePlantResponse(
                        success=False, id="", message=error_msg
                    )

                # Create new plant
                plant_data = {
                    "name": request.name,
                    "species": (
                        request.species.value
                        if request.species
                        else PlantSpecies.OTHER.value
                    ),
                    "species_details": request.species_details,
                    "description": request.description,
                    "location": request.location,
                    "acquisition_date": request.acquisition_date or now,
                    "created_at": now,
                    "updated_at": now,
                    "current_health_status": PlantHealthStatus.UNKNOWN.value,
                    "watering_frequency_days": request.watering_frequency_days,
                    "light_requirements": request.light_requirements,
                    "humidity_preference": request.humidity_preference,
                    "temperature_range": request.temperature_range,
                    "photos": [],
                    "ai_care_tips": [],
                }

                plant_id = await insert_document(PLANT_COLLECTION_NAME, plant_data)

            return CreateOrUpdatePlantResponse(
                success=True, id=plant_id, message="Plant saved successfully"
            )

        except Exception as e:
            logging.getLogger("uvicorn.error").error(
                f"Error creating/updating plant: {e}"
            )
            return CreateOrUpdatePlantResponse(
                success=False, id="", message=f"Failed to save plant: {str(e)}"
            )

    async def get_plant(self, plant_id: str) -> PlantResponse:
        """Get a plant by ID"""
        try:
            plant_data = await MongoDB().get_document(PLANT_COLLECTION_NAME, str(plant_id), True)
            if not plant_data:
                return PlantResponse(
                    success=False, plant=None, message="Plant not found"
                )

            # Convert to PlantInfo model
            plant = PlantInfo(**plant_data)

            return PlantResponse(
                success=True, plant=plant, message="Plant retrieved successfully"
            )

        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Error getting plant: {e}")
            return PlantResponse(
                success=False, plant=None, message=f"Failed to get plant: {str(e)}"
            )

    async def list_plants(self) -> PlantListResponse:
        """List all plants"""
        try:
            plants_data = await list_documents(PLANT_COLLECTION_NAME, True)
            plants = [PlantInfo(**plant_data) for plant_data in plants_data]

            return PlantListResponse(plants=plants)

        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Error listing plants: {e}")
            return PlantListResponse(plants=[])

    async def add_plant_photo(
        self, plant_id: str, request: AddPlantPhotoRequest
    ) -> PlantPhotoResponse:
        """Add a photo to a plant"""
        try:
            # Check if plant exists
            plant_data = await MongoDB().get_document(PLANT_COLLECTION_NAME, plant_id)
            if not plant_data:
                return PlantPhotoResponse(
                    success=False, photo_id="", message="Plant not found"
                )

            # Create image using ImageService
            image_request = CreateImageRequest(
                filename=request.filename,
                image_type=ImageType.PLANT_PHOTO,
                file_data=request.file_data,
            )

            image_response = await ImageService().create_image(image_request)
            if not image_response.success:
                return PlantPhotoResponse(
                    success=False,
                    photo_id="",
                    message=f"Failed to upload image: {image_response.message}",
                )

            # Add photo to plant's photos list
            photos = plant_data.get("photos", [])
            photos.append(image_response.image_id)

            # Update plant with new photo and last photo date
            update_data = {
                "photos": photos,
                "last_photo_date": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

            await update_document(PLANT_COLLECTION_NAME, plant_id, update_data)

            return PlantPhotoResponse(
                success=True, photo_id=image_response.image_id, message=""
            )

        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Error adding plant photo: {e}")
            return PlantPhotoResponse(
                success=False, photo_id="", message=f"Failed to add photo: {str(e)}"
            )

    async def autofill_plant_info(
        self, image_bytes: bytes
    ) -> AutofillPlantInfoResponse:
        """Analyze plant health using AI (placeholder for future implementation)"""
        model = LLMModel.GPT_4O
        try:
            # Detect the actual MIME type of the image
            detected_mime_type = detect_image_mime_type(image_bytes)

            graph = create_react_agent(
                model=ChatService().get_chat_model(model),
                tools=[],
                prompt="""
                    You are a helpful assistant that receive a plant photo and autofill the plant info.
                    Be concise and to the point.
                """,
                response_format=PlantAutofillResponseFormat,
            )

            config = RunnableConfig(
                metadata={
                    "model": model,
                },
                tags=[
                    self.__class__.__name__,
                ],
                run_name=f"Autofill plant info",
            )

            multimodal_content = [
                {
                    "type": "text",
                    "text": """
                        Examine this plant photo and autofill the plant info. 
                        If it's not a plant, return empty string for the fields.
                     """,
                },
                ChatFileContent(
                    type="image",
                    source_type="base64",
                    data=base64.b64encode(image_bytes).decode("utf-8"),
                    mime_type=detected_mime_type,
                ).model_dump(),
            ]
            current_message = HumanMessage(content=multimodal_content)
            response = graph.invoke({"messages": [current_message]}, config)

            logging.getLogger("uvicorn.info").info(
                f"Autofill plant info response: {response}"
            )

            autofill_data = response.get(
                "structured_response",
                PlantAutofillResponseFormat(
                    name="",
                    species=PlantSpecies.OTHER,
                    species_details="",
                    description="",
                    location="",
                    current_health_status=PlantHealthStatus.UNKNOWN,
                    watering_frequency_days=0,
                    fertilizing_frequency_days=0,
                    light_requirements=LightRequirement.LOW,
                    humidity_preference=HumidityPreference.MEDIUM,
                    temperature_range="",
                ),
            )

            return AutofillPlantInfoResponse(
                success=True,
                plant_info=PlantInfo(
                    name=autofill_data.name,
                    species=autofill_data.species,
                    species_details=autofill_data.species_details,
                    description=autofill_data.description,
                    location=autofill_data.location,
                    acquisition_date=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    current_health_status=autofill_data.current_health_status,
                    watering_frequency_days=autofill_data.watering_frequency_days,
                    fertilizing_frequency_days=autofill_data.fertilizing_frequency_days,
                    light_requirements=autofill_data.light_requirements,
                    humidity_preference=autofill_data.humidity_preference,
                    temperature_range=autofill_data.temperature_range,
                ),
                message="Autofill plant info completed",
            )

        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Error autofill plant info: {e}")
            return AutofillPlantInfoResponse(
                success=False,
                plant_info=None,
                message=f"Failed to autofill plant info: {str(e)}",
            )
