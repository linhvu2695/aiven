import { Box, VStack, HStack, Text, Spinner, IconButton } from "@chakra-ui/react";
import { useMemo } from "react";
import { FaSyncAlt } from "react-icons/fa";
import { Tooltip } from "@/components/ui/tooltip";
import {
    MemberDualBarChart,
    MemberSingleBarChart,
    MemberBarChartModeSelector,
    type MemberDualBarChartDataItem,
    type MemberSingleBarChartDataItem,
} from "./member-bar-charts";
import { formatMinutes, ACCENT_COLOR } from "@/components/work/work-utils";
import { SummaryCard } from "@/components/ui/summary-card";
import { useColorModeValue } from "@/components/ui/color-mode";
import { useTeamContext } from "@/context/team-ctx";
import { TeamMemberTaskList } from "./team-member-task-list";
import type { MemberWorkload } from "./team-types";
import { MEMBER_COLORS, memberTaskCount, memberTimeSpentMn, memberTimeLeftMn } from "./team-types";

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
    const { selectedMember, setSelectedMember, chartMode } = useTeamContext();
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

    const chartData = useMemo(
        () =>
            workload.map((m, i) => ({
                name: m.name.split(" ")[0],
                fullName: m.name,
                hours: Math.round((memberTimeLeftMn(m) / 60) * 10) / 10,
                tasks: memberTaskCount(m),
                rawMinutes: memberTimeLeftMn(m),
                color: MEMBER_COLORS[i % MEMBER_COLORS.length],
            })),
        [workload]
    );

    const chartDataHours = useMemo(
        () =>
            chartData.map(({ name, fullName, hours, rawMinutes, color }) => ({
                name,
                fullName,
                value: hours,
                rawMinutes,
                color,
            })),
        [chartData]
    );

    const chartDataTasks = useMemo(
        () =>
            chartData.map(({ name, fullName, tasks, color }) => ({
                name,
                fullName,
                value: tasks,
                color,
            })),
        [chartData]
    );

    const handleBarClick = (item: MemberDualBarChartDataItem | MemberSingleBarChartDataItem) => {
        setSelectedMember(selectedMember === item.fullName ? null : item.fullName);
    };

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

    const totalTasks = workload.reduce((s, m) => s + memberTaskCount(m), 0);
    const totalRemaining = workload.reduce((s, m) => s + memberTimeLeftMn(m), 0);
    const totalSpent = workload.reduce((s, m) => s + memberTimeSpentMn(m), 0);

    return (
        <Box flex={1} minH={0} overflowY="auto" px={6} py={4}>
            <VStack gap={6} align="stretch">
                {/* Header */}
                <HStack gap={3} justify="space-between" wrap="wrap">
                    <HStack gap={3}>
                        <Text fontWeight="bold" fontSize="xl">
                            Team Workload
                        </Text>
                        <MemberBarChartModeSelector />
                    </HStack>
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

                {/* Chart */}
                {chartMode === "dual" ? (
                    <MemberDualBarChart
                        title="Remaining Workload"
                        data={chartData}
                        leftLabel="Hours"
                        rightLabel="Tasks"
                        tooltipTimeSuffix="remaining"
                        onBarClick={handleBarClick}
                        width="800px"
                    />
                ) : (
                    <HStack gap={6} align="start">
                        <MemberSingleBarChart
                            title="Time Remaining (hours)"
                            data={chartDataHours}
                            tooltipFormat="time"
                            tooltipSuffix="remaining"
                            onBarClick={handleBarClick}
                        />
                        <MemberSingleBarChart
                            title="Remaining Tasks"
                            data={chartDataTasks}
                            tooltipFormat="tasks"
                            allowDecimals={false}
                            onBarClick={handleBarClick}
                        />
                    </HStack>
                )}

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
