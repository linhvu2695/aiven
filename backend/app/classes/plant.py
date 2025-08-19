from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from app.classes.image import ImageInfo, ImageType

class PlantSpecies(str, Enum):
    """Common plant species categories"""
    SUCCULENT = "succulent"
    TROPICAL = "tropical"
    FLOWERING = "flowering"
    HERB = "herb"
    FERN = "fern"
    TREE = "tree"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    CACTUS = "cactus"
    ORCHID = "orchid"
    OTHER = "other"

class CareActionType(str, Enum):
    """Types of care actions that can be performed on plants"""
    WATER = "water"
    FERTILIZE = "fertilize"
    PRUNE = "prune"
    REPOT = "repot"
    MIST = "mist"
    ROTATE = "rotate"
    INSPECT = "inspect"
    HARVEST = "harvest"

class PlantHealthStatus(str, Enum):
    """Plant health status based on AI analysis"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class PlantPhotoInfo(ImageInfo):
    """Specialized image model for plant photos"""
    plant_id: str
    health_status: PlantHealthStatus = PlantHealthStatus.UNKNOWN
    
    def __init__(self, **data):
        super().__init__(**data)
        self.image_type = ImageType.PLANT_PHOTO
    
class CareAction(BaseModel):
    """Individual care action with AI recommendations"""
    id: str
    plant_id: str
    action_type: CareActionType
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    is_completed: bool = False
    ai_generated: bool = False  # Whether this was AI-recommended
    notes: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=5)  # 1=low, 5=urgent
    
class CareSchedule(BaseModel):
    """AI-generated care schedule for a plant"""
    id: str
    plant_id: str
    created_at: datetime
    updated_at: datetime
    actions: List[CareAction] = Field(default_factory=list)
    ai_recommendations: Optional[dict] = None  # AI insights and reasoning
    
class PlantInfo(BaseModel):
    """Main plant information model"""
    id: Optional[str] = None
    name: str
    species: PlantSpecies
    species_details: Optional[str] = None  # Specific variety/cultivar
    description: Optional[str] = None
    location: Optional[str] = None  # Where the plant is located (indoor/outdoor/room)
    acquisition_date: datetime
    created_at: datetime
    updated_at: datetime
    
    # Current status
    current_health_status: PlantHealthStatus = PlantHealthStatus.UNKNOWN
    last_watered: Optional[datetime] = None
    last_fertilized: Optional[datetime] = None
    last_photo_date: Optional[datetime] = None
    
    # Care preferences and AI insights
    watering_frequency_days: Optional[int] = None  # AI-suggested frequency
    fertilizing_frequency_days: Optional[int] = None
    light_requirements: Optional[str] = None  # "low", "medium", "high", "bright indirect"
    humidity_preference: Optional[str] = None  # "low", "medium", "high"
    temperature_range: Optional[str] = None  # e.g., "65-75°F"
    
    # Tracking data
    photos: List[PlantPhotoInfo] = Field(default_factory=list)
    care_schedule: Optional[CareSchedule] = None
    
    # AI-generated insights
    ai_care_tips: List[str] = Field(default_factory=list)
    growth_pattern: Optional[dict] = None  # AI analysis of growth over time
    health_trends: Optional[dict] = None  # Health trends from photo analysis
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CreateOrUpdatePlantRequest(BaseModel):
    """Request model for creating or updating a plant"""
    id: Optional[str] = None  # If None/empty, create new plant; if provided, update existing
    name: str
    species: PlantSpecies
    species_details: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    acquisition_date: Optional[datetime] = None
    
    # Care preferences
    watering_frequency_days: Optional[int] = None
    light_requirements: Optional[str] = None
    humidity_preference: Optional[str] = None
    temperature_range: Optional[str] = None
    
    # Status updates (mainly for updates)
    last_watered: Optional[datetime] = None
    last_fertilized: Optional[datetime] = None

class AddPlantPhotoRequest(BaseModel):
    """Request model for adding a photo to a plant"""
    filename: str
    image_data: Optional[str] = None  # Base64 encoded image
    file_data: Optional[bytes] = None  # Raw file bytes
    title: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    captured_at: Optional[datetime] = None

class CreateCareActionRequest(BaseModel):
    """Request model for creating a care action"""
    action_type: CareActionType
    scheduled_date: datetime
    notes: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=5)

class CreateOrUpdatePlantResponse(BaseModel):
    """Response model for create or update plant operations"""
    success: bool
    id: str
    message: str

class PlantResponse(BaseModel):
    """Response model for plant operations"""
    success: bool
    plant: Optional[PlantInfo] = None
    message: str

class PlantListResponse(BaseModel):
    """Response model for listing plants"""
    plants: List[PlantInfo]
    total: int

class PlantPhotoResponse(BaseModel):
    """Response model for photo operations"""
    success: bool
    photo: Optional[PlantPhotoInfo] = None
    ai_analysis: Optional[dict] = None
    message: str

class CareScheduleResponse(BaseModel):
    """Response model for care schedule operations"""
    success: bool
    schedule: Optional[CareSchedule] = None
    upcoming_actions: List[CareAction] = Field(default_factory=list)
    message: str

class PlantHealthAnalysisResponse(BaseModel):
    """Response model for AI health analysis"""
    success: bool
    health_status: PlantHealthStatus
    analysis: Optional[dict] = None
    recommendations: List[str] = Field(default_factory=list)
    care_adjustments: Optional[dict] = None  # Suggested changes to care schedule
    message: str
