import { Box, HStack, Text, Input, VStack } from "@chakra-ui/react";

interface SchemaFormFieldProps {
    propertyName: string;
    propertySchema: Record<string, any>;
    value: string;
    onChange: (value: string) => void;
}

export const SchemaFormField = ({
    propertyName,
    propertySchema,
    value,
    onChange,
}: SchemaFormFieldProps) => {
    const getTypeLabel = (schema: Record<string, any>): string => {
        if (schema.type) {
            if (Array.isArray(schema.type)) {
                return schema.type.join(" | ");
            }
            return schema.type;
        }
        return "any";
    };

    const typeLabel = getTypeLabel(propertySchema);

    return (
        <Box
            p={3}
            border="1px solid"
            borderColor="gray.200"
            borderRadius="md"
            _dark={{
                borderColor: "gray.700",
            }}
        >
            <VStack align="stretch" gap={2}>
                <HStack justify="space-between" align="center">
                    <Text fontWeight="semibold" fontSize="sm">
                        {propertyName}
                    </Text>
                    <Text
                        fontSize="xs"
                        color="gray.500"
                        fontFamily="mono"
                        px={2}
                        py={1}
                        bg="gray.100"
                        borderRadius="sm"
                        _dark={{
                            bg: "gray.800",
                            color: "gray.400",
                        }}
                    >
                        {typeLabel}
                    </Text>
                </HStack>
                <Input
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={`Enter value for ${propertyName}`}
                    size="sm"
                />
            </VStack>
        </Box>
    );
};

