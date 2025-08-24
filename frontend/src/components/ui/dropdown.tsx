import {
    Box,
    Text,
    Select,
    createListCollection,
} from "@chakra-ui/react";

export interface DropdownOption {
    value: string;
    label: string;
}

export interface DropdownProps {
    title?: string;
    value: string;
    onValueChange: (value: string) => void;
    options: DropdownOption[];
    placeholder?: string;
    fontSize?: string;
    fontWeight?: string;
    disabled?: boolean;
    mb?: number | string;
    flex?: number;
    isRequired?: boolean;
}

export const Dropdown = ({
    title,
    value,
    onValueChange,
    options,
    placeholder = "Select an option",
    fontSize = "sm",
    fontWeight = "medium",
    disabled = false,
    mb = 2,
    flex,
    isRequired = false,
}: DropdownProps) => {
    const handleValueChange = (e: { value: string[] }) => {
        onValueChange(e.value[0] || "");
    };

    return (
        <Box flex={flex} width="100%">
            {title && (
                <Text fontSize={fontSize} fontWeight={fontWeight} mb={mb}>
                    {title}
                    {isRequired && (
                        <Text as="span" color="red.500" ml={1}>
                            *
                        </Text>
                    )}
                </Text>
            )}
            <Select.Root
                value={value ? [value] : []}
                onValueChange={handleValueChange}
                collection={createListCollection({
                    items: options,
                })}
                disabled={disabled}
            >
                <Select.Trigger>
                    <Select.ValueText placeholder={placeholder} />
                    <Select.Indicator />
                </Select.Trigger>
                <Select.Positioner>
                    <Select.Content
                        bg="white"
                        borderRadius="md"
                        borderWidth="1px"
                        borderColor="gray.200"
                        _dark={{ bg: "gray.800", borderColor: "gray.600" }}
                        boxShadow="lg"
                        p={1}
                        minW="200px"
                        maxH="300px"
                        overflowY="auto"
                        zIndex={1000}
                    >
                        {options.map((option) => (
                            <Select.Item 
                                key={option.value} 
                                item={option.value}
                                px={3}
                                py={2}
                                borderRadius="sm"
                                _hover={{ 
                                    bg: "gray.100", 
                                    _dark: { bg: "gray.700" } 
                                }}
                                _selected={{ 
                                    bg: "teal.50", 
                                    color: "teal.600",
                                    _dark: { bg: "teal.900", color: "teal.300" }
                                }}
                                cursor="pointer"
                                transition="all 0.2s"
                            >
                                {option.label}
                            </Select.Item>
                        ))}
                    </Select.Content>
                </Select.Positioner>
            </Select.Root>
        </Box>
    );
};
