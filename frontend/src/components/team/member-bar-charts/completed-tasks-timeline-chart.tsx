import { useMemo, useState, useCallback } from "react";
import { Box, HStack, VStack, Text } from "@chakra-ui/react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as ReTooltip,
    ResponsiveContainer,
    Legend,
} from "recharts";
import { Chart, useChart } from "@chakra-ui/charts";
import type { MemberWorkload } from "../team-types";
import { MEMBER_COLORS } from "../team-types";

export interface CompletedTasksTimelineChartProps {
    workload: MemberWorkload[];
    startDate: string;
    endDate: string;
    onMemberClick?: (memberName: string) => void;
    width?: number | string;
    height?: number | string;
}

/** Parse a date string to YYYY-MM-DD, or null if invalid */
const toDateKey = (dateStr: string | null | undefined): string | null => {
    if (!dateStr || typeof dateStr !== "string") return null;
    const d = new Date(dateStr);
    if (Number.isNaN(d.getTime())) return null;
    return d.toISOString().slice(0, 10);
};

/** Generate all dates between start and end (inclusive), YYYY-MM-DD */
const dateRange = (start: string, end: string): string[] => {
    const out: string[] = [];
    const d = new Date(start);
    const endD = new Date(end);
    while (d <= endD) {
        out.push(d.toISOString().slice(0, 10));
        d.setDate(d.getDate() + 1);
    }
    return out;
};

export const CompletedTasksTimelineChart = ({
    workload,
    startDate,
    endDate,
    width = "100%",
    height = 200,
    onMemberClick,
}: CompletedTasksTimelineChartProps) => {
    const [focusedMember, setFocusedMember] = useState<string | null>(null);

    const handleMemberClick = useCallback(
        (name: string) => {
            setFocusedMember((prev) => (prev === name ? null : name));
            onMemberClick?.(name);
        },
        [onMemberClick]
    );

    const { timelineData, members } = useMemo(() => {
        const countsByMemberAndDate: Record<string, Record<string, number>> = {};
        for (const m of workload) {
            countsByMemberAndDate[m.name] = {};
            for (const task of m.tasks) {
                const key = toDateKey(task.completion_date);
                if (key) {
                    const memberCounts = countsByMemberAndDate[m.name];
                    memberCounts[key] = (memberCounts[key] ?? 0) + 1;
                }
            }
        }
        const members = workload.map((m) => m.name);
        const cumulatives: Record<string, number> = {};
        for (const name of members) cumulatives[name] = 0;

        const data = dateRange(startDate, endDate).map((date) => {
            const row: Record<string, string | number> = { date };
            for (const name of members) {
                cumulatives[name] += countsByMemberAndDate[name]?.[date] ?? 0;
                row[name] = cumulatives[name];
            }
            return row;
        });
        return { timelineData: data, members };
    }, [workload, startDate, endDate]);

    const series = useMemo(
        () =>
            members.map((name, i) => ({
                name,
                color: MEMBER_COLORS[i % MEMBER_COLORS.length],
            })),
        [members]
    );

    const chart = useChart({
        data: timelineData,
        series: series.map((s) => ({ name: s.name, color: s.color })),
    });

    if (timelineData.length === 0) {
        return (
            <Box
                width={width}
                height={height}
                display="flex"
                alignItems="center"
                justifyContent="center"
                borderRadius="lg"
                borderWidth="1px"
                borderColor="border.default"
                bg="bg.subtle"
            >
                <Text fontSize="sm" color="fg.muted">
                    No completed tasks with completion dates in this range
                </Text>
            </Box>
        );
    }

    return (
        <Box flex={1} width={width} height={height} display="flex" flexDirection="column" minH={0}>
            <Text fontSize="sm" fontWeight="semibold" mb={2} flexShrink={0}>
                Cumulative Completed Tasks by Assignee
            </Text>
            <Box flex={1} minH={0}>
                <Chart.Root chart={chart}>
                    <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={timelineData} margin={{ top: 5, right: 10, bottom: 5, left: -10 }}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                        <XAxis dataKey="date" fontSize={11} tickFormatter={(v) => v.slice(5)} />
                        <YAxis fontSize={11} allowDecimals={false} />
                        <ReTooltip
                            cursor={{ strokeDasharray: "3 3" }}
                            content={({ payload, label }) => {
                                if (!payload?.length || !label) return null;
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
                                        <Text fontSize="xs" fontWeight="bold" mb={1}>
                                            {label}
                                        </Text>
                                        <VStack align="stretch" gap={0.5}>
                                            {payload.map((p) => (
                                                <HStack key={p.dataKey} justify="space-between" gap={4}>
                                                    <Text fontSize="xs" color={p.color}>
                                                        {p.name}:
                                                    </Text>
                                                    <Text fontSize="xs" fontWeight="medium">
                                                        {p.value} task
                                                        {(p.value as number) !== 1 ? "s" : ""}
                                                    </Text>
                                                </HStack>
                                            ))}
                                        </VStack>
                                    </Box>
                                );
                            }}
                        />
                        <Legend
                            content={({ payload }) => (
                                <HStack
                                    gap={4}
                                    flexWrap="wrap"
                                    justify="center"
                                    mt={2}
                                    cursor="pointer"
                                >
                                    {payload?.map((entry) => {
                                        const name = entry.value as string;
                                        const isFocused = focusedMember === null || focusedMember === name;
                                        return (
                                            <HStack
                                                key={name}
                                                gap={1.5}
                                                opacity={isFocused ? 1 : 0.35}
                                                _hover={{ opacity: 1 }}
                                                onClick={() => handleMemberClick(name)}
                                            >
                                                <Box
                                                    w={3}
                                                    h={3}
                                                    borderRadius="sm"
                                                    bg={entry.color}
                                                />
                                                <Text fontSize="xs">{name}</Text>
                                            </HStack>
                                        );
                                    })}
                                </HStack>
                            )}
                        />
                        {members.map((name, i) => {
                            const isFocused = focusedMember === null || focusedMember === name;
                            return (
                                <Line
                                    key={name}
                                    type="monotone"
                                    dataKey={name}
                                    name={name}
                                    stroke={chart.color(series[i].color)}
                                    strokeWidth={isFocused ? 2 : 1.5}
                                    strokeOpacity={isFocused ? 1 : 0.25}
                                    dot={{ r: isFocused ? 2 : 0 }}
                                    activeDot={{ r: 4 }}
                                    isAnimationActive
                                    onClick={() => handleMemberClick(name)}
                                    style={{ cursor: "pointer" }}
                                />
                            );
                        })}
                    </LineChart>
                </ResponsiveContainer>
            </Chart.Root>
                </Box>
        </Box>
    );
};
