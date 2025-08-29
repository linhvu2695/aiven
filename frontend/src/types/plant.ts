export enum PlantSpecies {
    SUCCULENT = "succulent",
    TROPICAL = "tropical",
    FLOWERING = "flowering",
    HERB = "herb",
    FERN = "fern",
    TREE = "tree",
    VEGETABLE = "vegetable",
    FRUIT = "fruit",
    CACTUS = "cactus",
    ORCHID = "orchid",
    OTHER = "other"
}

export enum PlantHealthStatus {
    EXCELLENT = "excellent",
    GOOD = "good",
    FAIR = "fair",
    POOR = "poor",
    CRITICAL = "critical",
    UNKNOWN = "unknown"
}

export enum LightRequirement {
    LOW = "low",
    MEDIUM = "medium",
    HIGH = "high",
    BRIGHT_INDIRECT = "bright_indirect"
}

export enum HumidityPreference {
    LOW = "low",
    MEDIUM = "medium",
    HIGH = "high"
}

export interface PlantInfo {
    id: string;
    name: string;
    species: PlantSpecies;
    species_details?: string;
    description?: string;
    location?: string;
    acquisition_date: string;
    created_at: string;
    updated_at: string;
    
    // Current status
    current_health_status: PlantHealthStatus;
    last_watered?: string;
    last_fertilized?: string;
    last_photo_date?: string;
    
    // Care preferences
    watering_frequency_days?: number;
    fertilizing_frequency_days?: number;
    light_requirements?: LightRequirement;
    humidity_preference?: HumidityPreference;
    temperature_range?: string;
    
    // Photos and care
    photos: string[];
    ai_care_tips: string[];
}

export interface PlantListResponse {
    plants: PlantInfo[];
}

export interface PlantResponse {
    success: boolean;
    plant?: PlantInfo;
    message: string;
}

export interface CreateOrUpdatePlantRequest {
    id?: string;
    name?: string;
    species?: PlantSpecies;
    species_details?: string;
    description?: string;
    location?: string;
    acquisition_date?: string;
    watering_frequency_days?: number;
    light_requirements?: LightRequirement;
    humidity_preference?: HumidityPreference;
    temperature_range?: string;
    last_watered?: string;
    last_fertilized?: string;
}

export interface CreateOrUpdatePlantResponse {
    success: boolean;
    id: string;
    message: string;
}
