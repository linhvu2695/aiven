import { 
    Box, 
    Flex, 
    VStack,
    useDisclosure
} from "@chakra-ui/react";
import { useState } from "react";
import { 
    PlantHeader, 
    PlantCategories, 
    PlantStats, 
    PlantCollection,
    AddPlantDialog
} from "@/components/plant";
import { toaster } from "@/components/ui/toaster";

export const PlantPage = () => {
    const { open, onOpen, onClose } = useDisclosure();
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const handlePlantAdded = () => {
        // Trigger refresh of plant list
        setRefreshTrigger(prev => prev + 1);
        toaster.create({
            description: "Plant added successfully",
            type: "success",
        });
    };

    return (
        <Box h="100vh" overflow="hidden">
            {/* Top Bar */}
            <PlantHeader onAddPlant={onOpen} />

            {/* Main Content */}
            <Flex h="calc(100vh - 120px)" p={4} gap={4}>
                {/* Left Sidebar - Plant Categories */}
                <PlantCategories />

                {/* Main Content Area - Plant Grid */}
                <Box flex={1} h="100%" overflow="auto">
                    <VStack align="stretch" gap={4} h="100%">
                        {/* Stats Overview */}
                        <PlantStats />

                        {/* Plant Collection */}
                        <PlantCollection 
                            onAddPlant={onOpen}
                            refreshTrigger={refreshTrigger}
                        />
                    </VStack>
                </Box>
            </Flex>

            <AddPlantDialog 
                isOpen={open} 
                onClose={onClose}
                onPlantAdded={handlePlantAdded}
            />
        </Box>
    );
};

export default PlantPage;
