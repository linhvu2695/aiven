import { Box, HStack, Text, Input, VStack } from "@chakra-ui/react";
import { Dropdown } from "@/components/ui/dropdown";

interface SchemaFormFieldProps {
    propertyName: string;
    propertySchema: Record<string, any>;
    value: string;
    isRequired: boolean;
    onChange: (value: string) => void;
    enumValues?: string[];
}

export const SchemaFormField = ({
    propertyName,
    propertySchema,
    value,
    isRequired,
    onChange,
    enumValues,
}: SchemaFormFieldProps) => {
    const getTypeLabel = (schema: Record<string, any>): string => {
        // AnyOf type
        if (schema.anyOf && Array.isArray(schema.anyOf)) {
            const types = schema.anyOf
                .map((option: Record<string, any>) => option.type)
                .filter((type: any) => type !== undefined && type !== "null");
            if (types.length > 0) {
                return types.join(" | ");
            }
        }
        // Normal type
        if (schema.type) {
            if (Array.isArray(schema.type)) {
                return schema.type.join(" | ");
            }
            return schema.type;
        }
        
        // Ref type
        if (schema.$ref) {
            return `${schema.$ref.replace("#/$defs/", "")}`;
        }
        // Default 
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
                {/* Field name */}
                <HStack justify="space-between" align="center">
                    <HStack align="center">
                        <Text fontWeight="semibold" fontSize="sm">
                            {propertyName}
                        </Text>
                        {isRequired && (
                            <Text as="span" color="red.500" ml={1}>
                                *
                            </Text>
                        )}
                    </HStack>
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

                {/* Field value */}
                {enumValues && enumValues.length > 0 ? (
                    <Dropdown
                        value={value}
                        onValueChange={onChange}
                        options={enumValues.map((enumValue) => ({
                            value: enumValue,
                            label: enumValue,
                        }))}
                        placeholder={`Select ${propertyName}`}
                    />
                ) : (
                    <Input
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        placeholder={`Enter value for ${propertyName}`}
                        size="sm"
                    />
                )}
            </VStack>
        </Box>
    );
};
