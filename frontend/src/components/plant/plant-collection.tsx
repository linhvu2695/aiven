import { 
    Box, 
    Heading, 
    Text, 
    Card,
    VStack,
    Button,
    useDisclosure
} from "@chakra-ui/react";
import { FaPlus, FaSeedling } from "react-icons/fa";
import { AddPlantDialog } from "./add-plant-dialog";
import { toaster } from "../ui/toaster";

export const PlantCollection = () => {
    const { open, onOpen, onClose } = useDisclosure();
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
                            onClick={onOpen}
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
            
            <AddPlantDialog 
                isOpen={open} 
                onClose={onClose}
                onPlantAdded={() => {
                    // TODO: Refresh plant list when implemented
                    
                    toaster.create({
                        description: "Plant added successfully",
                        type: "success",
                    });
                }}
            />
        </Box>
    );
};

export default PlantCollection;
