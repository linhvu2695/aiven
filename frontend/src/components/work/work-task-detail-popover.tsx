import { useState } from "react";
import {
    Box,
    VStack,
    HStack,
    Text,
    IconButton,
    Badge,
    Popover,
    Portal,
    Link,
    Spinner,
} from "@chakra-ui/react";
import {
    FaInfoCircle,
    FaUser,
    FaUsers,
    FaBox,
    FaCalendarAlt,
    FaLink,
    FaProjectDiagram,
    FaExclamationTriangle,
    FaCloudDownloadAlt,
    FaSyncAlt,
} from "react-icons/fa";
import { BASE_URL } from "@/App";
import { toaster } from "@/components/ui/toaster";
import { Tooltip } from "@/components/ui/tooltip";
import type { TaskDetail } from "./work-types";
import { formatMinutes, formatDate, statusColor, docSubTypeIcon } from "./work-utils";
import { useWorkContext } from "@/context/work-ctx";

const DetailRow = ({
    icon,
    label,
    children,
}: {
    icon: React.ReactNode;
    label: string;
    children: React.ReactNode;
}) => (
    <HStack gap={2} py={1}>
        <HStack gap={1} minW="120px" flexShrink={0} color="fg.muted">
            {icon}
            <Text fontSize="xs" fontWeight="medium">
                {label}
            </Text>
        </HStack>
        <Box flex={1}>{children}</Box>
    </HStack>
);

interface WorkTaskDetailPopoverProps {
    task: TaskDetail;
}

export const WorkTaskDetailPopover = ({ task }: WorkTaskDetailPopoverProps) => {
    const { updateTask, refreshTaskTree } = useWorkContext();
    const [isRefreshing, setIsRefreshing] = useState(false);
    const docSubType = task.doc_sub_type ? docSubTypeIcon(task.doc_sub_type) : null;
    const [isRefreshingTree, setIsRefreshingTree] = useState(false);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        try {
            const res = await fetch(`${BASE_URL}/api/work/task/${task.identifier}?force_refresh=true`);
            if (!res.ok) throw new Error("Failed to refresh task");
            const updatedTask: TaskDetail = await res.json();
            updateTask(updatedTask);
            toaster.create({ description: `Updated ${task.identifier}`, type: "success" });
        } catch (error) {
            toaster.create({ description: `Failed to refresh ${task.identifier}`, type: "error" });
        } finally {
            setIsRefreshing(false);
        }
    };

    const handleRefreshTree = async () => {
        setIsRefreshingTree(true);
        try {
            await refreshTaskTree(task.identifier);
        } finally {
            setIsRefreshingTree(false);
        }
    };

    return (
        <Popover.Root>
            <Popover.Trigger asChild>
                <IconButton
                    className="view-button"
                    aria-label="View task details"
                    variant="ghost"
                    size="2xs"
                    opacity={0}
                    transition="opacity 0.15s"
                    flexShrink={0}
                    onClick={(e) => e.stopPropagation()}
                >
                    <FaInfoCircle />
                </IconButton>
            </Popover.Trigger>
            <Portal>
                <Popover.Positioner>
                    <Popover.Content w="360px" p={4}>
                        <Popover.Arrow>
                            <Popover.ArrowTip />
                        </Popover.Arrow>

                        <VStack align="stretch" gap={2}>
                            <HStack gap={2} flexWrap="wrap">
                                <Badge size="sm" variant="outline" colorPalette="gray">
                                    {task.identifier}
                                </Badge>
                                {docSubType?.icon && (
                                    <Tooltip content={task.doc_sub_type}>
                                        <Box color={docSubType.color} flexShrink={0}>
                                            {docSubType.icon}
                                        </Box>
                                    </Tooltip>
                                )}
                                <Badge
                                    size="sm"
                                    colorPalette={statusColor(task.status)}
                                    variant="solid"
                                >
                                    {task.status || "No status"}
                                </Badge>
                                <Tooltip content="Refresh this task">
                                    <IconButton
                                        aria-label="Refresh task from Orange Logic"
                                        variant="ghost"
                                        size="2xs"
                                        onClick={handleRefresh}
                                        disabled={isRefreshing || isRefreshingTree}
                                    >
                                        {isRefreshing ? <Spinner size="xs" /> : <FaCloudDownloadAlt />}
                                    </IconButton>
                                </Tooltip>
                                <Tooltip content="Refresh this task and all descendants">
                                    <IconButton
                                        aria-label="Refresh task tree from Orange Logic"
                                        variant="ghost"
                                        size="2xs"
                                        onClick={handleRefreshTree}
                                        disabled={isRefreshing || isRefreshingTree}
                                    >
                                        {isRefreshingTree ? <Spinner size="xs" /> : <FaSyncAlt />}
                                    </IconButton>
                                </Tooltip>
                            </HStack>

                            <HStack gap={1}>
                                <Text fontWeight="semibold" fontSize="sm">
                                    {task.title || "Untitled Task"}
                                </Text>
                            </HStack>

                            {/* Time summary */}
                            <HStack
                                gap={4}
                                py={2}
                                px={3}
                                borderRadius="md"
                                bg="bg.subtle"
                                borderWidth="1px"
                                borderColor="border.default"
                            >
                                <VStack gap={0} align="center" flex={1}>
                                    <Text fontSize="2xs" color="fg.muted">Spent</Text>
                                    <Text fontSize="sm" fontWeight="bold">
                                        {formatMinutes(task.time_spent_mn)}
                                    </Text>
                                </VStack>
                                <VStack gap={0} align="center" flex={1}>
                                    <Text fontSize="2xs" color="fg.muted">Left</Text>
                                    <Text fontSize="sm" fontWeight="bold">
                                        {formatMinutes(task.time_left_mn)}
                                    </Text>
                                </VStack>
                                <VStack gap={0} align="center" flex={1}>
                                    <Text fontSize="2xs" color="fg.muted">Total</Text>
                                    <Text fontSize="sm" fontWeight="bold">
                                        {formatMinutes(task.time_spent_mn + task.time_left_mn)}
                                    </Text>
                                </VStack>
                            </HStack>

                            {/* Detail rows */}
                            <VStack align="stretch" gap={0} divideY="1px">
                                <DetailRow icon={<FaUser size={10} />} label="Assigned To">
                                    <Text fontSize="xs">{task.assigned_to || "—"}</Text>
                                </DetailRow>
                                <DetailRow icon={<FaUsers size={10} />} label="Dev Team">
                                    <HStack gap={1} flexWrap="wrap">
                                        {task.main_dev_team.length > 0 ? (
                                            task.main_dev_team.map((m) => (
                                                <Badge key={m} size="sm" variant="subtle">{m}</Badge>
                                            ))
                                        ) : (
                                            <Text fontSize="xs" color="fg.muted">—</Text>
                                        )}
                                    </HStack>
                                </DetailRow>
                                <DetailRow icon={<FaBox size={10} />} label="Module">
                                    <Text fontSize="xs">{task.module || "—"}</Text>
                                </DetailRow>
                                <DetailRow icon={<FaExclamationTriangle size={10} />} label="Priority">
                                    <Text fontSize="xs">{task.importance_for_next_release || "—"}</Text>
                                </DetailRow>
                                <DetailRow icon={<FaCalendarAlt size={10} />} label="Est. Start">
                                    <Text fontSize="xs">{formatDate(task.estimated_start_date)}</Text>
                                </DetailRow>
                                <DetailRow icon={<FaCalendarAlt size={10} />} label="Est. End">
                                    <Text fontSize="xs">{formatDate(task.estimated_end_date)}</Text>
                                </DetailRow>
                                <DetailRow icon={<FaCalendarAlt size={10} />} label="Est. Completion">
                                    <Text fontSize="xs">{formatDate(task.estimated_completion_date)}</Text>
                                </DetailRow>
                                <DetailRow icon={<FaCalendarAlt size={10} />} label="Complete Date">
                                    <Text fontSize="xs">{formatDate(task.completion_date)}</Text>
                                </DetailRow>
                                {task.dependencies.length > 0 && (
                                    <DetailRow icon={<FaProjectDiagram size={10} />} label="Dependencies">
                                        <HStack gap={1} flexWrap="wrap">
                                            {task.dependencies.map((dep) => (
                                                <Badge key={dep} size="sm" variant="outline">{dep}</Badge>
                                            ))}
                                        </HStack>
                                    </DetailRow>
                                )}
                                {task.cortex_share_link && (
                                    <DetailRow icon={<FaLink size={10} />} label="Link">
                                        <Link
                                            href={task.cortex_share_link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            fontSize="xs"
                                            color="blue.500"
                                            _hover={{ textDecoration: "underline" }}
                                        >
                                            Open in Cortex
                                        </Link>
                                    </DetailRow>
                                )}
                            </VStack>
                        </VStack>
                    </Popover.Content>
                </Popover.Positioner>
            </Portal>
        </Popover.Root>
    );
};
