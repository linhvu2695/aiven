import { 
    Box, 
    Heading, 
    Text, 
    Card,
    VStack,
    Button
} from "@chakra-ui/react";
import { FaPlus, FaSeedling } from "react-icons/fa";

interface PlantCollectionProps {
    onAddPlant?: () => void;
}

export const PlantCollection = ({ onAddPlant }: PlantCollectionProps) => {
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
                                bgColor: "teal.500",
                            }}
                        >
                            <FaPlus /> Add Your First Plant
                        </Button>
                    </VStack>
                </Card.Body>
            </Card.Root>
        </Box>
    );
};

export default PlantCollection;
