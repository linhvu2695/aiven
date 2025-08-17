import { 
    Box, 
    Heading, 
    Text, 
    HStack,
    VStack,
    IconButton,
    Input
} from "@chakra-ui/react";
import { FaPlus, FaSeedling } from "react-icons/fa";
import { Tooltip } from "@/components/ui/tooltip";

export const PlantHeader = () => {
    return (
        <HStack p={4} borderBottom="1px" borderColor="border.default">
            <VStack align="start" gap={0}>
                <Heading size="lg" color="fg.default">
                    <HStack>
                        <FaSeedling color="green.500" />
                        <Text>Plant Management</Text>
                    </HStack>
                </Heading>
                <Text fontSize="sm" color="fg.muted">
                    Manage your plant collection and care schedule
                </Text>
            </VStack>

            <Box flex={1} />

            {/* Action Bar */}
            <HStack gap={2}>
                <Input
                    placeholder="Search plants..."
                    maxW="300px"
                    size="sm"
                />
                <Tooltip content="Add new plant">
                    <IconButton
                        aria-label="Add new plant"
                        size="sm"
                        colorScheme="green"
                    >
                        <FaPlus />
                    </IconButton>
                </Tooltip>
            </HStack>
        </HStack>
    );
};

export default PlantHeader;
