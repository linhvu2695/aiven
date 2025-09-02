import {
    VStack,
    HStack,
    Box,
    Text,
    Heading,
    Button,
    Input,
    Textarea,
    Badge,
    Image,
    Card,
    SimpleGrid,
    IconButton,
} from "@chakra-ui/react";
import {
    FaEdit,
    FaSave,
    FaTimes,
    FaWater,
    FaSun,
    FaThermometerHalf,
    FaMapMarkerAlt,
    FaCalendarAlt,
    FaSeedling,
    FaLeaf
} from "react-icons/fa";
import { useState } from "react";
import { LightRequirement, type PlantInfo, type PlantInfoWithImage, PlantSpecies, HumidityPreference, type CreateOrUpdatePlantRequest } from "@/types/plant";
import { Dropdown } from "@/components/ui/dropdown";
import { toaster } from "@/components/ui/toaster";
import { BASE_URL } from "@/App";
import { getHealthStatusColor, formatSpeciesLabel, getSpeciesIcon } from "@/utils/plant-utils.tsx";

interface PlantDetailInfoProps {
    plant: PlantInfoWithImage;
    onPlantUpdate?: (updatedPlant: PlantInfo) => void;
    onClose?: () => void;
}

// Dropdown options
const speciesOptions = Object.values(PlantSpecies).map(species => ({
    value: species,
    label: formatSpeciesLabel(species)
}));

const lightRequirementOptions = Object.values(LightRequirement).map(light => ({
    value: light,
    label: formatSpeciesLabel(light)
}));

const humidityPreferenceOptions = Object.values(HumidityPreference).map(humidity => ({
    value: humidity,
    label: formatSpeciesLabel(humidity)
}));



export const PlantDetailInfo = ({ plant, onPlantUpdate }: PlantDetailInfoProps) => {
    const [isEditing, setIsEditing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [editedPlant, setEditedPlant] = useState<CreateOrUpdatePlantRequest>({
        id: plant.id,
        name: plant.name || undefined,
        species: plant.species || undefined,
        species_details: plant.species_details || undefined,
        description: plant.description || undefined,
        location: plant.location || undefined,
        acquisition_date: plant.acquisition_date || undefined,
        watering_frequency_days: plant.watering_frequency_days || undefined,
        light_requirements: plant.light_requirements || undefined,
        humidity_preference: plant.humidity_preference || undefined,
        temperature_range: plant.temperature_range || undefined,
        last_watered: plant.last_watered ? plant.last_watered.split('T')[0] : undefined,
        last_fertilized: plant.last_fertilized ? plant.last_fertilized.split('T')[0] : undefined,
    });

    const handleEdit = () => {
        setIsEditing(true);
    };

    const handleCancel = () => {
        setIsEditing(false);
        // Reset to original values
        setEditedPlant({
            id: plant.id,
            name: plant.name || undefined,
            species: plant.species || undefined,
            species_details: plant.species_details || undefined,
            description: plant.description || undefined,
            location: plant.location || undefined,
            acquisition_date: plant.acquisition_date || undefined,
            watering_frequency_days: plant.watering_frequency_days || undefined,
            light_requirements: plant.light_requirements || undefined,
            humidity_preference: plant.humidity_preference || undefined,
            temperature_range: plant.temperature_range || undefined,
            last_watered: plant.last_watered ? plant.last_watered.split('T')[0] : undefined,
            last_fertilized: plant.last_fertilized ? plant.last_fertilized.split('T')[0] : undefined,
        });
    };

    const handleSave = async () => {
        try {
            setIsSaving(true);

            // Validate that we have a plant ID for updates
            if (!plant.id) {
                toaster.create({
                    description: "Cannot update plant: missing plant ID",
                    type: "error",
                });
                return;
            }

            const response = await fetch(`${BASE_URL}/api/plant/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(editedPlant),
            });

            if (!response.ok) {
                toaster.create({
                    description: `Failed to update plant: ${response.status} ${response.statusText}`,
                    type: "error",
                });
                return;
            }

            const result = await response.json();
            
            if (result.success) {
                // Fetch the updated plant data
                const updatedResponse = await fetch(`${BASE_URL}/api/plant/${plant.id}`);
                if (updatedResponse.ok) {
                    const updatedPlantData = await updatedResponse.json();
                    onPlantUpdate?.(updatedPlantData.plant);
                }
                
                setIsEditing(false);
                toaster.create({
                    description: "Plant updated successfully!",
                    type: "success",
                });
            } else {
                toaster.create({
                    description: "Failed to update plant",
                    type: "error",
                });
            }
        } catch (error) {
            toaster.create({
                description: "Failed to update plant",
                type: "error",
            });
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <VStack gap={6} align="stretch" h="100%" overflow="auto" paddingRight={8} paddingBottom={8}>
            {/* Header with Plant Image and Basic Info */}
            <Card.Root>
                <Card.Body>
                    <VStack gap={4} align="stretch">
                        {/* Plant Image */}
                        {plant.rep_image_url ? (
                            <Box alignSelf="center">
                                <Image
                                    src={plant.rep_image_url}
                                    alt={plant.name}
                                    h="auto"
                                    w="100%"
                                    maxH="400px"
                                    objectFit="cover"
                                    borderRadius="lg"
                                />
                            </Box>
                        ) : (
                            <Box alignSelf="center">
                                <Box
                                    h="200px"
                                    w="300px"
                                    bg="gray.100"
                                    borderRadius="lg"
                                    display="flex"
                                    alignItems="center"
                                    justifyContent="center"
                                >
                                    <FaSeedling size={48} color="gray.400" />
                                </Box>
                            </Box>
                        )}

                        {/* Plant Name and Species */}
                        <VStack align="stretch" gap={2}>
                            {isEditing ? (
                                <Input
                                    value={editedPlant.name || ""}
                                    onChange={(e) => setEditedPlant({ ...editedPlant, name: e.target.value })}
                                    placeholder="Plant name"
                                    fontSize="lg"
                                    fontWeight="bold"
                                />
                            ) : (
                                <Heading size="lg">{plant.name}</Heading>
                            )}

                            <HStack justify="space-between" align="center">
                                {isEditing ? (
                                    <Dropdown
                                        value={editedPlant.species || ""}
                                        onValueChange={(value) => setEditedPlant({ ...editedPlant, species: value as PlantSpecies })}
                                        options={speciesOptions}
                                        placeholder="Select species"
                                    />
                                ) : (
                                    <HStack gap={2}>
                                        {getSpeciesIcon(plant.species)}
                                        <Text fontWeight="medium">{formatSpeciesLabel(plant.species)}</Text>
                                    </HStack>
                                )}

                                <Badge color={getHealthStatusColor(plant.current_health_status)} size="md">
                                    {formatSpeciesLabel(plant.current_health_status)}
                                </Badge>
                            </HStack>
                        </VStack>
                    </VStack>
                </Card.Body>
            </Card.Root>

            {/* Plant Details */}
            <Card.Root>
                <Card.Body>
                    <VStack gap={4} align="stretch">
                        <HStack justify="space-between" align="center">
                            <Heading size="md">Details</Heading>
                            {!isEditing && (
                                <IconButton
                                    size="sm"
                                    variant="outline"
                                    colorScheme="teal"
                                    aria-label="Edit plant"
                                    onClick={handleEdit}
                                    _hover={{
                                        bg: "teal.600",
                                        transform: "scale(1.1)",
                                    }}
                                >
                                    <FaEdit />
                                </IconButton>
                            )}
                        </HStack>

                        <SimpleGrid columns={1} gap={4}>
                            {/* Species Details */}
                            <VStack align="stretch" gap={2}>
                                <Text fontSize="sm" fontWeight="medium" color="fg.muted">
                                    Species Details
                                </Text>
                                {isEditing ? (
                                    <Input
                                        value={editedPlant.species_details || ""}
                                        onChange={(e) => setEditedPlant({ ...editedPlant, species_details: e.target.value })}
                                        placeholder="e.g., Monstera Deliciosa"
                                    />
                                ) : (
                                    <Text>{plant.species_details || "Not specified"}</Text>
                                )}
                            </VStack>

                            {/* Description */}
                            <VStack align="stretch" gap={2}>
                                <Text fontSize="sm" fontWeight="medium" color="fg.muted">
                                    Description
                                </Text>
                                {isEditing ? (
                                    <Textarea
                                        value={editedPlant.description || ""}
                                        onChange={(e) => setEditedPlant({ ...editedPlant, description: e.target.value })}
                                        placeholder="Tell us about your plant..."
                                        rows={3}
                                    />
                                ) : (
                                    <Text>{plant.description || "No description provided"}</Text>
                                )}
                            </VStack>

                            {/* Location */}
                            <VStack align="stretch" gap={2}>
                                <Text fontSize="sm" fontWeight="medium" color="fg.muted">
                                    <HStack gap={2}>
                                        <FaMapMarkerAlt />
                                        <Text>Location</Text>
                                    </HStack>
                                </Text>
                                {isEditing ? (
                                    <Input
                                        value={editedPlant.location || ""}
                                        onChange={(e) => setEditedPlant({ ...editedPlant, location: e.target.value })}
                                        placeholder="e.g., Living room window"
                                    />
                                ) : (
                                    <Text>{plant.location || "Not specified"}</Text>
                                )}
                            </VStack>
                        </SimpleGrid>
                    </VStack>
                </Card.Body>
            </Card.Root>

            {/* Care Information */}
            <Card.Root>
                <Card.Body>
                    <VStack gap={4} align="stretch">
                        <Heading size="md">Care</Heading>

                        <SimpleGrid columns={{ base: 1, md: 2 }} gap={4}>
                            {/* Watering Frequency */}
                            <VStack align="stretch" gap={2}>
                                <Text fontSize="sm" fontWeight="medium" color="blue.400">
                                    <HStack gap={2}>
                                        <FaWater color="blue.500" />
                                        <Text>Watering Frequency (days)</Text>
                                    </HStack>
                                </Text>
                                {isEditing ? (
                                    <Input
                                        type="number"
                                        value={editedPlant.watering_frequency_days || ""}
                                        onChange={(e) => setEditedPlant({ ...editedPlant, watering_frequency_days: parseInt(e.target.value) || undefined })}
                                        placeholder="7"
                                    />
                                ) : (
                                    <Text>{plant.watering_frequency_days ? `Every ${plant.watering_frequency_days} days` : "Not specified"}</Text>
                                )}
                            </VStack>

                            {/* Light Requirements */}
                            <VStack align="stretch" gap={2}>
                                <Text fontSize="sm" fontWeight="medium" color="yellow.400">
                                    <HStack gap={2}>
                                        <FaSun color="yellow.500" />
                                        <Text>Light Requirements</Text>
                                    </HStack>
                                </Text>
                                {isEditing ? (
                                    <Dropdown
                                        value={editedPlant.light_requirements || ""}
                                        onValueChange={(value) => setEditedPlant({ ...editedPlant, light_requirements: value as LightRequirement })}
                                        options={lightRequirementOptions}
                                        placeholder="Select light requirement"
                                    />
                                ) : (
                                    <Text>{plant.light_requirements ? formatSpeciesLabel(plant.light_requirements) : "Not specified"}</Text>
                                )}
                            </VStack>

                            {/* Humidity Preference */}
                            <VStack align="stretch" gap={2}>
                                <Text fontSize="sm" fontWeight="medium" color="green.400">
                                    Humidity Preference
                                </Text>
                                {isEditing ? (
                                    <Dropdown
                                        value={editedPlant.humidity_preference || ""}
                                        onValueChange={(value) => setEditedPlant({ ...editedPlant, humidity_preference: value as HumidityPreference })}
                                        options={humidityPreferenceOptions}
                                        placeholder="Select humidity preference"
                                    />
                                ) : (
                                    <Text>{plant.humidity_preference ? formatSpeciesLabel(plant.humidity_preference) : "Not specified"}</Text>
                                )}
                            </VStack>

                            {/* Temperature Range */}
                            <VStack align="stretch" gap={2}>
                                <Text fontSize="sm" fontWeight="medium" color="red.400">
                                    <HStack gap={2}>
                                        <FaThermometerHalf />
                                        <Text>Temperature Range</Text>
                                    </HStack>
                                </Text>
                                {isEditing ? (
                                    <Input
                                        value={editedPlant.temperature_range || ""}
                                        onChange={(e) => setEditedPlant({ ...editedPlant, temperature_range: e.target.value })}
                                        placeholder="e.g., 65-75°F"
                                    />
                                ) : (
                                    <Text>{plant.temperature_range || "Not specified"}</Text>
                                )}
                            </VStack>

                            {/* Last Watered */}
                            <VStack align="stretch" gap={2}>
                                <Text fontSize="sm" fontWeight="medium" color="fg.muted">
                                    <HStack gap={2}>
                                        <FaCalendarAlt color="blue.400" />
                                        <Text>Last Watered</Text>
                                    </HStack>
                                </Text>
                                {isEditing ? (
                                    <Input
                                        type="date"
                                        value={editedPlant.last_watered || ""}
                                        onChange={(e) => setEditedPlant({ ...editedPlant, last_watered: e.target.value })}
                                    />
                                ) : (
                                    <Text>{plant.last_watered ? new Date(plant.last_watered).toLocaleDateString() : "Not recorded"}</Text>
                                )}
                            </VStack>

                            {/* Last Fertilized */}
                            <VStack align="stretch" gap={2}>
                                <Text fontSize="sm" fontWeight="medium" color="fg.muted">
                                    <HStack gap={2}>
                                        <FaLeaf color="green.500" />
                                        <Text>Last Fertilized</Text>
                                    </HStack>
                                </Text>
                                {isEditing ? (
                                    <Input
                                        type="date"
                                        value={editedPlant.last_fertilized || ""}
                                        onChange={(e) => setEditedPlant({ ...editedPlant, last_fertilized: e.target.value })}
                                    />
                                ) : (
                                    <Text>{plant.last_fertilized ? new Date(plant.last_fertilized).toLocaleDateString() : "Not recorded"}</Text>
                                )}
                            </VStack>
                        </SimpleGrid>
                    </VStack>
                </Card.Body>
            </Card.Root>

            {/* AI Care Tips */}
            {plant.ai_care_tips.length > 0 && (
                <Card.Root>
                    <Card.Body>
                        <VStack gap={4} align="stretch">
                            <Heading size="md" color="purple.500">AI Care Tips</Heading>
                            <VStack gap={2} align="stretch">
                                {plant.ai_care_tips.map((tip, index) => (
                                    <Text key={index} fontSize="sm" pl={4} borderLeft="3px solid" borderColor="purple.200">
                                        {tip}
                                    </Text>
                                ))}
                            </VStack>
                        </VStack>
                    </Card.Body>
                </Card.Root>
            )}

            {/* Action Buttons */}
            {isEditing && (
                <HStack justify="end" gap={3} pt={4} borderTop="1px solid" borderColor="border.default">
                    <Button
                        variant="outline"
                        onClick={handleCancel}
                    >
                        <FaTimes />
                        Cancel
                    </Button>
                    <Button
                        colorScheme="teal"
                        onClick={handleSave}
                        loading={isSaving}
                        _hover={{
                            bg: "teal.600",
                            transform: "scale(1.1)",
                        }}
                    >
                        <FaSave />
                        Save Changes
                    </Button>
                </HStack>
            )}
        </VStack>
    );
};

export default PlantDetailInfo;
