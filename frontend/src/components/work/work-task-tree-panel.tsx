import { Box, VStack, Text, Spinner } from "@chakra-ui/react";
import { useMemo } from "react";
import { WorkTaskTreeItem } from "./work-task-tree-item";
import type { TaskDetail } from "./work-types";

interface WorkTaskTreePanelProps {
    tasks: TaskDetail[];
    rootTaskId: string;
    isLoading: boolean;
    scaleMode: "linear" | "log";
}

export const WorkTaskTreePanel = ({
    tasks,
    rootTaskId,
    isLoading,
    scaleMode,
}: WorkTaskTreePanelProps) => {
    const rootTasks = tasks.filter(
        (t) => t.parent_folder_identifier === rootTaskId
    );

    // Compute the max total time (spent + left) across all tasks for scaling
    const maxTime = useMemo(() => {
        if (tasks.length === 0) return 1;
        return Math.max(
            ...tasks.map((t) => t.time_spent_mn + t.time_left_mn),
            1
        );
    }, [tasks]);

    return (
        <Box w="100%" h="100%">
            <VStack h="full" gap={0} align="stretch">
                <Box flex={1} overflowY="auto" px={2}>
                    {isLoading ? (
                        <VStack justify="center" align="center" h="200px">
                            <Spinner size="lg" />
                            <Text fontSize="sm" color="fg.muted">
                                Loading tasks...
                            </Text>
                        </VStack>
                    ) : rootTasks.length > 0 ? (
                        <VStack gap={0} align="stretch">
                            {rootTasks.map((task) => (
                                <WorkTaskTreeItem
                                    key={task.identifier}
                                    task={task}
                                    allTasks={tasks}
                                    maxTime={maxTime}
                                    scaleMode={scaleMode}
                                    level={0}
                                />
                            ))}
                        </VStack>
                    ) : (
                        <Box p={4} textAlign="center">
                            <Text color="fg.muted" fontSize="sm">
                                No tasks found. Enter a task ID to search.
                            </Text>
                        </Box>
                    )}
                </Box>
            </VStack>
        </Box>
    );
};
