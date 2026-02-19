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
import { FaFilter, FaUser } from "react-icons/fa";
import { docSubTypeIcon, DOC_SUB_TYPES } from "./work-utils";

interface WorkTaskFilterProps {
    activeFilters: Set<string>;
    onFilterChange: (filters: Set<string>) => void;
    assignees?: string[];
    activeAssigneeFilters?: Set<string> | null;
    onAssigneeFilterChange?: (filters: Set<string> | null) => void;
}

export const WorkTaskFilter = ({
    activeFilters,
    onFilterChange,
    assignees = [],
    activeAssigneeFilters = null,
    onAssigneeFilterChange,
}: WorkTaskFilterProps) => {
    const allTypesSelected = DOC_SUB_TYPES.every((t) => activeFilters.has(t));

    const toggleType = (type: string) => {
        const next = new Set(activeFilters);
        if (next.has(type)) {
            next.delete(type);
        } else {
            next.add(type);
        }
        onFilterChange(next);
    };

    const toggleAllTypes = () => {
        if (allTypesSelected) {
            onFilterChange(new Set());
        } else {
            onFilterChange(new Set(DOC_SUB_TYPES));
        }
    };

    const selectExclusiveType = (type: string) => {
        onFilterChange(new Set([type]));
    };

    const allAssigneesSelected =
        activeAssigneeFilters === null || assignees.every((a) => activeAssigneeFilters.has(a));

    const isAssigneeSelected = (name: string) =>
        activeAssigneeFilters === null || activeAssigneeFilters.has(name);

    const toggleAssignee = (name: string) => {
        if (!onAssigneeFilterChange) return;
        if (activeAssigneeFilters === null) {
            const next = new Set(assignees);
            next.delete(name);
            onAssigneeFilterChange(next);
        } else {
            const next = new Set(activeAssigneeFilters);
            if (next.has(name)) {
                next.delete(name);
            } else {
                next.add(name);
            }
            if (assignees.every((a) => next.has(a))) {
                onAssigneeFilterChange(null);
            } else {
                onAssigneeFilterChange(next);
            }
        }
    };

    const toggleAllAssignees = () => {
        if (!onAssigneeFilterChange) return;
        if (allAssigneesSelected) {
            onAssigneeFilterChange(new Set());
        } else {
            onAssigneeFilterChange(null);
        }
    };

    const selectExclusiveAssignee = (name: string) => {
        onAssigneeFilterChange?.(new Set([name]));
    };

    const hasAssigneeFilter = assignees.length > 0 && onAssigneeFilterChange;

    return (
        <Popover.Root positioning={{ placement: "bottom-start" }}>
            <Popover.Trigger asChild>
                <IconButton
                    aria-label="Filter tasks"
                    variant="ghost"
                    size="xs"
                    flexShrink={0}
                >
                    <FaFilter />
                </IconButton>
            </Popover.Trigger>
            <Portal>
                <Popover.Positioner>
                    <Popover.Content w={hasAssigneeFilter ? "auto" : "240px"} p={3}>
                        <Popover.Arrow>
                            <Popover.ArrowTip />
                        </Popover.Arrow>
                        <HStack align="start" gap={4}>
                            {/* Task type column */}
                            <VStack align="stretch" gap={1} minW="200px">
                                <Text fontSize="xs" fontWeight="semibold" color="fg.muted" mb={1}>
                                    Task type
                                </Text>

                                <Checkbox.Root
                                    checked={allTypesSelected}
                                    onCheckedChange={toggleAllTypes}
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
                                        <HStack key={type} gap={0}>
                                            <Checkbox.Root
                                                checked={activeFilters.has(type)}
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
                                                onClick={() => selectExclusiveType(type)}
                                            >
                                                {icon && <Box color={color}>{icon}</Box>}
                                                <Text fontSize="xs">{type}</Text>
                                            </HStack>
                                        </HStack>
                                    );
                                })}
                            </VStack>

                            {/* Assignee column */}
                            {hasAssigneeFilter && (
                                <>
                                    <Box alignSelf="stretch" borderLeftWidth="1px" borderColor="border.default" />

                                    <VStack align="stretch" gap={1} minW="140px">
                                        <Text fontSize="xs" fontWeight="semibold" color="fg.muted" mb={1}>
                                            Assignee
                                        </Text>

                                        <Checkbox.Root
                                            checked={allAssigneesSelected}
                                            onCheckedChange={toggleAllAssignees}
                                            size="sm"
                                        >
                                            <Checkbox.HiddenInput />
                                            <Checkbox.Control />
                                            <Checkbox.Label>
                                                <Text fontSize="xs" fontWeight="medium">All</Text>
                                            </Checkbox.Label>
                                        </Checkbox.Root>

                                        <Box borderBottomWidth="1px" borderColor="border.default" my={1} />

                                        {assignees.map((name) => (
                                            <HStack key={name} gap={0}>
                                                <Checkbox.Root
                                                    checked={isAssigneeSelected(name)}
                                                    onCheckedChange={() => toggleAssignee(name)}
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
                                                    onClick={() => selectExclusiveAssignee(name)}
                                                >
                                                    <Box color="fg.muted"><FaUser size={10} /></Box>
                                                    <Text fontSize="xs">{name}</Text>
                                                </HStack>
                                            </HStack>
                                        ))}
                                    </VStack>
                                </>
                            )}
                        </HStack>
                    </Popover.Content>
                </Popover.Positioner>
            </Portal>
        </Popover.Root>
    );
};
