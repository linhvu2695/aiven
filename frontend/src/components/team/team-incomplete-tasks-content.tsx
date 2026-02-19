import { Box, VStack, HStack, Text, Spinner, IconButton } from "@chakra-ui/react";
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
import { formatMinutes, ACCENT_COLOR } from "@/components/work/work-utils";
import { SummaryCard } from "@/components/ui/summary-card";
import { useColorModeValue } from "@/components/ui/color-mode";
import { useTeamContext } from "@/context/team-ctx";
import { TeamMemberTaskList } from "./team-member-task-list";
import type { MemberWorkload } from "./team-types";
import { MEMBER_COLORS } from "./team-types";

interface TeamIncompleteTasksContentProps {
    workload: MemberWorkload[];
    loading: boolean;
    onRefresh: () => void;
}

export const TeamIncompleteTasksContent = ({
    workload,
    loading,
    onRefresh,
}: TeamIncompleteTasksContentProps) => {
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
                    <TeamMemberTaskList
                        memberData={selectedMemberData}
                        headerBg={selectedMemberBg}
                        onClose={() => setSelectedMember(null)}
                    />
                )}
            </VStack>
        </Box>
    );
};
