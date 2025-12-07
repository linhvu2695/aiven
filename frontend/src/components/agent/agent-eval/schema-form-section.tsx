import { Box, Text, VStack } from "@chakra-ui/react";
import { SchemaFormField } from "./schema-form-field";

interface SchemaFormSectionProps {
    title: string;
    schema: Record<string, any> | null;
    values: Record<string, any>;
    onChange: (values: Record<string, any>) => void;
    prefix?: string; // For nested properties, e.g., "request"
}

/**
 * Resolves a $ref reference in a JSON schema
 */
const resolveRef = (
    ref: string,
    defs: Record<string, any>
): Record<string, any> | null => {
    if (!ref.startsWith("#/$defs/")) {
        return null;
    }
    
    const defName = ref.replace("#/$defs/", "");
    const resolved = defs[defName];
    
    // If resolved schema exists, ensure it has access to defs for nested $ref resolution
    if (resolved) {
        return {
            ...resolved,
            $defs: defs,
        };
    }
    
    return null;
};

/**
 * Gets the nested value for a property path
 */
const getNestedValue = (
    values: Record<string, any>,
    path: string
): any => {
    const parts = path.split(".");
    let current = values;
    for (const part of parts) {
        if (current && typeof current === "object" && part in current) {
            current = current[part];
        } else {
            return undefined;
        }
    }
    return current;
};

/**
 * Sets a nested value for a property path
 */
const setNestedValue = (
    values: Record<string, any>,
    path: string,
    value: any
): Record<string, any> => {
    const parts = path.split(".");
    const newValues = { ...values };
    let current = newValues;
    
    for (let i = 0; i < parts.length - 1; i++) {
        const part = parts[i];
        if (!(part in current) || typeof current[part] !== "object" || current[part] === null) {
            current[part] = {};
        }
        current = current[part];
    }
    
    current[parts[parts.length - 1]] = value;
    return newValues;
};

export const SchemaFormSection = ({
    title,
    schema,
    values,
    onChange,
    prefix = "",
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
    
    const defs = schema.$defs || {};
    const properties = schema.properties as Record<string, Record<string, any>>;
    const required = schema.required ? schema.required as string[] : [];

    const handleFieldChange = (propertyName: string, value: string) => {
        const fullPath = prefix ? `${prefix}.${propertyName}` : propertyName;
        const newValues = setNestedValue(values, fullPath, value);
        onChange(newValues);
    };

    const handleNestedChange = (propertyName: string, nestedValues: Record<string, any>) => {
        const fullPath = prefix ? `${prefix}.${propertyName}` : propertyName;
        const newValues = setNestedValue(values, fullPath, nestedValues);
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
                        // Check if this property has a $ref
                        if (propertySchema.$ref) {
                            const resolvedSchema = resolveRef(propertySchema.$ref, defs);
                            
                            // If resolved schema is an object, render nested properties
                            if (resolvedSchema && resolvedSchema.type === "object" 
                                && resolvedSchema.properties) 
                            {
                                const nestedPath = prefix ? `${prefix}.${propertyName}` : propertyName;
                                const nestedValues = getNestedValue(values, nestedPath) || {};
                                
                                return (
                                    <Box
                                        key={propertyName}
                                        pl={4}
                                        borderLeft="2px solid"
                                        borderColor="gray.300"
                                        _dark={{
                                            borderColor: "gray.600",
                                        }}
                                    >
                                        <SchemaFormSection
                                            title={propertyName}
                                            schema={resolvedSchema}
                                            values={nestedValues}
                                            onChange={(newNestedValues) => handleNestedChange(propertyName, newNestedValues)}
                                            prefix={nestedPath}
                                        />
                                    </Box>
                                );
                            }
                            
                            // Check if resolved schema is an enum
                            else if (resolvedSchema && resolvedSchema.enum 
                                && Array.isArray(resolvedSchema.enum)) 
                            {
                                const fullPath = prefix ? `${prefix}.${propertyName}` : propertyName;
                                const value = getNestedValue(values, fullPath) || "";
                                const enumValue = String(value); // enum values are strings
                                
                                return (
                                    <SchemaFormField
                                        key={propertyName}
                                        propertyName={propertyName}
                                        propertySchema={propertySchema}
                                        value={enumValue}
                                        isRequired={required.includes(propertyName)}
                                        onChange={(value) => handleFieldChange(propertyName, value)}
                                        enumValues={resolvedSchema.enum}
                                    />
                                );
                            }
                            
                            // If resolved schema is not an object or enum, or couldn't be resolved,
                            // fall through to regular field rendering
                        }
                        
                        // Regular field rendering for non-$ref or non-object $ref properties
                        const fullPath = prefix ? `${prefix}.${propertyName}` : propertyName;
                        const value = getNestedValue(values, fullPath);
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

