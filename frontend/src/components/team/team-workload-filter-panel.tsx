import { Box, VStack, HStack, Text, Checkbox } from "@chakra-ui/react";
import { DOC_SUB_TYPES, docSubTypeIcon } from "@/components/work/work-utils";

interface TeamWorkloadFilterPanelProps {
    selectedTypes: Set<string>;
    onSelectedTypesChange: (types: Set<string>) => void;
}

export const TeamWorkloadFilterPanel = ({
    selectedTypes,
    onSelectedTypesChange,
}: TeamWorkloadFilterPanelProps) => {
    const allTypesSelected = DOC_SUB_TYPES.every((t) => selectedTypes.has(t));

    const toggleType = (type: string) => {
        onSelectedTypesChange(
            (() => {
                const next = new Set(selectedTypes);
                if (next.has(type)) next.delete(type);
                else next.add(type);
                return next;
            })()
        );
    };

    const toggleAllTypes = () => {
        if (allTypesSelected) onSelectedTypesChange(new Set());
        else onSelectedTypesChange(new Set(DOC_SUB_TYPES));
    };

    return (
        <Box
            w="280px"
            flexShrink={0}
            borderLeftWidth="1px"
            borderColor="border.default"
            overflowY="auto"
            px={3}
            py={4}
        >
            <VStack align="stretch" gap={1}>
                <Text fontSize="xs" fontWeight="semibold" color="fg.muted" mb={1}>
                    Task type
                </Text>

                <Checkbox.Root checked={allTypesSelected} onCheckedChange={toggleAllTypes} size="sm">
                    <Checkbox.HiddenInput />
                    <Checkbox.Control />
                    <Checkbox.Label>
                        <Text fontSize="xs" fontWeight="medium">
                            All
                        </Text>
                    </Checkbox.Label>
                </Checkbox.Root>

                <Box borderBottomWidth="1px" borderColor="border.default" my={1} />

                {DOC_SUB_TYPES.map((type) => {
                    const { icon, color } = docSubTypeIcon(type);
                    return (
                        <HStack key={type} gap={0}>
                            <Checkbox.Root
                                checked={selectedTypes.has(type)}
                                onCheckedChange={() => toggleType(type)}
                                size="sm"
                            >
                                <Checkbox.HiddenInput />
                                <Checkbox.Control />
                            </Checkbox.Root>
                            <HStack
                                gap={1}
                                flex={1}
                                cursor="pointer"
                                px={1}
                                borderRadius="sm"
                                _hover={{ bg: { base: "gray.100", _dark: "gray.700" } }}
                                onClick={() => onSelectedTypesChange(new Set([type]))}
                            >
                                {icon && <Box color={color}>{icon}</Box>}
                                <Text fontSize="xs">{type}</Text>
                            </HStack>
                        </HStack>
                    );
                })}
            </VStack>
        </Box>
    );
};
