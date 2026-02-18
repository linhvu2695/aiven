import { Box, VStack, HStack, Text, Spinner, IconButton, Checkbox, Badge, CloseButton } from "@chakra-ui/react";
import { useEffect, useState, useMemo, useCallback } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as ReTooltip, Cell, ResponsiveContainer } from "recharts";
import { Chart, useChart } from "@chakra-ui/charts";
import { FaSyncAlt } from "react-icons/fa";
import { Tooltip } from "@/components/ui/tooltip";
import { BASE_URL } from "@/App";
import { formatMinutes, ACCENT_COLOR, DOC_SUB_TYPES, docSubTypeIcon, statusColor } from "@/components/work/work-utils";
import { SummaryCard } from "@/components/ui/summary-card";
import { useColorModeValue } from "@/components/ui/color-mode";
import { WorkTaskProgressBar } from "@/components/work/work-task-progress-bar";
import { Link } from "@chakra-ui/react";

interface TeamTask {
    title: string;
    identifier: string;
    doc_sub_type?: string;
    status: string;
    time_spent_mn: number;
    time_left_mn: number;
    cortex_share_link?: string;
    [key: string]: unknown;
}

interface MemberWorkload {
    name: string;
    task_count: number;
    time_spent_mn: number;
    time_left_mn: number;
    tasks: TeamTask[];
}

const MEMBER_COLORS = [
    "teal.400", "blue.400", "purple.400", "orange.400", "cyan.400",
    "pink.400", "yellow.400", "red.400", "green.400", "gray.400",
];

const TeamPageContent = () => {
    const [workload, setWorkload] = useState<MemberWorkload[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedTypes, setSelectedTypes] = useState<Set<string>>(() => new Set(["Development"]));
    const [selectedMember, setSelectedMember] = useState<string | null>(null);
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

    const fetchWorkload = useCallback(async (types: Set<string>, forceRefresh = false) => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            for (const t of types) params.append("subtypes", t.toLowerCase());
            if (forceRefresh) params.append("force_refresh", "true");
            const res = await fetch(`${BASE_URL}/api/work/team/workload?${params}`);
            if (res.ok) setWorkload(await res.json());
        } catch (err) {
            console.error("Failed to fetch team workload:", err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchWorkload(selectedTypes);
    }, [selectedTypes, fetchWorkload]);

    const chartDataRemaining = useMemo(
        () => workload.map((m, i) => ({
            name: m.name.split(" ")[0],
            fullName: m.name,
            value: Math.round(m.time_left_mn / 60 * 10) / 10,
            rawMinutes: m.time_left_mn,
            color: MEMBER_COLORS[i % MEMBER_COLORS.length],
        })),
        [workload]
    );

    const chartDataTaskCount = useMemo(
        () => workload.map((m, i) => ({
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
            <VStack justify="center" align="center" h="calc(100vh - 105px)">
                <Spinner size="lg" />
                <Text fontSize="sm" color="fg.muted">Loading team workload...</Text>
            </VStack>
        );
    }

    const totalTasks = workload.reduce((s, m) => s + m.task_count, 0);
    const totalRemaining = workload.reduce((s, m) => s + m.time_left_mn, 0);
    const totalSpent = workload.reduce((s, m) => s + m.time_spent_mn, 0);

    const allTypesSelected = DOC_SUB_TYPES.every((t) => selectedTypes.has(t));

    const toggleType = (type: string) => {
        setSelectedTypes((prev) => {
            const next = new Set(prev);
            if (next.has(type)) next.delete(type);
            else next.add(type);
            return next;
        });
    };

    const toggleAllTypes = () => {
        if (allTypesSelected) setSelectedTypes(new Set());
        else setSelectedTypes(new Set(DOC_SUB_TYPES));
    };

    return (
        <HStack h="calc(100vh - 105px)" align="stretch" gap={0}>
            {/* Main content */}
            <Box flex={1} overflowY="auto" px={6} py={4}>
                <VStack gap={6} align="stretch">

                    {/* Header */}
                    <HStack gap={3}>
                        <Text fontWeight="bold" fontSize="xl">Team Workload</Text>
                        <Tooltip content="Refresh from Orange Logic">
                            <IconButton
                                aria-label="Force refresh"
                                variant="ghost"
                                size="xs"
                                onClick={() => fetchWorkload(selectedTypes, true)}
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
                            <Text fontSize="sm" fontWeight="semibold" mb={2}>Time Remaining (hours)</Text>
                            <Chart.Root chart={chartRemaining}>
                                <ResponsiveContainer width="100%" height={200}>
                                    <BarChart data={chartDataRemaining} margin={{ top: 5, right: 10, bottom: 5, left: -10 }}>
                                        <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                                        <XAxis dataKey="name" fontSize={11} />
                                        <YAxis fontSize={11} />
                                        <ReTooltip
                                            cursor={{ fill: "transparent" }}
                                            content={({ payload }) => {
                                                if (!payload?.length) return null;
                                                const d = payload[0].payload;
                                                return (
                                                    <Box bg="bg.panel" borderWidth="1px" borderColor="border.default" borderRadius="md" px={3} py={2} shadow="md">
                                                        <Text fontSize="xs" fontWeight="bold">{d.fullName}</Text>
                                                        <Text fontSize="xs" color="fg.muted">{formatMinutes(d.rawMinutes)} remaining</Text>
                                                    </Box>
                                                );
                                            }}
                                        />
                                        <Bar
                                            dataKey="value"
                                            radius={[4, 4, 0, 0]}
                                            cursor="pointer"
                                            onClick={(ev: unknown) => {
                                                const e = ev as { payload?: { fullName?: string }; fullName?: string };
                                                const name = e?.payload?.fullName ?? e?.fullName;
                                                if (name) setSelectedMember((prev) => (prev === name ? null : name));
                                            }}
                                        >
                                            {chartDataRemaining.map((entry) => (
                                                <Cell key={entry.fullName} fill={chartRemaining.color(entry.color)} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </Chart.Root>
                        </Box>

                        <Box flex={1}>
                            <Text fontSize="sm" fontWeight="semibold" mb={2}>Remaining Tasks</Text>
                            <Chart.Root chart={chartTaskCount}>
                                <ResponsiveContainer width="100%" height={200}>
                                    <BarChart data={chartDataTaskCount} margin={{ top: 5, right: 10, bottom: 5, left: -10 }}>
                                        <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                                        <XAxis dataKey="name" fontSize={11} />
                                        <YAxis fontSize={11} allowDecimals={false} />
                                        <ReTooltip
                                            cursor={{ fill: "transparent" }}
                                            content={({ payload }) => {
                                                if (!payload?.length) return null;
                                                const d = payload[0].payload;
                                                return (
                                                    <Box bg="bg.panel" borderWidth="1px" borderColor="border.default" borderRadius="md" px={3} py={2} shadow="md">
                                                        <Text fontSize="xs" fontWeight="bold">{d.fullName}</Text>
                                                        <Text fontSize="xs" color="fg.muted">{d.value} task{d.value !== 1 ? "s" : ""}</Text>
                                                    </Box>
                                                );
                                            }}
                                        />
                                        <Bar
                                            dataKey="value"
                                            radius={[4, 4, 0, 0]}
                                            cursor="pointer"
                                            onClick={(ev: unknown) => {
                                                const e = ev as { payload?: { fullName?: string }; fullName?: string };
                                                const name = e?.payload?.fullName ?? e?.fullName;
                                                if (name) setSelectedMember((prev) => (prev === name ? null : name));
                                            }}
                                        >
                                            {chartDataTaskCount.map((entry) => (
                                                <Cell key={entry.fullName} fill={chartTaskCount.color(entry.color)} />
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
                                        return da - db; // soonest first (priority queue)
                                    });
                                    return sortedTasks.map((task) => {
                                        const obsolete = (task.status || "").toLowerCase().includes("obsolete");
                                        const { icon, color } = docSubTypeIcon(task.doc_sub_type || "");
                                        return (
                                            <HStack
                                                key={task.identifier}
                                                p={2}
                                                gap={2}
                                                _hover={{ bg: { base: "gray.100", _dark: "gray.800" } }}
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
                                                        color={obsolete ? "fg.subtle" : undefined}
                                                        _hover={{ textDecoration: "underline" }}
                                                    >
                                                        {task.title || task.identifier}
                                                    </Link>
                                                ) : (
                                                    <Text
                                                        fontSize="sm"
                                                        truncate
                                                        color={obsolete ? "fg.subtle" : undefined}
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

            {/* Right: always-visible filter panel */}
            <Box
                w="220px"
                flexShrink={0}
                borderLeftWidth="1px"
                borderColor="border.default"
                overflowY="auto"
                px={3}
                py={4}
            >
                <VStack align="stretch" gap={1}>
                    <Text fontSize="xs" fontWeight="semibold" color="fg.muted" mb={1}>Task type</Text>

                    <Checkbox.Root checked={allTypesSelected} onCheckedChange={toggleAllTypes} size="sm">
                        <Checkbox.HiddenInput />
                        <Checkbox.Control />
                        <Checkbox.Label><Text fontSize="xs" fontWeight="medium">All</Text></Checkbox.Label>
                    </Checkbox.Root>

                    <Box borderBottomWidth="1px" borderColor="border.default" my={1} />

                    {DOC_SUB_TYPES.map((type) => {
                        const { icon, color } = docSubTypeIcon(type);
                        return (
                            <HStack key={type} gap={0}>
                                <Checkbox.Root checked={selectedTypes.has(type)} onCheckedChange={() => toggleType(type)} size="sm">
                                    <Checkbox.HiddenInput />
                                    <Checkbox.Control />
                                </Checkbox.Root>
                                <HStack
                                    gap={1} flex={1} cursor="pointer" px={1} borderRadius="sm"
                                    _hover={{ bg: { base: "gray.100", _dark: "gray.700" } }}
                                    onClick={() => setSelectedTypes(new Set([type]))}
                                >
                                    {icon && <Box color={color}>{icon}</Box>}
                                    <Text fontSize="xs">{type}</Text>
                                </HStack>
                            </HStack>
                        );
                    })}
                </VStack>
            </Box>
        </HStack>
    );
};

export const TeamPage = () => <TeamPageContent />;

export default TeamPage;
