import { Box, VStack, Text, Spinner } from "@chakra-ui/react";
import { useMemo } from "react";
import { WorkTaskTreeItem } from "./work-task-tree-item";
import { WorkTaskHeader } from "./work-task-header";
import type { TaskDetail } from "./work-types";

interface WorkTaskTreePanelProps {
    rootTask: TaskDetail | null;
    descendants: TaskDetail[];
    isLoading: boolean;
}

export const WorkTaskTreePanel = ({
    rootTask,
    descendants,
    isLoading,
}: WorkTaskTreePanelProps) => {
    // All tasks including root (needed for subtree time aggregation)
    const allTasks = useMemo(() => {
        if (!rootTask) return descendants;
        return [rootTask, ...descendants];
    }, [rootTask, descendants]);

    // Direct children of the root task
    const topLevelTasks = useMemo(() => {
        if (!rootTask) return [];
        return descendants.filter(
            (t) => t.parent_folder_identifier === rootTask.identifier
        );
    }, [rootTask, descendants]);

    // Compute the max total time (spent + left) across all tasks for scaling
    const maxTime = useMemo(() => {
        if (allTasks.length === 0) return 1;
        return Math.max(
            ...allTasks.map((t) => t.time_spent_mn + t.time_left_mn),
            1
        );
    }, [allTasks]);

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
                        allTasks={allTasks}
                        maxTime={maxTime}
                    />

                    {/* Scrollable descendants */}
                    <Box flex={1} overflowY="auto" px={2}>
                        {topLevelTasks.length > 0 ? (
                            <VStack gap={0} align="stretch">
                                {topLevelTasks.map((task) => (
                                    <WorkTaskTreeItem
                                        key={task.identifier}
                                        task={task}
                                        allTasks={allTasks}
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
