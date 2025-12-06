import { Box, Text, VStack } from "@chakra-ui/react";
import { SchemaFormField } from "./schema-form-field";

interface SchemaFormSectionProps {
    title: string;
    schema: Record<string, any> | null;
    values: Record<string, any>;
    onChange: (values: Record<string, any>) => void;
}

export const SchemaFormSection = ({
    title,
    schema,
    values,
    onChange,
}: SchemaFormSectionProps) => {
    if (!schema || schema.type !== "object" || !schema.properties) {
        return (
            <Box>
                <Text fontWeight="semibold" mb={2} fontSize="sm">
                    {title}
                </Text>
                <Text fontSize="xs" color="gray.500" fontStyle="italic">
                    No schema defined or invalid schema structure
                </Text>
            </Box>
        );
    }

    const properties = schema.properties as Record<string, Record<string, any>>;
    const required = schema.required as string[];

    const handleFieldChange = (propertyName: string, value: string) => {
        const newValues = {
            ...values,
            [propertyName]: value,
        };
        onChange(newValues);
    };

    return (
        <Box>
            <Text fontWeight="semibold" mb={3} fontSize="sm">
                {title}
            </Text>
            {Object.keys(properties).length === 0 ? (
                <Text fontSize="xs" color="gray.500" fontStyle="italic">
                    No properties defined in schema
                </Text>
            ) : (
                <VStack gap={2} align="stretch">
                    {Object.entries(properties).map(([propertyName, propertySchema]) => {
                        // Convert value to string for display in input field
                        const value = values[propertyName];
                        const displayValue = value !== undefined && value !== null
                            ? String(value)
                            : "";
                        
                        return (
                            <SchemaFormField
                                key={propertyName}
                                propertyName={propertyName}
                                propertySchema={propertySchema}
                                value={displayValue}
                                isRequired={required.includes(propertyName)}
                                onChange={(value) => handleFieldChange(propertyName, value)}
                            />
                        );
                    })}
                </VStack>
            )}
        </Box>
    );
};

