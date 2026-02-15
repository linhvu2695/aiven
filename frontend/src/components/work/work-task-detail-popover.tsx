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
} from "@chakra-ui/react";
import {
    FaInfoCircle,
    FaUser,
    FaUsers,
    FaCalendarAlt,
    FaLink,
    FaProjectDiagram,
    FaExclamationTriangle,
} from "react-icons/fa";
import type { TaskDetail } from "./work-types";
import { formatMinutes, formatDate, statusColor } from "./work-utils";

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
                                {task.doc_sub_type && (
                                    <Badge size="sm" variant="outline" colorPalette="gray">
                                        {task.doc_sub_type}
                                    </Badge>
                                )}
                                <Badge
                                    size="sm"
                                    colorPalette={statusColor(task.status)}
                                    variant="solid"
                                >
                                    {task.status || "No status"}
                                </Badge>
                            </HStack>
                            <Text fontWeight="semibold" fontSize="sm">
                                {task.title || "Untitled Task"}
                            </Text>

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
                                <DetailRow icon={<FaExclamationTriangle size={10} />} label="Priority">
                                    <Text fontSize="xs">{task.importance_for_next_release || "—"}</Text>
                                </DetailRow>
                                <DetailRow icon={<FaCalendarAlt size={10} />} label="Start">
                                    <Text fontSize="xs">{formatDate(task.estimated_start_date)}</Text>
                                </DetailRow>
                                <DetailRow icon={<FaCalendarAlt size={10} />} label="End">
                                    <Text fontSize="xs">{formatDate(task.estimated_end_date)}</Text>
                                </DetailRow>
                                <DetailRow icon={<FaCalendarAlt size={10} />} label="Completion">
                                    <Text fontSize="xs">{formatDate(task.estimated_completion_date)}</Text>
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
