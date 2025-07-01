import { Box, Text, VStack } from "@chakra-ui/react";

export interface AgentGridItemProps {
    name: string;
    description: string;
    imageUrl: string;
}

export const AgentGridItem = ({ name, description, imageUrl }: AgentGridItemProps) => {
    return (
        <Box
            borderRadius="lg"
            overflow="hidden"
            position="relative"
            bgImage={`url(${imageUrl})`}
            bgSize="cover"
            bgPos="center"
            h="300px"
            _hover={{
                transform: "scale(1.05)",
                transition: "transform 0.2s ease-in-out",
            }}
        >
            <VStack
                position="absolute"
                bottom="0"
                left="0"
                right="0"
                bg="linear-gradient(to top, rgba(0,0,0,0.8), transparent)"
                p={4}
                align="start"
                spaceY={1}
            >
                <Text fontWeight="bold" fontSize="xl" color="white">
                    {name}
                </Text>
                <Text fontSize="sm" color="gray.200" lineClamp={2}>
                    {description}
                </Text>
            </VStack>
        </Box>
    );
}; 