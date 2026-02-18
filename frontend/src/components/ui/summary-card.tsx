import { Box, Text } from "@chakra-ui/react";

export const SummaryCard = ({ label, value, color }: { label: string; value: string; color?: string }) => (
    <Box px={4} py={3} borderWidth="1px" borderColor="border.default" borderRadius="md" minW="120px">
        <Text fontSize="xs" color="fg.muted" mb={1}>{label}</Text>
        <Text fontSize="lg" fontWeight="bold" color={color}>{value}</Text>
    </Box>
);
