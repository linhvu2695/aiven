import { HStack } from "@chakra-ui/react";
import { useEffect, useState, useCallback } from "react";
import { BASE_URL } from "@/App";
import { TeamWorkloadContent, TeamWorkloadFilterPanel } from "@/components/team";
import type { MemberWorkload } from "@/components/team";
import { TeamProvider } from "@/context/team-ctx";

const TeamPageContent = () => {
    const [workload, setWorkload] = useState<MemberWorkload[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedTypes, setSelectedTypes] = useState<Set<string>>(
        () =>
            new Set([
                "Defect - Application",
                "Defect - Configuration",
                "Defect - QA",
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
            <HStack h="calc(100vh - 105px)" align="stretch" gap={0}>
                <TeamWorkloadContent
                    workload={workload}
                    loading={loading}
                    onRefresh={handleRefresh}
                />
                <TeamWorkloadFilterPanel
                    selectedTypes={selectedTypes}
                    onSelectedTypesChange={setSelectedTypes}
                />
            </HStack>
        </TeamProvider>
    );
};

export const TeamPage = () => <TeamPageContent />;

export default TeamPage;
