import {
    Box,
    HStack,
    VStack,
    Text,
    IconButton,
    Popover,
    Portal,
    Checkbox,
} from "@chakra-ui/react";
import { FaFilter } from "react-icons/fa";
import { docSubTypeIcon, DOC_SUB_TYPES } from "./work-utils";

interface WorkTaskFilterProps {
    activeFilters: Set<string>;
    onFilterChange: (filters: Set<string>) => void;
}

export const WorkTaskFilter = ({ activeFilters, onFilterChange }: WorkTaskFilterProps) => {
    const allSelected = DOC_SUB_TYPES.every((t) => activeFilters.has(t));

    const toggleType = (type: string) => {
        const next = new Set(activeFilters);
        if (next.has(type)) {
            next.delete(type);
        } else {
            next.add(type);
        }
        onFilterChange(next);
    };

    const toggleAll = () => {
        if (allSelected) {
            onFilterChange(new Set());
        } else {
            onFilterChange(new Set(DOC_SUB_TYPES));
        }
    };

    return (
        <Popover.Root>
            <Popover.Trigger asChild>
                <IconButton
                    aria-label="Filter task types"
                    variant="ghost"
                    size="xs"
                    flexShrink={0}
                >
                    <FaFilter />
                </IconButton>
            </Popover.Trigger>
            <Portal>
                <Popover.Positioner>
                    <Popover.Content w="240px" p={3}>
                        <Popover.Arrow>
                            <Popover.ArrowTip />
                        </Popover.Arrow>
                        <VStack align="stretch" gap={1}>
                            <Text fontSize="xs" fontWeight="semibold" color="fg.muted" mb={1}>
                                Filter by task type
                            </Text>

                            <Checkbox.Root
                                checked={allSelected}
                                onCheckedChange={toggleAll}
                                size="sm"
                            >
                                <Checkbox.HiddenInput />
                                <Checkbox.Control />
                                <Checkbox.Label>
                                    <Text fontSize="xs" fontWeight="medium">All</Text>
                                </Checkbox.Label>
                            </Checkbox.Root>

                            <Box borderBottomWidth="1px" borderColor="border.default" my={1} />

                            {DOC_SUB_TYPES.map((type) => {
                                const { icon, color } = docSubTypeIcon(type);
                                return (
                                    <Checkbox.Root
                                        key={type}
                                        checked={activeFilters.has(type)}
                                        onCheckedChange={() => toggleType(type)}
                                        size="sm"
                                    >
                                        <Checkbox.HiddenInput />
                                        <Checkbox.Control />
                                        <Checkbox.Label>
                                            <HStack gap={1}>
                                                {icon && <Box color={color}>{icon}</Box>}
                                                <Text fontSize="xs">{type}</Text>
                                            </HStack>
                                        </Checkbox.Label>
                                    </Checkbox.Root>
                                );
                            })}
                        </VStack>
                    </Popover.Content>
                </Popover.Positioner>
            </Portal>
        </Popover.Root>
    );
};
