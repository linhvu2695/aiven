import {
    Box,
    HStack,
    IconButton,
    VStack,
    Text,
    Badge,
    Spinner,
} from "@chakra-ui/react";
import { useMemo, useRef, useState, useCallback } from "react";
import { FaChevronRight, FaChevronDown } from "react-icons/fa";
import type { TaskDetail } from "./work-types";
import { statusColor, docSubTypeIcon, formatDate, ACCENT_COLOR, DEFAULT_DOC_SUB_TYPE_FILTER } from "./work-utils";
import { useColorModeValue } from "../ui/color-mode";
import { useWorkContext } from "@/context/work-ctx";
import { WorkTaskDetailPopover } from "./work-task-detail-popover";
import { WorkTaskFilter } from "./work-task-filter";

const ROW_HEIGHT = 36;
const LABEL_WIDTH = 360;
const DAY_WIDTH = 28;
const MONTH_ROW_HEIGHT = 24;
const DAY_ROW_HEIGHT = 24;
const HEADER_HEIGHT = MONTH_ROW_HEIGHT + DAY_ROW_HEIGHT;
const INDENT_PX = 20;

const parseDate = (value: string | null): Date | null => {
    if (!value) return null;
    const d = new Date(value);
    return isNaN(d.getTime()) ? null : d;
};

const daysBetween = (a: Date, b: Date): number =>
    Math.round((b.getTime() - a.getTime()) / (1000 * 60 * 60 * 24));

const addDays = (d: Date, n: number): Date => {
    const r = new Date(d);
    r.setDate(r.getDate() + n);
    return r;
};

interface FlatGanttRow {
    task: TaskDetail;
    level: number;
    hasChildren: boolean;
    start: Date | null;
    end: Date | null;
}

const getTaskDates = (task: TaskDetail): { start: Date | null; end: Date | null } => ({
    start: parseDate(task.estimated_start_date),
    end: parseDate(task.estimated_end_date) ?? parseDate(task.estimated_completion_date),
});

/**
 * Flatten the task tree into a depth-first ordered list,
 * respecting collapsed state. Returns rows that should be visible.
 */
const flattenTree = (
    allTasks: TaskDetail[],
    parentId: string,
    level: number,
    collapsed: Set<string>,
): FlatGanttRow[] => {
    const children = allTasks.filter((t) => t.parent_folder_identifier === parentId);
    const rows: FlatGanttRow[] = [];
    for (const child of children) {
        const grandchildren = allTasks.filter((t) => t.parent_folder_identifier === child.identifier);
        const hasChildren = grandchildren.length > 0;
        const { start, end } = getTaskDates(child);
        rows.push({
            task: child,
            level,
            hasChildren,
            start,
            end,
        });
        if (hasChildren && !collapsed.has(child.identifier)) {
            rows.push(...flattenTree(allTasks, child.identifier, level + 1, collapsed));
        }
    }
    return rows;
};

export const WorkGanttPanel = () => {
    const { selectedRootTask: rootTask, selectedDescendants: descendants, isLoadingTree: isLoading } = useWorkContext();
    const accentColor = useColorModeValue(ACCENT_COLOR.light, ACCENT_COLOR.dark);
    const timelineRef = useRef<HTMLDivElement>(null);

    // Track which nodes are collapsed
    const [collapsed, setCollapsed] = useState<Set<string>>(() => {
        const initial = new Set<string>();
        for (const t of descendants) {
            const s = t.status.toLowerCase();
            if (s.includes("obsolete") || s.includes("blocked")) {
                initial.add(t.identifier);
            }
        }
        return initial;
    });

    const toggleCollapse = useCallback((id: string) => {
        setCollapsed((prev) => {
            const next = new Set(prev);
            if (next.has(id)) {
                next.delete(id);
            } else {
                next.add(id);
            }
            return next;
        });
    }, []);

    const [activeFilters, setActiveFilters] = useState<Set<string>>(
        () => new Set(DEFAULT_DOC_SUB_TYPE_FILTER)
    );

    const allTasks = useMemo(() => {
        if (!rootTask) return [];
        const nonObsolete = [rootTask, ...descendants].filter(
            (t) => !t.status.toLowerCase().includes("obsolete")
        );

        if (activeFilters.size === 0) return nonObsolete;

        // Find tasks matching the filter
        const matchingIds = new Set<string>();
        for (const t of nonObsolete) {
            const typeLower = t.doc_sub_type.toLowerCase();
            for (const filter of activeFilters) {
                if (typeLower.includes(filter.toLowerCase())) {
                    matchingIds.add(t.identifier);
                    break;
                }
            }
        }

        // Include ancestors to preserve tree structure
        const includedIds = new Set(matchingIds);
        const taskMap = new Map(nonObsolete.map((t) => [t.identifier, t]));
        for (const id of matchingIds) {
            let current = taskMap.get(id);
            while (current && current.parent_folder_identifier) {
                if (includedIds.has(current.parent_folder_identifier)) break;
                includedIds.add(current.parent_folder_identifier);
                current = taskMap.get(current.parent_folder_identifier);
            }
        }

        return nonObsolete.filter((t) => includedIds.has(t.identifier));
    }, [rootTask, descendants, activeFilters]);

    // Build the root row + flattened children
    const visibleRows = useMemo((): FlatGanttRow[] => {
        if (!rootTask) return [];
        const rootChildren = allTasks.filter((t) => t.parent_folder_identifier === rootTask.identifier);
        const { start: rootStart, end: rootEnd } = getTaskDates(rootTask);
        const rootRow: FlatGanttRow = {
            task: rootTask,
            level: 0,
            hasChildren: rootChildren.length > 0,
            start: rootStart,
            end: rootEnd,
        };
        if (collapsed.has(rootTask.identifier)) {
            return [rootRow];
        }
        return [rootRow, ...flattenTree(allTasks, rootTask.identifier, 1, collapsed)];
    }, [rootTask, allTasks, collapsed]);

    // Compute timeline range from ALL tasks so collapsing doesn't shift the chart
    const { timelineStart, totalDays, months, days } = useMemo(() => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const allDates: Date[] = [];
        for (const t of allTasks) {
            const { start: s, end: e } = getTaskDates(t);
            if (s) allDates.push(s);
            if (e) allDates.push(e);
        }
        if (allDates.length === 0) allDates.push(today);

        const minDate = new Date(Math.min(...allDates.map((d) => d.getTime())));
        const maxDate = new Date(Math.max(...allDates.map((d) => d.getTime()), today.getTime()));

        const start = addDays(minDate, -7);
        start.setHours(0, 0, 0, 0);
        const end = addDays(maxDate, 14);
        const totalDays = daysBetween(start, end);

        // Build month markers
        const monthMarkers: { label: string; offsetDays: number; widthDays: number }[] = [];
        const cursor = new Date(start.getFullYear(), start.getMonth(), 1);
        while (cursor <= end) {
            const monthStart = new Date(cursor);
            const nextMonth = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1);
            const offsetDays = Math.max(0, daysBetween(start, monthStart));
            const endDay = Math.min(totalDays, daysBetween(start, nextMonth));
            monthMarkers.push({
                label: monthStart.toLocaleDateString(undefined, { month: "short", year: "numeric" }),
                offsetDays,
                widthDays: endDay - offsetDays,
            });
            cursor.setMonth(cursor.getMonth() + 1);
        }

        // Build day markers
        const todayTime = today.getTime();
        const dayMarkers: { label: string; offset: number; isWeekend: boolean; isMonday: boolean; isToday: boolean }[] = [];
        for (let i = 0; i < totalDays; i++) {
            const d = addDays(start, i);
            const dow = d.getDay();
            dayMarkers.push({
                label: String(d.getDate()),
                offset: i,
                isWeekend: dow === 0 || dow === 6,
                isMonday: dow === 1,
                isToday: d.getTime() === todayTime,
            });
        }

        return { timelineStart: start, totalDays, months: monthMarkers, days: dayMarkers };
    }, [allTasks]);

    const todayOffset = useMemo(() => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return daysBetween(timelineStart, today);
    }, [timelineStart]);

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
                <Text color="fg.muted" fontSize="sm">No tasks found. Enter a task ID to search.</Text>
            </Box>
        );
    }

    const timelineWidth = totalDays * DAY_WIDTH;

    return (
        <Box w="100%" h="100%" display="flex" flexDirection="column" overflow="hidden">
            {/* Header */}
            <HStack px={4} py={3} borderBottomWidth="1px" borderColor="border.default" flexShrink={0} gap={2}>
                <Text fontWeight="bold" fontSize="md" truncate flex={1}>
                    Gantt Chart — {rootTask.title || rootTask.identifier}
                </Text>
                <WorkTaskFilter activeFilters={activeFilters} onFilterChange={setActiveFilters} />
            </HStack>

            {/* Timeline header: months + days */}
            <HStack gap={0} flexShrink={0} borderBottomWidth="1px" borderColor="border.default" bg="bg.subtle">
                <Box w={`${LABEL_WIDTH}px`} flexShrink={0} h={`${HEADER_HEIGHT}px`} px={3} display="flex" alignItems="center">
                    <Text fontSize="xs" fontWeight="semibold" color="fg.muted">Task</Text>
                </Box>
                <Box flex={1} overflow="hidden">
                    <Box
                        w={`${timelineWidth}px`}
                        h={`${HEADER_HEIGHT}px`}
                        position="relative"
                        ref={timelineRef}
                    >
                        {/* Month row */}
                        {months.map((m) => (
                            <Box
                                key={m.label}
                                position="absolute"
                                left={`${m.offsetDays * DAY_WIDTH}px`}
                                w={`${m.widthDays * DAY_WIDTH}px`}
                                h={`${MONTH_ROW_HEIGHT}px`}
                                top={0}
                                borderRightWidth="1px"
                                borderBottomWidth="1px"
                                borderColor="border.default"
                                display="flex"
                                alignItems="center"
                                px={2}
                            >
                                <Text fontSize="2xs" fontWeight="medium" color="fg.muted" whiteSpace="nowrap">
                                    {m.label}
                                </Text>
                            </Box>
                        ))}
                        {/* Day row */}
                        {days.map((d) => (
                            <Box
                                key={d.offset}
                                position="absolute"
                                left={`${d.offset * DAY_WIDTH}px`}
                                w={`${DAY_WIDTH}px`}
                                h={`${DAY_ROW_HEIGHT}px`}
                                top={`${MONTH_ROW_HEIGHT}px`}
                                borderRightWidth="1px"
                                borderColor={d.isMonday ? "border.default" : "border.muted"}
                                display="flex"
                                alignItems="center"
                                justifyContent="center"
                                bg={d.isToday ? "red.500" : d.isWeekend ? { base: "gray.100", _dark: "gray.800" } : undefined}
                            >
                                <Text
                                    fontSize="2xs"
                                    color={d.isToday ? "white" : d.isWeekend ? "fg.subtle" : "fg.muted"}
                                    fontWeight={d.isToday || d.isMonday ? "semibold" : undefined}
                                >
                                    {d.label}
                                </Text>
                            </Box>
                        ))}
                    </Box>
                </Box>
            </HStack>

            {/* Body: labels + timeline rows */}
            <HStack gap={0} flex={1} overflow="hidden" align="start">
                {/* Left: task labels */}
                <Box
                    w={`${LABEL_WIDTH}px`}
                    flexShrink={0}
                    overflowY="auto"
                    overflowX="scroll"
                    borderRightWidth="1px"
                    borderColor="border.default"
                    h="100%"
                    onScroll={(e) => {
                        const target = e.currentTarget;
                        const timeline = target.nextElementSibling;
                        if (timeline) timeline.scrollTop = target.scrollTop;
                    }}
                >
                    {visibleRows.map((row) => {
                        const { icon, color } = docSubTypeIcon(row.task.doc_sub_type);
                        const isRoot = row.level === 0;
                        return (
                            <HStack
                                key={row.task.identifier}
                                h={`${ROW_HEIGHT}px`}
                                gap={1}
                                borderBottomWidth="1px"
                                borderColor="border.default"
                                bg={isRoot ? "bg.subtle" : undefined}
                                _hover={{
                                    bg: { base: "gray.50", _dark: "gray.900" },
                                    "& .view-button": { opacity: 1 },
                                }}
                                style={{ paddingLeft: `${row.level * INDENT_PX + 8}px`, paddingRight: "8px" }}
                            >
                                {/* Collapse toggle */}
                                <Box w="18px" flexShrink={0}>
                                    {row.hasChildren && (
                                        <IconButton
                                            aria-label="Toggle children"
                                            variant="ghost"
                                            size="2xs"
                                            onClick={() => toggleCollapse(row.task.identifier)}
                                        >
                                            {collapsed.has(row.task.identifier) ? <FaChevronRight size={10} /> : <FaChevronDown size={10} />}
                                        </IconButton>
                                    )}
                                </Box>
                                {icon && (
                                    <Box color={color} flexShrink={0}>{icon}</Box>
                                )}
                                <Text
                                    fontSize="xs"
                                    fontWeight={isRoot ? "semibold" : undefined}
                                    truncate
                                    flex={1}
                                >
                                    {row.task.title || row.task.identifier}
                                </Text>
                                <Badge size="sm" colorPalette={statusColor(row.task.status)} variant="subtle" flexShrink={0}>
                                    {row.task.status || "—"}
                                </Badge>
                                <WorkTaskDetailPopover task={row.task} />
                            </HStack>
                        );
                    })}
                </Box>

                {/* Right: timeline bars */}
                <Box
                    flex={1}
                    overflow="auto"
                    h="100%"
                    onScroll={(e) => {
                        const target = e.currentTarget;
                        const labels = target.previousElementSibling;
                        if (labels) labels.scrollTop = target.scrollTop;
                        const headerTimeline = timelineRef.current;
                        if (headerTimeline?.parentElement) {
                            headerTimeline.parentElement.scrollLeft = target.scrollLeft;
                        }
                    }}
                >
                    <Box w={`${timelineWidth}px`} position="relative">
                        {/* Today marker */}
                        <Box
                            position="absolute"
                            left={`${todayOffset * DAY_WIDTH}px`}
                            top={0}
                            w="2px"
                            bg="red.400"
                            zIndex={2}
                            h={`${visibleRows.length * ROW_HEIGHT}px`}
                        />

                        {/* Task bars */}
                        {visibleRows.map((row) => {
                            const hasBar = row.start && row.end;
                            const startOffset = row.start ? daysBetween(timelineStart, row.start) : 0;
                            const duration = row.start && row.end ? Math.max(daysBetween(row.start, row.end), 1) : 0;
                            const barColor = statusColor(row.task.status);
                            const isRoot = row.level === 0;

                            return (
                                <Box
                                    key={row.task.identifier}
                                    position="relative"
                                    h={`${ROW_HEIGHT}px`}
                                    borderBottomWidth="1px"
                                    borderColor="border.default"
                                    bg={isRoot ? "bg.subtle" : undefined}
                                >
                                    {hasBar && (
                                        <Box
                                            position="absolute"
                                            top="6px"
                                            left={`${startOffset * DAY_WIDTH}px`}
                                            w={`${duration * DAY_WIDTH}px`}
                                            h={`${ROW_HEIGHT - 12}px`}
                                            bg={`${barColor}.400`}
                                            opacity={isRoot ? 1 : 0.85}
                                            borderRadius="sm"
                                            display="flex"
                                            alignItems="center"
                                            px={1}
                                            overflow="visible"
                                            title={`${row.task.identifier}: ${formatDate(row.task.estimated_start_date)} → ${formatDate(row.task.estimated_end_date)}`}
                                        >
                                            {row.task.assigned_to && (
                                                <Text fontSize="2xs" color={{ base: "gray.900", _dark: "white" }} fontWeight="medium" whiteSpace="nowrap">
                                                    {row.task.assigned_to}
                                                </Text>
                                            )}
                                        </Box>
                                    )}
                                    {!hasBar && (
                                        <Box
                                            position="absolute"
                                            top={`${ROW_HEIGHT / 2 - 3}px`}
                                            left={`${todayOffset * DAY_WIDTH - 3}px`}
                                            w="6px"
                                            h="6px"
                                            borderRadius="full"
                                            bg="gray.400"
                                            title="No date info"
                                        />
                                    )}
                                </Box>
                            );
                        })}
                    </Box>
                </Box>
            </HStack>
        </Box>
    );
};
