import { Box, HStack, VStack, IconButton } from "@chakra-ui/react";
import { useEffect, useState, useCallback } from "react";
import { Tooltip } from "@/components/ui/tooltip";
import { BASE_URL } from "@/App";
import {
    TeamFilterPanel,
    TeamIncompleteTasksContent,
    TeamCompletedTasksContent,
    TEAM_VIEW_MODES,
    TEAM_VIEW_MODE_ICONS,
    type MemberWorkload,
    type TeamViewMode,
} from "@/components/team";
import { TeamProvider } from "@/context/team-ctx";

const TeamPageContent = () => {
    const [viewMode, setViewMode] = useState<TeamViewMode>("incomplete_tasks");
    const [workload, setWorkload] = useState<MemberWorkload[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedTypes, setSelectedTypes] = useState<Set<string>>(
        () =>
            new Set([
                "Defect - Application",
                "Defect - Configuration",
                "Defect - QA Vietnam",
                "Defect - Logs",
                "Defect - UX",
                "Defect - Infrastructure",
            ])
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

    const handleRefresh = useCallback(() => {
        fetchWorkload(selectedTypes, true);
    }, [fetchWorkload, selectedTypes]);

    return (
        <TeamProvider>
            <HStack h="calc(100vh - 105px)" align="stretch" gap={0} overflow="hidden">
                {/* Left: content based on mode */}
                <Box flex={1} minW={0} minH={0} overflow="hidden" display="flex" flexDirection="column">
                    {viewMode === "incomplete_tasks" && (
                        <TeamIncompleteTasksContent
                            workload={workload}
                            loading={loading}
                            onRefresh={handleRefresh}
                        />
                    )}
                    {viewMode === "completed_tasks" && (
                        <TeamCompletedTasksContent selectedTypes={selectedTypes} />
                    )}
                </Box>

                {/* Mode toolbar: vertical bar with icon buttons */}
                <VStack
                    py={4}
                    px={1}
                    gap={1}
                    borderLeftWidth="1px"
                    borderRightWidth="1px"
                    borderColor="border.default"
                    bg="bg.subtle"
                    flexShrink={0}
                >
                    {TEAM_VIEW_MODES.map((mode) => (
                        <Tooltip
                            key={mode.id}
                            content={mode.label}
                            positioning={{ placement: "left" }}
                        >
                            <IconButton
                                aria-label={mode.label}
                                variant={viewMode === mode.id ? "solid" : "ghost"}
                                size="sm"
                                onClick={() => setViewMode(mode.id)}
                            >
                                {TEAM_VIEW_MODE_ICONS[mode.id]}
                            </IconButton>
                        </Tooltip>
                    ))}
                </VStack>

                {/* Right: filter panel */}
                <TeamFilterPanel
                    selectedTypes={selectedTypes}
                    onSelectedTypesChange={setSelectedTypes}
                />
            </HStack>
        </TeamProvider>
    );
};

export const TeamPage = () => <TeamPageContent />;

export default TeamPage;
