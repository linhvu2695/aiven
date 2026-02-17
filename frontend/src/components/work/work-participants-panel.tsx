import { Box, VStack, HStack, Text, Spinner, Badge } from "@chakra-ui/react";
import { useMemo } from "react";
import { useChart } from "@chakra-ui/charts";
import { formatMinutes, ACCENT_COLOR } from "./work-utils";
import { DonutChart } from "@/components/ui/donut-chart";
import { useColorModeValue } from "../ui/color-mode";
import { useWorkContext } from "@/context/work-ctx";

interface ParticipantStats {
    name: string;
    taskCount: number;
    completedCount: number;
    timeSpent: number;
    timeLeft: number;
}

/** Chakra color tokens used for per-assignee colouring */
const ASSIGNEE_COLORS: Array<`${string}.${string}`> = [
    "teal.400",
    "blue.400",
    "purple.400",
    "orange.400",
    "cyan.400",
    "pink.400",
    "yellow.400",
    "red.400",
    "green.400",
    "gray.400",
    "teal.600",
    "blue.600",
    "purple.600",
    "orange.600",
    "cyan.600",
    "pink.600",
    "yellow.600",
    "red.600",
    "green.600",
    "gray.600",
];

export const WorkParticipantsPanel = () => {
    const { selectedRootTask: rootTask, selectedDescendants: descendants, isLoadingTree: isLoading } = useWorkContext();
    const accentColor = useColorModeValue(ACCENT_COLOR.light, ACCENT_COLOR.dark);

    const allTasks = useMemo(() => {
        if (!rootTask) return [];
        return [rootTask, ...descendants].filter(
            (t) => !t.status.toLowerCase().includes("obsolete")
        );
    }, [rootTask, descendants]);

    // Build stats per assignee
    const participants = useMemo(() => {
        const map = new Map<string, ParticipantStats>();

        for (const t of allTasks) {
            const name = t.assigned_to || "Unassigned";
            let stats = map.get(name);
            if (!stats) {
                stats = { name, taskCount: 0, completedCount: 0, timeSpent: 0, timeLeft: 0 };
                map.set(name, stats);
            }
            stats.taskCount++;
            stats.timeSpent += t.time_spent_mn;
            stats.timeLeft += t.time_left_mn;
            const sl = t.status.toLowerCase();
            if (
                sl.includes("done") ||
                sl.includes("completed") ||
                sl.includes("implemented") ||
                sl.includes("closed")
            ) {
                stats.completedCount++;
            }
        }

        return Array.from(map.values()).sort((a, b) => b.timeSpent - a.timeSpent);
    }, [allTasks]);

    const totalSpent = useMemo(() => participants.reduce((s, p) => s + p.timeSpent, 0), [participants]);
    const totalLeft = useMemo(() => participants.reduce((s, p) => s + p.timeLeft, 0), [participants]);
    const totalTasks = useMemo(() => participants.reduce((s, p) => s + p.taskCount, 0), [participants]);
    const maxIndividualTotal = useMemo(
        () => Math.max(...participants.map((p) => p.timeSpent + p.timeLeft), 1),
        [participants]
    );

    // Assign a stable color to each participant (by sorted order)
    const participantColors = useMemo(
        () => participants.map((_, i) => ASSIGNEE_COLORS[i % ASSIGNEE_COLORS.length]),
        [participants]
    );

    // Pie chart data — time spent per assignee
    const pieDataSpent = useMemo(
        () =>
            participants
                .map((p, i) => ({ name: p.name, value: p.timeSpent, label: formatMinutes(p.timeSpent), color: participantColors[i] }))
                .filter((d) => d.value > 0),
        [participants, participantColors]
    );

    // Pie chart data — time remaining per assignee
    const pieDataLeft = useMemo(
        () =>
            participants
                .map((p, i) => ({ name: p.name, value: p.timeLeft, label: formatMinutes(p.timeLeft), color: participantColors[i] }))
                .filter((d) => d.value > 0),
        [participants, participantColors]
    );

    const chartSpent = useChart({
        data: pieDataSpent,
        series: pieDataSpent.map((d) => ({ name: "value" as const, color: d.color })),
    });

    const chartLeft = useChart({
        data: pieDataLeft,
        series: pieDataLeft.map((d) => ({ name: "value" as const, color: d.color })),
    });

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
                    Select a task to view participant statistics.
                </Text>
            </Box>
        );
    }

    return (
        <Box w="100%" h="100%" display="flex" flexDirection="column" overflow="hidden">
            {/* Header */}
            <Box px={4} py={3} borderBottomWidth="1px" borderColor="border.default" flexShrink={0}>
                <Text fontWeight="bold" fontSize="md" truncate>
                    Participants — {rootTask.title || rootTask.identifier}
                </Text>
            </Box>

            {/* Scrollable content */}
            <Box flex={1} overflowY="auto" px={4} py={4}>
                <VStack gap={6} align="stretch">
                    {/* Summary cards */}
                    <HStack gap={4} wrap="wrap">
                        <SummaryCard label="Participants" value={String(participants.length)} />
                        <SummaryCard label="Tasks" value={String(totalTasks)} />
                        <SummaryCard label="Time spent" value={formatMinutes(totalSpent)} color={accentColor} />
                        <SummaryCard label="Time remaining" value={formatMinutes(totalLeft)} />
                        <SummaryCard
                            label="Completion"
                            value={totalSpent + totalLeft > 0
                                ? `${Math.round((totalSpent / (totalSpent + totalLeft)) * 100)}%`
                                : "—"
                            }
                            color={accentColor}
                        />
                    </HStack>

                    {/* Workload distribution donut charts */}
                    {(totalSpent > 0 || totalLeft > 0) && (
                        <Box>
                            <HStack gap={8} align="center">
                                {/* Time spent donut */}
                                {totalSpent > 0 && (
                                    <DonutChart
                                        data={pieDataSpent}
                                        chartHook={chartSpent}
                                        total={totalSpent}
                                        centerLabel={formatMinutes(totalSpent)}
                                        centerSublabel="spent"
                                    />
                                )}

                                {/* Time remaining donut */}
                                {totalLeft > 0 && (
                                    <DonutChart
                                        data={pieDataLeft}
                                        chartHook={chartLeft}
                                        total={totalLeft}
                                        centerLabel={formatMinutes(totalLeft)}
                                        centerSublabel="remaining"
                                    />
                                )}

                                {/* Single shared legend */}
                                <VStack gap={1} align="flex-start">
                                    {participants.map((p, i) => (
                                        <HStack key={p.name} gap={2}>
                                            <Box
                                                w="10px"
                                                h="10px"
                                                borderRadius="sm"
                                                bg={participantColors[i]}
                                                flexShrink={0}
                                            />
                                            <Text fontSize="xs" color="fg.muted">
                                                {p.name}
                                            </Text>
                                        </HStack>
                                    ))}
                                </VStack>
                            </HStack>
                        </Box>
                    )}

                    {/* Per-assignee breakdown */}
                    <Box>
                        <Text fontSize="sm" fontWeight="semibold" mb={3}>
                            Per-assignee breakdown
                        </Text>
                        <VStack gap={3} align="stretch">
                            {participants.map((p, i) => {
                                const pTotal = p.timeSpent + p.timeLeft;
                                const pctComplete = pTotal > 0 ? (p.timeSpent / pTotal) * 100 : 0;
                                const barW = Math.max((pTotal / maxIndividualTotal) * 100, 2);

                                return (
                                    <Box
                                        key={p.name}
                                        p={3}
                                        borderWidth="1px"
                                        borderColor="border.default"
                                        borderRadius="md"
                                    >
                                        {/* Name row */}
                                        <HStack justify="space-between" mb={2}>
                                            <HStack gap={2}>
                                                <Box
                                                    w="10px"
                                                    h="10px"
                                                    borderRadius="full"
                                                    bg={ASSIGNEE_COLORS[i % ASSIGNEE_COLORS.length]}
                                                    flexShrink={0}
                                                />
                                                <Text fontSize="sm" fontWeight="medium">
                                                    {p.name}
                                                </Text>
                                            </HStack>
                                            <HStack gap={2}>
                                                <Badge size="sm" variant="subtle" colorPalette="gray">
                                                    {p.taskCount} task{p.taskCount !== 1 ? "s" : ""}
                                                </Badge>
                                                <Badge size="sm" variant="subtle" colorPalette="green">
                                                    {p.completedCount} done
                                                </Badge>
                                            </HStack>
                                        </HStack>

                                        {/* Time stats */}
                                        <HStack gap={4} mb={2} fontSize="xs" color="fg.muted">
                                            <Text>
                                                Spent: <Text as="span" color={accentColor} fontWeight="bold">{formatMinutes(p.timeSpent)}</Text>
                                            </Text>
                                            <Text>
                                                Remaining: <Text as="span" fontWeight="bold">{formatMinutes(p.timeLeft)}</Text>
                                            </Text>
                                            <Text>
                                                Total: <Text as="span" fontWeight="bold">{formatMinutes(pTotal)}</Text>
                                            </Text>
                                            <Text>
                                                Completion: <Text as="span" color={accentColor} fontWeight="bold">{Math.round(pctComplete)}%</Text>
                                            </Text>
                                        </HStack>

                                        {/* Stacked bar */}
                                        {pTotal > 0 && (
                                            <Box
                                                w={`${barW}%`}
                                                h="10px"
                                                borderRadius="full"
                                                bg="gray.600"
                                                overflow="hidden"
                                            >
                                                <Box
                                                    h="full"
                                                    w={`${pctComplete}%`}
                                                    borderRadius="full"
                                                    bg={accentColor}
                                                    transition="width 0.3s"
                                                />
                                            </Box>
                                        )}
                                    </Box>
                                );
                            })}
                        </VStack>
                    </Box>
                </VStack>
            </Box>
        </Box>
    );
};

/** Small summary card */
const SummaryCard = ({
    label,
    value,
    color,
}: {
    label: string;
    value: string;
    color?: string;
}) => (
    <Box px={4} py={3} borderWidth="1px" borderColor="border.default" borderRadius="md" minW="120px">
        <Text fontSize="xs" color="fg.muted" mb={1}>
            {label}
        </Text>
        <Text fontSize="lg" fontWeight="bold" color={color}>
            {value}
        </Text>
    </Box>
);
