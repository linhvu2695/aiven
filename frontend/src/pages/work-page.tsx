import { Box, HStack, VStack, IconButton } from "@chakra-ui/react";
import { useState, useCallback, useEffect } from "react";
import { FaSitemap } from "react-icons/fa";
import { BASE_URL } from "@/App";
import { toaster } from "@/components/ui/toaster";
import { Tooltip } from "@/components/ui/tooltip";
import { WorkTaskTreePanel, WorkTaskListPanel, WorkParticipantsPanel, WORK_VIEW_MODES, type TaskDetail, type WorkViewMode } from "@/components/work";
import { FaPeopleGroup } from "react-icons/fa6";

const VIEW_MODE_ICONS: Record<WorkViewMode, React.ReactNode> = {
    hierarchy: <FaSitemap />,
    participants: <FaPeopleGroup />,
};

export const WorkPage = () => {
    const [monitoredTasks, setMonitoredTasks] = useState<TaskDetail[]>([]);
    const [selectedRootTask, setSelectedRootTask] = useState<TaskDetail | null>(null);
    const [selectedDescendants, setSelectedDescendants] = useState<TaskDetail[]>([]);
    const [isAdding, setIsAdding] = useState(false);
    const [isLoadingTree, setIsLoadingTree] = useState(false);
    const [viewMode, setViewMode] = useState<WorkViewMode>("hierarchy");

    // Load monitored tasks on mount
    useEffect(() => {
        const loadMonitored = async () => {
            try {
                const res = await fetch(`${BASE_URL}/api/work/monitored`);
                if (!res.ok) return;
                const data: TaskDetail[] = await res.json();
                setMonitoredTasks(data);
            } catch (error) {
                console.error("Error loading monitored tasks:", error);
            }
        };
        loadMonitored();
    }, []);

    const handleSelect = useCallback(async (taskId: string) => {
        setIsLoadingTree(true);
        try {
            const [rootRes, descRes] = await Promise.all([
                fetch(`${BASE_URL}/api/work/task/${taskId}`),
                fetch(`${BASE_URL}/api/work/task/${taskId}/descendants`),
            ]);

            if (!rootRes.ok) throw new Error("Failed to fetch root task");
            if (!descRes.ok) throw new Error("Failed to fetch descendants");

            setSelectedRootTask(await rootRes.json());
            setSelectedDescendants(await descRes.json());
        } catch (error) {
            console.error("Error fetching task tree:", error);
            toaster.create({ description: "Failed to load task hierarchy", type: "error" });
        } finally {
            setIsLoadingTree(false);
        }
    }, []);

    const handleAdd = useCallback(async (taskId: string, forceRefresh: boolean) => {
        // Don't add duplicates
        if (monitoredTasks.some((t) => t.identifier === taskId)) {
            handleSelect(taskId);
            return;
        }

        setIsAdding(true);
        try {
            const rootRes = await fetch(`${BASE_URL}/api/work/task/${taskId}?force_refresh=${forceRefresh}`);
            if (!rootRes.ok) throw new Error("Failed to fetch task");
            const rootTask: TaskDetail = await rootRes.json();

            // Set monitor=true in backend
            await fetch(`${BASE_URL}/api/work/task/${rootTask.identifier}/monitor`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ monitor: true }),
            });

            setMonitoredTasks((prev) => [...prev, rootTask]);
            handleSelect(rootTask.identifier);
        } catch (error) {
            toaster.create({
                description: `Failed to add task ${taskId} to monitor list`,
                type: "error",
            });
        } finally {
            setIsAdding(false);
        }
    }, [monitoredTasks, handleSelect]);

    const handleRemove = useCallback(async (taskId: string) => {
        // Set monitor=false in backend
        try {
            await fetch(`${BASE_URL}/api/work/task/${taskId}/monitor`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ monitor: false }),
            });
        } catch (error) {
            toaster.create({ description: "Failed to remove task from monitor list", type: "error" });
            return;
        }

        setMonitoredTasks((prev) => prev.filter((t) => t.identifier !== taskId));
        if (selectedRootTask?.identifier === taskId) {
            setSelectedRootTask(null);
            setSelectedDescendants([]);
        }
    }, [selectedRootTask]);

    return (
        <HStack h="100vh" overflow="hidden" gap={0} align="stretch">
            {/* Left panel: task list */}
            <Box w="320px" flexShrink={0}>
                <WorkTaskListPanel
                    monitoredTasks={monitoredTasks}
                    selectedTaskId={selectedRootTask?.identifier ?? null}
                    onSelect={handleSelect}
                    onAdd={handleAdd}
                    onRemove={handleRemove}
                    isAdding={isAdding}
                />
            </Box>

            {/* Mode toolbar */}
            <VStack
                py={4}
                px={1}
                gap={1}
                borderRightWidth="1px"
                borderColor="border.default"
                bg="bg.subtle"
                flexShrink={0}
            >
                {WORK_VIEW_MODES.map((mode) => (
                    <Tooltip key={mode.id} content={mode.label} positioning={{ placement: "right" }}>
                        <IconButton
                            aria-label={mode.label}
                            variant={viewMode === mode.id ? "solid" : "ghost"}
                            size="sm"
                            onClick={() => setViewMode(mode.id)}
                        >
                            {VIEW_MODE_ICONS[mode.id]}
                        </IconButton>
                    </Tooltip>
                ))}
            </VStack>

            {/* Right panel: content based on mode */}
            <Box flex={1} h="100%">
                {viewMode === "hierarchy" && (
                    <WorkTaskTreePanel
                        rootTask={selectedRootTask}
                        descendants={selectedDescendants}
                        isLoading={isLoadingTree}
                    />
                )}
                {viewMode === "participants" && (
                    <WorkParticipantsPanel
                        rootTask={selectedRootTask}
                        descendants={selectedDescendants}
                        isLoading={isLoadingTree}
                    />
                )}
            </Box>
        </HStack>
    );
};

export default WorkPage;
