import { 
    Box, 
    Card, 
    Text, 
    Image, 
    VStack, 
    HStack, 
    Badge, 
    Heading
} from "@chakra-ui/react";
import { 
    FaWater, 
    FaSun, 
    FaMapMarkerAlt, 
    FaCalendarAlt, 
} from "react-icons/fa";
import type { PlantInfoWithImage } from "@/types/plant";
import { getHealthStatusColor, formatSpeciesLabel, getSpeciesIcon } from "@/utils/plant-utils.tsx";

interface PlantCardProps {
    plant: PlantInfoWithImage;
    onViewDetails?: (plant: PlantInfoWithImage) => void;
}

export const PlantCard = ({ plant, onViewDetails }: PlantCardProps) => {
    const healthColor = getHealthStatusColor(plant.current_health_status);
    const speciesIcon = getSpeciesIcon(plant.species);
    
    // Get the first photo if available, otherwise use placeholder
    const plantImage = plant.rep_image_url || "";

    return (
        <Card.Root
            maxW="350px"
            cursor="pointer"
            onClick={() => onViewDetails?.(plant)}
            _hover={{
                transform: "translateY(-4px)",
                shadow: "xl",
                borderColor: "primary.300"
            }}
            transition="all 0.2s"
            border="1px solid"
            borderColor="border.default"
        >
            <Card.Body p={0}>
                {/* Plant Image */}
                <Box position="relative">
                    <Image
                        src={plantImage}
                        alt={plant.name}
                        h="200px"
                        w="100%"
                        objectFit="cover"
                        borderTopRadius="lg"
                    />
                    
                    {/* Health Status Badge */}
                    <Badge
                        position="absolute"
                        top={3}
                        right={3}
                        color={healthColor}
                        size="sm"
                        fontWeight="bold"
                    >
                        {formatSpeciesLabel(plant.current_health_status)}
                    </Badge>
                </Box>

                {/* Plant Info */}
                <VStack p={4} align="stretch" gap={3}>
                    {/* Name and Species */}
                    <VStack align="stretch" gap={1}>
                        <Heading size="md" color="fg.default" lineClamp={1}>
                            {plant.name}
                        </Heading>
                        <HStack>
                            {speciesIcon}
                            <Text fontSize="sm" color="fg.muted">
                                {formatSpeciesLabel(plant.species)}
                                {plant.species_details && ` • ${plant.species_details}`}
                            </Text>
                        </HStack>
                    </VStack>

                    {/* Location */}
                    {plant.location && (
                        <HStack gap={2}>
                            <FaMapMarkerAlt size={12} />
                            <Text fontSize="sm" color="fg.muted" lineClamp={1}>
                                {plant.location}
                            </Text>
                        </HStack>
                    )}

                    {/* Care Info */}
                    <VStack gap={2} align="stretch">
                        {/* Last Watered */}
                        {plant.last_watered && (
                            <HStack justify="space-between">
                                <HStack gap={2}>
                                    <FaWater size={12} color="blue.500" />
                                    <Text fontSize="sm" color="fg.muted">
                                        Last watered:
                                    </Text>
                                </HStack>
                                <Text fontSize="sm" fontWeight="medium">
                                    {new Date(plant.last_watered).toLocaleDateString()}
                                </Text>
                            </HStack>
                        )}

                        {/* Light Requirements */}
                        {plant.light_requirements && (
                            <HStack>
                                <HStack gap={2}>
                                    <FaSun size={12} color="yellow.500" />
                                    <Text fontSize="sm" color="yellow.400">
                                        Light:
                                    </Text>
                                </HStack>
                                <Text fontSize="sm" fontWeight="medium">
                                    {formatSpeciesLabel(plant.light_requirements)}
                                </Text>
                            </HStack>
                        )}

                        {/* Watering Frequency */}
                        {plant.watering_frequency_days && (
                            <HStack>
                                <HStack gap={2}>
                                    <FaCalendarAlt size={12} color="blue.400" />
                                    <Text fontSize="sm" color="blue.400">
                                        Water every:
                                    </Text>
                                </HStack>
                                <Text fontSize="sm" fontWeight="medium">
                                    {plant.watering_frequency_days} days
                                </Text>
                            </HStack>
                        )}
                    </VStack>

                    {/* Description */}
                    {plant.description && (
                        <Text fontSize="sm" color="fg.muted" lineClamp={2}>
                            {plant.description}
                        </Text>
                    )}

                    {/* AI Care Tips Preview */}
                    {plant.ai_care_tips.length > 0 && (
                        <Box>
                            <Text fontSize="xs" fontWeight="bold" color="purple.500" mb={1}>
                                AI Tip:
                            </Text>
                            <Text fontSize="xs" color="fg.muted" lineClamp={2}>
                                {plant.ai_care_tips[0]}
                            </Text>
                        </Box>
                    )}
                </VStack>
            </Card.Body>
        </Card.Root>
    );
};

export default PlantCard;
