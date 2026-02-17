import {
    Box,
    HStack,
    Text,
    Badge,
    Link,
} from "@chakra-ui/react";
import type { TaskDetail } from "./work-types";
import { statusColor, docSubTypeIcon, formatMinutes, ACCENT_COLOR } from "./work-utils";
import { useColorModeValue } from "../ui/color-mode";
import { WorkTaskDetailPopover } from "./work-task-detail-popover";
import { WorkTaskFilter } from "./work-task-filter";

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

                <WorkTaskFilter activeFilters={activeFilters} onFilterChange={onFilterChange} />
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
