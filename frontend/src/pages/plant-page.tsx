import { 
    Box, 
    Flex, 
    VStack
} from "@chakra-ui/react";
import { 
    PlantHeader, 
    PlantCategories, 
    PlantStats, 
    PlantCollection 
} from "@/components/plant";

export const PlantPage = () => {
    return (
        <Box h="100vh" overflow="hidden">
            {/* Top Bar */}
            <PlantHeader />

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
                        <PlantCollection />
                    </VStack>
                </Box>
            </Flex>
        </Box>
    );
};

export default PlantPage;
