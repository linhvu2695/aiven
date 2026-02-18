import { Box, VStack, Text, Spinner } from "@chakra-ui/react";
import { useMemo } from "react";
import { WorkTaskTreeItem } from "./work-task-tree-item";
import { WorkTaskHeader } from "../work-task-header";
import { useWorkContext } from "@/context/work-ctx";

export const WorkTaskTreePanel = () => {
    const {
        selectedRootTask: rootTask,
        isLoadingTree: isLoading,
        filteredTasks,
        assignees,
        activeTypeFilters,
        setActiveTypeFilters,
        activeAssigneeFilters,
        setActiveAssigneeFilters,
    } = useWorkContext();

    const topLevelTasks = useMemo(() => {
        if (!rootTask) return [];
        return filteredTasks.filter(
            (t) => t.parent_folder_identifier === rootTask.identifier
        );
    }, [rootTask, filteredTasks]);

    // Compute the max total time (spent + left) across all tasks for scaling
    const maxTime = useMemo(() => {
        if (filteredTasks.length === 0) return 1;
        return Math.max(
            ...filteredTasks.map((t) => t.time_spent_mn + t.time_left_mn),
            1
        );
    }, [filteredTasks]);

    return (
        <Box w="100%" h="100%" display="flex" flexDirection="column">
            {isLoading ? (
                <VStack justify="center" align="center" h="200px">
                    <Spinner size="lg" />
                    <Text fontSize="sm" color="fg.muted">
                        Loading tasks...
                    </Text>
                </VStack>
            ) : rootTask ? (
                <>
                    {/* Fixed root task header */}
                    <WorkTaskHeader
                        task={rootTask}
                        allTasks={filteredTasks}
                        activeFilters={activeTypeFilters}
                        onFilterChange={setActiveTypeFilters}
                        assignees={assignees}
                        activeAssigneeFilters={activeAssigneeFilters}
                        onAssigneeFilterChange={setActiveAssigneeFilters}
                    />

                    {/* Scrollable descendants */}
                    <Box flex={1} overflowY="auto" px={2}>
                        {topLevelTasks.length > 0 ? (
                            <VStack gap={0} align="stretch">
                                {topLevelTasks.map((task) => (
                                    <WorkTaskTreeItem
                                        key={task.identifier}
                                        task={task}
                                        allTasks={filteredTasks}
                                        maxTime={maxTime}
                                        level={0}
                                    />
                                ))}
                            </VStack>
                        ) : (
                            <Box p={4} textAlign="center">
                                <Text color="fg.muted" fontSize="sm">
                                    No child tasks found.
                                </Text>
                            </Box>
                        )}
                    </Box>
                </>
            ) : (
                <Box p={4} textAlign="center">
                    <Text color="fg.muted" fontSize="sm">
                        No tasks found. Enter a task ID to search.
                    </Text>
                </Box>
            )}
        </Box>
    );
};
