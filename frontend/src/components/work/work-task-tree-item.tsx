import {
    Box,
    VStack,
    HStack,
    Text,
    IconButton,
    Badge,
    Collapsible,
    Link,
    useDisclosure,
} from "@chakra-ui/react";
import { FaChevronRight, FaChevronDown } from "react-icons/fa";
import type { TaskDetail } from "./work-types";
import { statusColor, docSubTypeIcon, ACCENT_COLOR } from "./work-utils";
import { useColorModeValue } from "../ui/color-mode";
import { WorkTaskDetailPopover } from "./work-task-detail-popover";
import { WorkTaskProgressBar } from "./work-task-progress-bar";

interface WorkTaskTreeItemProps {
    task: TaskDetail;
    allTasks: TaskDetail[];
    maxTime: number;
    level?: number;
}

export const WorkTaskTreeItem = ({
    task,
    allTasks,
    maxTime,
    level = 0,
}: WorkTaskTreeItemProps) => {
    const accentColor = useColorModeValue(ACCENT_COLOR.light, ACCENT_COLOR.dark);
    const statusLower = task.status.toLowerCase();
    const obsolete = statusLower.includes("obsolete");
    const blocked = statusLower.includes("blocked");
    const { open, onToggle } = useDisclosure({ defaultOpen: !obsolete && !blocked });

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
    const completed = totalLeft === 0;

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
                    {task.cortex_share_link ? (
                        <Link
                            href={task.cortex_share_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            fontSize="sm"
                            truncate
                            color={obsolete ? "fg.subtle" : undefined}
                            _hover={{ textDecoration: "underline" }}
                        >
                            {task.title || task.identifier}
                        </Link>
                    ) : (
                        <Text fontSize="sm" truncate color={obsolete ? "fg.subtle" : undefined}>
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
                </HStack>

                {/* Progress bar (spent / total, scaled) — hidden for obsolete */}
                {!obsolete && (
                    <WorkTaskProgressBar
                        spent={totalSpent}
                        left={totalLeft}
                        maxTime={maxTime}
                    />
                )}

                {/* Assignee */}
                <Box flexShrink={0} w="100px">
                    <Text fontSize="xs" color={completed ? accentColor : "fg.muted"} truncate textAlign="right">
                        {task.assigned_to || "—"}
                    </Text>
                </Box>

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
