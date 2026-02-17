import {
    Box,
    HStack,
    VStack,
    Text,
    Badge,
    Link,
    IconButton,
    Popover,
    Portal,
    Checkbox,
} from "@chakra-ui/react";
import { FaFilter } from "react-icons/fa";
import type { TaskDetail } from "./work-types";
import { statusColor, docSubTypeIcon, formatMinutes, ACCENT_COLOR, DOC_SUB_TYPES } from "./work-utils";
import { useColorModeValue } from "../ui/color-mode";
import { WorkTaskDetailPopover } from "./work-task-detail-popover";

interface WorkTaskHeaderFilterProps {
    activeFilters: Set<string>;
    onFilterChange: (filters: Set<string>) => void;
}

const WorkTaskHeaderFilter = ({ activeFilters, onFilterChange }: WorkTaskHeaderFilterProps) => {
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

interface WorkTaskHeaderProps {
    task: TaskDetail;
    allTasks: TaskDetail[];
    activeFilters: Set<string>;
    onFilterChange: (filters: Set<string>) => void;
}

export const WorkTaskHeader = ({ task, allTasks, activeFilters, onFilterChange }: WorkTaskHeaderProps) => {
    const accentColor = useColorModeValue(ACCENT_COLOR.light, ACCENT_COLOR.dark);

    const getSubtreeTime = (
        t: TaskDetail,
        field: "time_spent_mn" | "time_left_mn"
    ): number => {
        if (t.status.toLowerCase().includes("obsolete")) return 0;
        const directChildren = allTasks.filter(
            (c) => c.parent_folder_identifier === t.identifier
        );
        return (
            t[field] +
            directChildren.reduce((sum, c) => sum + getSubtreeTime(c, field), 0)
        );
    };

    const totalSpent = getSubtreeTime(task, "time_spent_mn");
    const totalLeft = getSubtreeTime(task, "time_left_mn");
    const total = totalSpent + totalLeft;
    const spentPct = total > 0 ? (totalSpent / total) * 100 : 0;
    const completed = totalLeft === 0;

    const { icon: docIcon, color: docIconColor } = docSubTypeIcon(task.doc_sub_type);

    return (
        <Box
            px={4}
            py={3}
            borderBottomWidth="1px"
            borderColor="border.default"
            bg="bg.subtle"
            flexShrink={0}
        >
            {/* Top row: icon + title + status + filter + popover */}
            <HStack gap={3} mb={2} css={{ "& .view-button": { opacity: 1 } }}>
                {docIcon && (
                    <Box color={docIconColor} flexShrink={0}>
                        {docIcon}
                    </Box>
                )}
                {task.cortex_share_link ? (
                    <Link
                        href={task.cortex_share_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        fontSize="md"
                        fontWeight="semibold"
                        truncate
                        _hover={{ textDecoration: "underline" }}
                    >
                        {task.title || task.identifier}
                    </Link>
                ) : (
                    <Text fontSize="md" fontWeight="semibold" truncate>
                        {task.title || task.identifier}
                    </Text>
                )}
                <Badge
                    size="sm"
                    colorPalette={statusColor(task.status)}
                    variant="subtle"
                    flexShrink={0}
                >
                    {task.status || "—"}
                </Badge>
                <Badge size="sm" variant="outline" colorPalette="gray" flexShrink={0}>
                    {task.identifier}
                </Badge>
                <Box flex={1} />
                {task.assigned_to && (
                    <Text fontSize="xs" color={completed ? accentColor : "fg.muted"} flexShrink={0}>
                        {task.assigned_to}
                    </Text>
                )}

                <WorkTaskHeaderFilter activeFilters={activeFilters} onFilterChange={onFilterChange} />
                <WorkTaskDetailPopover task={task} />
            </HStack>

            {/* Bottom row: progress bar (full width) + time label */}
            {total > 0 && (
                <HStack gap={3} align="center">
                    {/* Time label */}
                    {completed ? (
                        <Text fontSize="xs" whiteSpace="nowrap" color={accentColor} fontWeight="bold">
                            {formatMinutes(total)}
                        </Text>
                    ) : (
                        <Text fontSize="xs" whiteSpace="nowrap">
                            <Text as="span" color={accentColor}>{formatMinutes(totalSpent)}</Text>
                            <Text as="span" color="fg.muted"> / {formatMinutes(total)}</Text>
                        </Text>
                    )}

                    {/* Full-width bar */}
                    <Box
                        flex={1}
                        h="10px"
                        borderRadius="full"
                        bg="gray.600"
                        overflow="hidden"
                    >
                        <Box
                            h="full"
                            w={`${spentPct}%`}
                            borderRadius="full"
                            bg={accentColor}
                            transition="width 0.3s"
                        />
                    </Box>
                </HStack>
            )}
        </Box>
    );
};
