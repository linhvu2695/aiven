import {
    Box,
    VStack,
    HStack,
    Text,
    Spinner,
    IconButton,
    Badge,
    CloseButton,
    Link,
} from "@chakra-ui/react";
import { useMemo } from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as ReTooltip,
    Cell,
    ResponsiveContainer,
} from "recharts";
import { Chart, useChart } from "@chakra-ui/charts";
import { FaSyncAlt } from "react-icons/fa";
import { Tooltip } from "@/components/ui/tooltip";
import { formatMinutes, ACCENT_COLOR, docSubTypeIcon, statusColor } from "@/components/work/work-utils";
import { SummaryCard } from "@/components/ui/summary-card";
import { useColorModeValue } from "@/components/ui/color-mode";
import { useTeamContext } from "@/context/team-ctx";
import { WorkTaskProgressBar } from "@/components/work/work-task-progress-bar";
import type { MemberWorkload } from "./team-types";
import { MEMBER_COLORS } from "./team-types";

interface TeamWorkloadContentProps {
    workload: MemberWorkload[];
    loading: boolean;
    onRefresh: () => void;
}

export const TeamWorkloadContent = ({
    workload,
    loading,
    onRefresh,
}: TeamWorkloadContentProps) => {
    const { selectedMember, setSelectedMember } = useTeamContext();
    const accentColor = useColorModeValue(ACCENT_COLOR.light, ACCENT_COLOR.dark);

    const selectedMemberData = useMemo(
        () => (selectedMember ? workload.find((m) => m.name === selectedMember) : null),
        [selectedMember, workload]
    );

    const selectedMemberColor = useMemo(() => {
        if (!selectedMemberData) return null;
        const idx = workload.findIndex((m) => m.name === selectedMemberData.name);
        return idx >= 0 ? MEMBER_COLORS[idx % MEMBER_COLORS.length] : null;
    }, [selectedMemberData, workload]);

    const selectedMemberBg = useColorModeValue(
        selectedMemberColor ? selectedMemberColor.replace(/\.\d+$/, ".100") : "gray.100",
        selectedMemberColor ? selectedMemberColor.replace(/\.\d+$/, ".800") : "gray.800"
    );

    const chartDataRemaining = useMemo(
        () =>
            workload.map((m, i) => ({
                name: m.name.split(" ")[0],
                fullName: m.name,
                value: Math.round((m.time_left_mn / 60) * 10) / 10,
                rawMinutes: m.time_left_mn,
                color: MEMBER_COLORS[i % MEMBER_COLORS.length],
            })),
        [workload]
    );

    const chartDataTaskCount = useMemo(
        () =>
            workload.map((m, i) => ({
                name: m.name.split(" ")[0],
                fullName: m.name,
                value: m.task_count,
                color: MEMBER_COLORS[i % MEMBER_COLORS.length],
            })),
        [workload]
    );

    const chartRemaining = useChart({
        data: chartDataRemaining,
        series: [{ name: "value" as const, color: "teal.400" }],
    });

    const chartTaskCount = useChart({
        data: chartDataTaskCount,
        series: [{ name: "value" as const, color: "teal.400" }],
    });

    if (loading) {
        return (
            <Box flex={1} display="flex" alignItems="center" justifyContent="center">
                <VStack gap={2}>
                    <Spinner size="lg" />
                    <Text fontSize="sm" color="fg.muted">
                        Loading team workload...
                    </Text>
                </VStack>
            </Box>
        );
    }

    const totalTasks = workload.reduce((s, m) => s + m.task_count, 0);
    const totalRemaining = workload.reduce((s, m) => s + m.time_left_mn, 0);
    const totalSpent = workload.reduce((s, m) => s + m.time_spent_mn, 0);

    const handleBarClick = (ev: unknown) => {
        const e = ev as { payload?: { fullName?: string }; fullName?: string };
        const name = e?.payload?.fullName ?? e?.fullName;
        if (name) setSelectedMember(selectedMember === name ? null : name);
    };

    return (
        <Box flex={1} overflowY="auto" px={6} py={4}>
            <VStack gap={6} align="stretch">
                {/* Header */}
                <HStack gap={3}>
                    <Text fontWeight="bold" fontSize="xl">
                        Team Workload
                    </Text>
                    <Tooltip content="Refresh from Orange Logic">
                        <IconButton
                            aria-label="Force refresh"
                            variant="ghost"
                            size="xs"
                            onClick={onRefresh}
                            disabled={loading}
                        >
                            {loading ? <Spinner size="xs" /> : <FaSyncAlt />}
                        </IconButton>
                    </Tooltip>
                </HStack>

                {/* Summary cards */}
                <HStack gap={4} wrap="wrap">
                    <SummaryCard label="Members" value={String(workload.length)} />
                    <SummaryCard label="Tasks" value={String(totalTasks)} />
                    <SummaryCard label="Time spent" value={formatMinutes(totalSpent)} color={accentColor} />
                    <SummaryCard label="Time remaining" value={formatMinutes(totalRemaining)} />
                </HStack>

                {/* Charts */}
                <HStack gap={6} align="start">
                    <Box flex={1}>
                        <Text fontSize="sm" fontWeight="semibold" mb={2}>
                            Time Remaining (hours)
                        </Text>
                        <Chart.Root chart={chartRemaining}>
                            <ResponsiveContainer width="100%" height={200}>
                                <BarChart
                                    data={chartDataRemaining}
                                    margin={{ top: 5, right: 10, bottom: 5, left: -10 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                                    <XAxis dataKey="name" fontSize={11} />
                                    <YAxis fontSize={11} />
                                    <ReTooltip
                                        cursor={{ fill: "transparent" }}
                                        content={({ payload }) => {
                                            if (!payload?.length) return null;
                                            const d = payload[0].payload;
                                            return (
                                                <Box
                                                    bg="bg.panel"
                                                    borderWidth="1px"
                                                    borderColor="border.default"
                                                    borderRadius="md"
                                                    px={3}
                                                    py={2}
                                                    shadow="md"
                                                >
                                                    <Text fontSize="xs" fontWeight="bold">
                                                        {d.fullName}
                                                    </Text>
                                                    <Text fontSize="xs" color="fg.muted">
                                                        {formatMinutes(d.rawMinutes)} remaining
                                                    </Text>
                                                </Box>
                                            );
                                        }}
                                    />
                                    <Bar
                                        dataKey="value"
                                        radius={[4, 4, 0, 0]}
                                        cursor="pointer"
                                        onClick={handleBarClick}
                                    >
                                        {chartDataRemaining.map((entry) => (
                                            <Cell
                                                key={entry.fullName}
                                                fill={chartRemaining.color(entry.color)}
                                            />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </Chart.Root>
                    </Box>

                    <Box flex={1}>
                        <Text fontSize="sm" fontWeight="semibold" mb={2}>
                            Remaining Tasks
                        </Text>
                        <Chart.Root chart={chartTaskCount}>
                            <ResponsiveContainer width="100%" height={200}>
                                <BarChart
                                    data={chartDataTaskCount}
                                    margin={{ top: 5, right: 10, bottom: 5, left: -10 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                                    <XAxis dataKey="name" fontSize={11} />
                                    <YAxis fontSize={11} allowDecimals={false} />
                                    <ReTooltip
                                        cursor={{ fill: "transparent" }}
                                        content={({ payload }) => {
                                            if (!payload?.length) return null;
                                            const d = payload[0].payload;
                                            return (
                                                <Box
                                                    bg="bg.panel"
                                                    borderWidth="1px"
                                                    borderColor="border.default"
                                                    borderRadius="md"
                                                    px={3}
                                                    py={2}
                                                    shadow="md"
                                                >
                                                    <Text fontSize="xs" fontWeight="bold">
                                                        {d.fullName}
                                                    </Text>
                                                    <Text fontSize="xs" color="fg.muted">
                                                        {d.value} task{d.value !== 1 ? "s" : ""}
                                                    </Text>
                                                </Box>
                                            );
                                        }}
                                    />
                                    <Bar
                                        dataKey="value"
                                        radius={[4, 4, 0, 0]}
                                        cursor="pointer"
                                        onClick={handleBarClick}
                                    >
                                        {chartDataTaskCount.map((entry) => (
                                            <Cell
                                                key={entry.fullName}
                                                fill={chartTaskCount.color(entry.color)}
                                            />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </Chart.Root>
                    </Box>
                </HStack>

                {/* Task list for selected member */}
                {selectedMemberData && (
                    <Box
                        borderWidth="1px"
                        borderColor="border.default"
                        borderRadius="md"
                        overflow="hidden"
                        mt={2}
                    >
                        <HStack
                            justify="space-between"
                            px={4}
                            py={2}
                            bg={selectedMemberBg}
                            borderBottomWidth="1px"
                            borderColor="border.default"
                        >
                            <Text fontSize="sm" fontWeight="semibold">
                                {selectedMemberData.name} — {selectedMemberData.tasks.length} remaining task
                                {selectedMemberData.tasks.length !== 1 ? "s" : ""}
                            </Text>
                            <CloseButton size="sm" onClick={() => setSelectedMember(null)} />
                        </HStack>
                        <VStack align="stretch" gap={0} maxH="400px" overflowY="auto" p={2}>
                            {(() => {
                                const maxTime = Math.max(
                                    ...selectedMemberData.tasks.map(
                                        (t) => t.time_spent_mn + t.time_left_mn
                                    ),
                                    1
                                );
                                const sortedTasks = [...selectedMemberData.tasks].sort((a, b) => {
                                    const da = a.estimated_completion_date
                                        ? new Date(a.estimated_completion_date as string).getTime()
                                        : Infinity;
                                    const db = b.estimated_completion_date
                                        ? new Date(b.estimated_completion_date as string).getTime()
                                        : Infinity;
                                    return da - db;
                                });
                                return sortedTasks.map((task) => {
                                    const obsolete = (task.status || "")
                                        .toLowerCase()
                                        .includes("obsolete");
                                    const { icon, color } = docSubTypeIcon(task.doc_sub_type || "");
                                    return (
                                        <HStack
                                            key={task.identifier}
                                            p={2}
                                            gap={2}
                                            _hover={{
                                                bg: { base: "gray.100", _dark: "gray.800" },
                                            }}
                                            borderRadius="md"
                                        >
                                            {icon && (
                                                <Box color={color} flexShrink={0}>
                                                    {icon}
                                                </Box>
                                            )}
                                            <HStack flex={1} gap={2} overflow="hidden" minW={0}>
                                                {task.cortex_share_link ? (
                                                    <Link
                                                        href={task.cortex_share_link}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        fontSize="sm"
                                                        truncate
                                                        color={
                                                            obsolete ? "fg.subtle" : undefined
                                                        }
                                                        _hover={{ textDecoration: "underline" }}
                                                    >
                                                        {task.title || task.identifier}
                                                    </Link>
                                                ) : (
                                                    <Text
                                                        fontSize="sm"
                                                        truncate
                                                        color={
                                                            obsolete ? "fg.subtle" : undefined
                                                        }
                                                    >
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
                                            {!obsolete && (
                                                <WorkTaskProgressBar
                                                    spent={task.time_spent_mn}
                                                    left={task.time_left_mn}
                                                    maxTime={maxTime}
                                                />
                                            )}
                                        </HStack>
                                    );
                                });
                            })()}
                        </VStack>
                    </Box>
                )}
            </VStack>
        </Box>
    );
};
