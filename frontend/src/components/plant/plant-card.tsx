import { 
    Box, 
    Card, 
    Text, 
    Image, 
    VStack, 
    HStack, 
    Badge, 
    IconButton,
    Heading
} from "@chakra-ui/react";
import { 
    FaWater, 
    FaLeaf, 
    FaSun, 
    FaMapMarkerAlt, 
    FaCalendarAlt, 
    FaEdit,
    FaSeedling,
    FaTree,
    FaCarrot,
    FaAppleAlt
} from "react-icons/fa";
import { 
    GiCactus,
    GiFlowerPot,
    GiFern,
    GiGrass,
    GiFlowers,
} from "react-icons/gi";
import type { PlantInfoWithImage } from "@/types/plant";
import { PlantHealthStatus, PlantSpecies, LightRequirement } from "@/types/plant";
import { Tooltip } from "@/components/ui/tooltip";
import { IoFlower } from "react-icons/io5";

interface PlantCardProps {
    plant: PlantInfoWithImage;
    onEdit?: (plant: PlantInfoWithImage) => void;
    onViewDetails?: (plant: PlantInfoWithImage) => void;
}

const getHealthStatusColor = (status: PlantHealthStatus): string => {
    switch (status) {
        case PlantHealthStatus.EXCELLENT:
            return "green";
        case PlantHealthStatus.GOOD:
            return "teal";
        case PlantHealthStatus.FAIR:
            return "yellow";
        case PlantHealthStatus.POOR:
            return "orange";
        case PlantHealthStatus.CRITICAL:
            return "red";
        default:
            return "gray";
    }
};

const getSpeciesIcon = (species: PlantSpecies) => {
    switch (species) {
        case PlantSpecies.CACTUS:
            return <GiCactus color="green.600" size={16} />;
        case PlantSpecies.SUCCULENT:
            return <GiFlowerPot color="teal.500" size={16} />;
        case PlantSpecies.FLOWERING:
            return <IoFlower color="pink.500" size={16} />;
        case PlantSpecies.TROPICAL:
            return <FaLeaf color="emerald.500" size={16} />;
        case PlantSpecies.HERB:
            return <GiGrass color="green.500" size={16} />;
        case PlantSpecies.FERN:
            return <GiFern color="green.400" size={16} />;
        case PlantSpecies.TREE:
            return <FaTree color="brown.500" size={16} />;
        case PlantSpecies.VEGETABLE:
            return <FaCarrot color="orange.500" size={16} />;
        case PlantSpecies.FRUIT:
            return <FaAppleAlt color="red.500" size={16} />;
        case PlantSpecies.ORCHID:
            return <GiFlowers color="purple.500" size={16} />;
        case PlantSpecies.OTHER:
        default:
            return <FaSeedling color="green.500" size={16} />;
    }
};

const formatSpeciesLabel = (species: PlantSpecies | PlantHealthStatus | LightRequirement): string => {
    return species.charAt(0).toUpperCase() + species.slice(1).replace('_', ' ');
};

export const PlantCard = ({ plant, onEdit, onViewDetails }: PlantCardProps) => {
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
                borderColor: "teal.300"
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

                    {/* Edit Button */}
                    {onEdit && (
                        <Tooltip content="Edit plant">
                            <IconButton
                                position="absolute"
                                top={3}
                                left={3}
                                size="sm"
                                variant="solid"
                                colorScheme="teal"
                                aria-label="Edit plant"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onEdit(plant);
                                }}
                                _hover={{
                                    transform: "scale(1.1)",
                                    bg: "teal.500"
                                }}
                            >
                                <FaEdit />
                            </IconButton>
                        </Tooltip>
                    )}
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
                                    <Text fontSize="sm" color="fg.muted">
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
                            <HStack justify="space-between">
                                <HStack gap={2}>
                                    <FaCalendarAlt size={12} color="teal.500" />
                                    <Text fontSize="sm" color="fg.muted">
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
