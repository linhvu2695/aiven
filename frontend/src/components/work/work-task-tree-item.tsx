import {
    Box,
    VStack,
    HStack,
    Text,
    IconButton,
    Badge,
    Collapsible,
    useDisclosure,
} from "@chakra-ui/react";
import { FaChevronRight, FaChevronDown } from "react-icons/fa";
import type { TaskDetail } from "./work-types";
import { statusColor, docSubTypeIcon } from "./work-utils";
import { WorkTaskDetailPopover } from "./work-task-detail-popover";
import { WorkTaskProgressBar } from "./work-task-progress-bar";

interface WorkTaskTreeItemProps {
    task: TaskDetail;
    allTasks: TaskDetail[];
    maxTime: number;
    scaleMode: "linear" | "log";
    level?: number;
}

export const WorkTaskTreeItem = ({
    task,
    allTasks,
    maxTime,
    scaleMode,
    level = 0,
}: WorkTaskTreeItemProps) => {
    const obsolete = task.status.toLowerCase().includes("obsolete");
    const { open, onToggle } = useDisclosure({ defaultOpen: !obsolete });

    const children = allTasks.filter(
        (t) => t.parent_folder_identifier === task.identifier
    );
    const hasChildren = children.length > 0;

    // Compute aggregate time for this node + all descendants (skip obsolete)
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

    return (
        <Box>
            <HStack
                p={2}
                style={{ paddingLeft: `${level * 24 + 12}px` }}
                _hover={{
                    bg: { base: "gray.100", _dark: "gray.800" },
                    "& .view-button": { opacity: 1 },
                }}
                borderRadius="md"
                gap={2}
            >
                {/* Expand/collapse toggle */}
                <Box w="20px" flexShrink={0}>
                    {hasChildren && (
                        <IconButton
                            aria-label="Toggle children"
                            variant="ghost"
                            size="2xs"
                            onClick={onToggle}
                        >
                            {open ? <FaChevronDown /> : <FaChevronRight />}
                        </IconButton>
                    )}
                </Box>

                {/* Doc sub type icon + Task title + status */}
                <HStack flex={1} gap={2} overflow="hidden">
                    {docSubTypeIcon(task.doc_sub_type).icon && (
                        <Box color={docSubTypeIcon(task.doc_sub_type).color} flexShrink={0}>
                            {docSubTypeIcon(task.doc_sub_type).icon}
                        </Box>
                    )}
                    <Text fontSize="sm" truncate color={obsolete ? "fg.subtle" : undefined}>
                        {task.title || task.identifier}
                    </Text>
                    <Badge
                        size="sm"
                        colorPalette={statusColor(task.status)}
                        variant="subtle"
                        flexShrink={0}
                    >
                        {task.status || "—"}
                    </Badge>
                </HStack>

                {/* Progress bar (spent / total, scaled) — hidden for obsolete */}
                {!obsolete && (
                    <WorkTaskProgressBar
                        spent={totalSpent}
                        left={totalLeft}
                        maxTime={maxTime}
                        scaleMode={scaleMode}
                    />
                )}

                {/* View detail popover */}
                <WorkTaskDetailPopover task={task} />
            </HStack>

            {/* Children */}
            {hasChildren && (
                <Collapsible.Root open={open}>
                    <Collapsible.Content>
                        <VStack gap={0} align="stretch">
                            {children.map((child) => (
                                <WorkTaskTreeItem
                                    key={child.identifier}
                                    task={child}
                                    allTasks={allTasks}
                                    maxTime={maxTime}
                                    scaleMode={scaleMode}
                                    level={level + 1}
                                />
                            ))}
                        </VStack>
                    </Collapsible.Content>
                </Collapsible.Root>
            )}
        </Box>
    );
};
