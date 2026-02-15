import { Box, HStack, Input, IconButton } from "@chakra-ui/react";
import { useState } from "react";
import { FaSearch, FaSync } from "react-icons/fa";
import { BASE_URL } from "@/App";
import { Tooltip } from "@/components/ui/tooltip";
import { toaster } from "@/components/ui/toaster";
import { WorkTaskTreePanel, type TaskDetail } from "@/components/work";

export const WorkPage = () => {
    const [searchInput, setSearchInput] = useState("");
    const [rootTask, setRootTask] = useState<TaskDetail | null>(null);
    const [descendants, setDescendants] = useState<TaskDetail[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const fetchDescendants = async (taskId: string, forceRefresh = false) => {
        if (!taskId.trim()) return;

        setIsLoading(true);
        try {
            const [rootRes, descRes] = await Promise.all([
                fetch(`${BASE_URL}/api/work/task/${taskId}?force_refresh=${forceRefresh}`, {
                    method: "GET",
                    headers: { "Content-Type": "application/json" },
                }),
                fetch(`${BASE_URL}/api/work/task/${taskId}/descendants?force_refresh=${forceRefresh}`, {
                    method: "GET",
                    headers: { "Content-Type": "application/json" },
                }),
            ]);

            if (!rootRes.ok) throw new Error("Failed to fetch root task");
            if (!descRes.ok) throw new Error("Failed to fetch descendants");

            const root: TaskDetail = await rootRes.json();
            const desc: TaskDetail[] = await descRes.json();

            setRootTask(root);
            setDescendants(desc);
        } catch (error) {
            console.error("Error fetching tasks:", error);
            toaster.create({
                description: "Failed to fetch tasks",
                type: "error",
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleSearch = () => {
        fetchDescendants(searchInput);
    };

    const handleRefresh = () => {
        if (searchInput) {
            fetchDescendants(searchInput, true);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter") {
            handleSearch();
        }
    };

    return (
        <Box h="100vh" overflow="hidden">
            {/* Top Bar */}
            <HStack p={4} gap={3}>
                <Input
                    placeholder="Enter task ID (e.g. L-XXXXX)"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    maxW="350px"
                    size="sm"
                />
                <Tooltip content="Search descendants">
                    <IconButton
                        aria-label="Search descendants"
                        size="sm"
                        onClick={handleSearch}
                        disabled={!searchInput.trim()}
                    >
                        <FaSearch />
                    </IconButton>
                </Tooltip>
                <Tooltip content="Force refresh from API">
                    <IconButton
                        aria-label="Refresh"
                        size="sm"
                        variant="ghost"
                        onClick={handleRefresh}
                        disabled={!searchInput}
                    >
                        <FaSync />
                    </IconButton>
                </Tooltip>
            </HStack>

            {/* Tree panel with root header */}
            <Box h="calc(100vh - 80px)">
                <WorkTaskTreePanel
                    rootTask={rootTask}
                    descendants={descendants}
                    isLoading={isLoading}
                />
            </Box>
        </Box>
    );
};

export default WorkPage;
