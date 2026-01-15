import { 
    Box, 
    Heading, 
    Text, 
    Card,
    VStack,
    Button,
    SimpleGrid,
    Spinner,
    Alert
} from "@chakra-ui/react";
import { FaPlus, FaSeedling, FaExclamationTriangle } from "react-icons/fa";
import { useState, useEffect } from "react";
import type { PlantInfo, PlantInfoWithImage } from "@/types/plant";
import type { ImageUrlsResponse } from "@/types/image";
import { PlantCard } from "./plant-card";
import { PlantDetailDialog } from "./plant-detail-dialog";
import { toaster } from "@/components/ui/toaster";
import { BASE_URL } from "@/App";

interface PlantCollectionProps {
    onAddPlant?: () => void;
    refreshTrigger?: number; // Prop to trigger refresh when plants are added
    onPlantsLoaded?: (plants: PlantInfoWithImage[]) => void; // Callback to share plant data
}

export const PlantCollection = ({ onAddPlant, refreshTrigger, onPlantsLoaded }: PlantCollectionProps) => {
    const [plants, setPlants] = useState<PlantInfoWithImage[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedPlant, setSelectedPlant] = useState<PlantInfoWithImage | null>(null);
    const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false);

    const populatePlantImages = async (plantsData: PlantInfo[]): Promise<PlantInfoWithImage[]> => {
        try {
            // Extract last photo ID from each plant that has photos
            const imageRequests: { plantId: string; imageId: string }[] = [];
            
            plantsData.forEach(plant => {
                if (plant.photos && plant.photos.length > 0) {
                    // Get the last photo (representative image)
                    const lastPhotoId = plant.photos[plant.photos.length - 1];
                    imageRequests.push({ plantId: plant.id, imageId: lastPhotoId });
                }
            });

            if (imageRequests.length === 0) {
                // No images to fetch, return plants as-is
                return plantsData.map(plant => ({ ...plant }));
            }

            // Batch fetch presigned URLs
            const imageIds = imageRequests.map(req => req.imageId);
            const idsParam = imageIds.join(',');
            var response = await fetch(`${BASE_URL}/api/image/serve/ids/${encodeURIComponent(idsParam)}`);

            if (!response.ok) {
                console.warn('Failed to fetch image URLs, proceeding without images');
                return plantsData.map(plant => ({ ...plant }));
            }

            const imageUrlsResponse: ImageUrlsResponse = await response.json();

            // Create a map of image ID to URL for quick lookup
            const imageUrlMap = new Map<string, string>();
            imageUrlsResponse.results.forEach(result => {
                if (result.success && result.url) {
                    imageUrlMap.set(result.image_id, result.url);
                }
            });

            // Map URLs back to plants
            return plantsData.map(plant => {
                const plantWithImage: PlantInfoWithImage = { ...plant };
                
                if (plant.photos && plant.photos.length > 0) {
                    const lastPhotoId = plant.photos[plant.photos.length - 1];
                    const imageUrl = imageUrlMap.get(lastPhotoId);
                    if (imageUrl) {
                        plantWithImage.rep_image_url = imageUrl;
                    }
                }
                
                return plantWithImage;
            });

        } catch (error) {
            console.warn('Error fetching representative images:', error);
            // Return plants without images on error
            return plantsData.map(plant => ({ ...plant }));
        }
    };

    const fetchPlants = async () => {
        try {
            setIsLoading(true);
            setError(null);
            
            const response = await fetch(`${BASE_URL}/api/plant/`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch plants: ${response.statusText}`);
            }
            
            const plantData = await response.json();
            const plantsWithImages = await populatePlantImages(plantData.plants);
            setPlants(plantsWithImages);
            onPlantsLoaded?.(plantsWithImages);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : "Failed to fetch plants";
            setError(errorMessage);
            toaster.create({
                description: errorMessage,
                type: "error",
            });
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchPlants();
    }, [refreshTrigger]); // Re-fetch when refreshTrigger changes

    const handleViewDetails = (plant: PlantInfoWithImage) => {
        setSelectedPlant(plant);
        setIsDetailDialogOpen(true);
    };

    const handleCloseDetailDialog = () => {
        setIsDetailDialogOpen(false);
        setSelectedPlant(null);
    };

    const handlePlantUpdate = (updatedPlant: PlantInfo) => {
        // Update the plant in the local state
        setPlants(prevPlants => 
            prevPlants.map(plant => 
                plant.id === updatedPlant.id 
                    ? { ...plant, ...updatedPlant }
                    : plant
            )
        );
        // Update the selected plant if it's the one being viewed
        if (selectedPlant?.id === updatedPlant.id) {
            setSelectedPlant(updatedPlant);
        }
    };

    if (isLoading) {
        return (
            <Box flex={1}>
                <Heading size="md" mb={4}>Your Plants</Heading>
                <Card.Root h="400px">
                    <Card.Body>
                        <VStack justify="center" h="100%" gap={4}>
                            <Spinner size="xl" color="primary.500" />
                            <Text color="fg.muted">Loading your plants...</Text>
                        </VStack>
                    </Card.Body>
                </Card.Root>
            </Box>
        );
    }

    if (error) {
        return (
            <Box flex={1}>
                <Heading size="md" mb={4}>Your Plants</Heading>
                <Alert.Root status="error">
                    <FaExclamationTriangle />
                    <VStack align="start" gap={2}>
                        <Alert.Title>Error loading plants</Alert.Title>
                        <Alert.Description>{error}</Alert.Description>
                        <Button 
                            size="sm" 
                            onClick={fetchPlants}
                            colorScheme="red"
                            variant="outline"
                        >
                            Try Again
                        </Button>
                    </VStack>
                </Alert.Root>
            </Box>
        );
    }

    if (plants.length === 0) {
        return (
            <Box flex={1}>
                <Heading size="md" mb={4}>Your Plants</Heading>
                
                {/* Empty State */}
                <Card.Root h="400px">
                    <Card.Body>
                        <VStack 
                            justify="center" 
                            h="100%" 
                            gap={4}
                            color="fg.muted"
                        >
                            <FaSeedling size={48} />
                            <VStack gap={2}>
                                <Text fontSize="lg" fontWeight="semibold">
                                    No plants yet
                                </Text>
                                <Text textAlign="center">
                                    Start building your plant collection by adding your first plant
                                </Text>
                            </VStack>
                            <Button 
                                colorScheme="green" 
                                size="sm" 
                                onClick={onAddPlant}
                                _hover={{
                                    transform: "scale(1.1)",
                                    bgColor: "primary.500",
                                }}
                            >
                                <FaPlus /> Add Your First Plant
                            </Button>
                        </VStack>
                    </Card.Body>
                </Card.Root>
            </Box>
        );
    }

    return (
        <Box flex={1}>
            <Heading size="md" mb={4}>
                Your Plants ({plants.length})
            </Heading>
            
            {/* Plant Grid */}
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} gap={6}>
                {plants.map((plant) => (
                    <PlantCard 
                        key={plant.id}
                        plant={plant}
                        onViewDetails={handleViewDetails}
                    />
                ))}
            </SimpleGrid>

            {/* Plant Detail Dialog */}
            <PlantDetailDialog
                plant={selectedPlant}
                isOpen={isDetailDialogOpen}
                onClose={handleCloseDetailDialog}
                onPlantUpdate={handlePlantUpdate}
            />
        </Box>
    );
};

export default PlantCollection;
