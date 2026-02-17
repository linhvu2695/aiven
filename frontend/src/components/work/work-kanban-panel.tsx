import {
    Box,
    VStack,
    HStack,
    Text,
    Badge,
    Link,
    Spinner,
} from "@chakra-ui/react";
import { useMemo } from "react";
import type { TaskDetail } from "./work-types";
import {
    statusColor,
    docSubTypeIcon,
    formatMinutes,
    ACCENT_COLOR,
    KANBAN_COLUMNS,
} from "./work-utils";
import { useColorModeValue } from "../ui/color-mode";
import { useWorkContext } from "@/context/work-ctx";

export const WorkKanbanPanel = () => {
    const { selectedRootTask: rootTask, selectedDescendants: descendants, isLoadingTree: isLoading } = useWorkContext();
    const accentColor = useColorModeValue(ACCENT_COLOR.light, ACCENT_COLOR.dark);

    // All tasks except root (root is shown as header)
    const allTasks = useMemo(() => {
        if (!rootTask) return [];
        return descendants;
    }, [rootTask, descendants]);

    // Group tasks into columns by status
    const columns = useMemo(() => {
        const grouped: Record<string, TaskDetail[]> = {};
        for (const col of KANBAN_COLUMNS) {
            grouped[col.id] = [];
        }
        grouped["other"] = [];

        for (const task of allTasks) {
            const sl = task.status.toLowerCase();
            let placed = false;
            for (const col of KANBAN_COLUMNS) {
                if (col.match(sl)) {
                    grouped[col.id].push(task);
                    placed = true;
                    break;
                }
            }
            if (!placed) {
                grouped["other"].push(task);
            }
        }

        return grouped;
    }, [allTasks]);

    if (isLoading) {
        return (
            <VStack justify="center" align="center" h="200px">
                <Spinner size="lg" />
                <Text fontSize="sm" color="fg.muted">Loading tasks...</Text>
            </VStack>
        );
    }

    if (!rootTask) {
        return (
            <Box p={4} textAlign="center">
                <Text color="fg.muted" fontSize="sm">
                    Select a task to view its Kanban board.
                </Text>
            </Box>
        );
    }

    // Columns to render (KANBAN_COLUMNS + "other" if it has items)
    const visibleColumns = [
        ...KANBAN_COLUMNS.map((col) => ({
            ...col,
            tasks: columns[col.id],
        })),
        ...(columns["other"].length > 0
            ? [{ id: "other", label: "Other", colorPalette: "gray", match: () => false, tasks: columns["other"] }]
            : []),
    ];

    return (
        <Box w="100%" h="100%" display="flex" flexDirection="column" overflow="hidden">
            {/* Header */}
            <Box px={4} py={3} borderBottomWidth="1px" borderColor="border.default" flexShrink={0}>
                <Text fontWeight="bold" fontSize="md" truncate>
                    Kanban — {rootTask.title || rootTask.identifier}
                </Text>
            </Box>

            {/* Board */}
            <HStack
                flex={1}
                overflowX="auto"
                overflowY="hidden"
                gap={4}
                px={4}
                py={4}
                align="stretch"
            >
                {visibleColumns.map((col) => (
                    <Box
                        key={col.id}
                        minW="280px"
                        w="280px"
                        flexShrink={0}
                        display="flex"
                        flexDirection="column"
                        borderWidth="1px"
                        borderColor="border.default"
                        borderRadius="lg"
                        overflow="hidden"
                        bg="bg.subtle"
                    >
                        {/* Column header */}
                        <HStack
                            px={3}
                            py={2}
                            borderBottomWidth="1px"
                            borderColor="border.default"
                            gap={2}
                            flexShrink={0}
                        >
                            <Badge colorPalette={col.colorPalette} variant="subtle" size="sm">
                                {col.label}
                            </Badge>
                            <Text fontSize="xs" color="fg.muted">
                                {col.tasks.length}
                            </Text>
                        </HStack>

                        {/* Cards */}
                        <VStack
                            flex={1}
                            overflowY="auto"
                            gap={2}
                            p={2}
                            align="stretch"
                        >
                            {col.tasks.length === 0 && (
                                <Text fontSize="xs" color="fg.subtle" textAlign="center" py={4}>
                                    No tasks
                                </Text>
                            )}
                            {col.tasks.map((task) => (
                                <KanbanCard
                                    key={task.identifier}
                                    task={task}
                                    accentColor={accentColor}
                                />
                            ))}
                        </VStack>
                    </Box>
                ))}
            </HStack>
        </Box>
    );
};

/* ------------------------------------------------------------------ */
/*  Kanban Card                                                        */
/* ------------------------------------------------------------------ */

const KanbanCard = ({
    task,
    accentColor,
}: {
    task: TaskDetail;
    accentColor: string;
}) => {
    const obsolete = task.status.toLowerCase().includes("obsolete");
    const spent = task.time_spent_mn;
    const total = spent + task.time_left_mn;
    const pct = total > 0 ? (spent / total) * 100 : 0;
    const completed = task.time_left_mn === 0 && spent > 0;

    const { icon: docIcon, color: docIconColor } = docSubTypeIcon(task.doc_sub_type);

    return (
        <Box
            p={3}
            borderWidth="1px"
            borderColor="border.default"
            borderRadius="md"
            bg="bg.panel"
            _hover={{ shadow: "md", borderColor: "border.emphasized" }}
            transition="all 0.15s"
            opacity={obsolete ? 0.5 : 1}
        >
            {/* Title row */}
            <HStack gap={2} mb={1}>
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
                        fontSize="sm"
                        fontWeight="medium"
                        lineClamp={2}
                        _hover={{ textDecoration: "underline" }}
                        color={obsolete ? "fg.subtle" : undefined}
                    >
                        {task.title || task.identifier}
                    </Link>
                ) : (
                    <Text
                        fontSize="sm"
                        fontWeight="medium"
                        lineClamp={2}
                        color={obsolete ? "fg.subtle" : undefined}
                    >
                        {task.title || task.identifier}
                    </Text>
                )}
            </HStack>

            {/* Identifier + Status */}
            <HStack gap={2} mb={2}>
                <Badge size="sm" variant="outline" colorPalette="gray">
                    {task.identifier}
                </Badge>
                <Badge size="sm" variant="subtle" colorPalette={statusColor(task.status)}>
                    {task.status}
                </Badge>
            </HStack>

            {/* Progress bar (if not obsolete and has time) */}
            {!obsolete && total > 0 && (
                <Box mb={2}>
                    <Box
                        h="6px"
                        borderRadius="full"
                        bg="gray.600"
                        overflow="hidden"
                    >
                        <Box
                            h="full"
                            w={`${pct}%`}
                            borderRadius="full"
                            bg={accentColor}
                            transition="width 0.3s"
                        />
                    </Box>
                    <Text fontSize="2xs" color="fg.muted" mt={0.5}>
                        {completed ? (
                            <Text as="span" color={accentColor} fontWeight="bold">
                                {formatMinutes(total)}
                            </Text>
                        ) : (
                            <>
                                <Text as="span" color={accentColor}>{formatMinutes(spent)}</Text>
                                {" / "}
                                {formatMinutes(total)}
                            </>
                        )}
                    </Text>
                </Box>
            )}

            {/* Assignee */}
            {task.assigned_to && (
                <Text
                    fontSize="xs"
                    color={completed ? accentColor : "fg.muted"}
                    truncate
                >
                    {task.assigned_to}
                </Text>
            )}
        </Box>
    );
};
