import { Box, VStack, Text, Spinner } from "@chakra-ui/react";
import { useMemo, useState, useCallback } from "react";
import { WorkTaskTreeItem } from "./work-task-tree-item";
import { WorkTaskHeader } from "./work-task-header";
import { DEFAULT_DOC_SUB_TYPE_FILTER } from "./work-utils";
import { useWorkContext } from "@/context/work-ctx";

export const WorkTaskTreePanel = () => {
    const { selectedRootTask: rootTask, selectedDescendants: descendants, isLoadingTree: isLoading } = useWorkContext();
    const [activeFilters, setActiveFilters] = useState<Set<string>>(
        () => new Set(DEFAULT_DOC_SUB_TYPE_FILTER)
    );

    const handleFilterChange = useCallback((filters: Set<string>) => {
        setActiveFilters(filters);
    }, []);

    // All tasks including root (needed for subtree time aggregation)
    const allTasks = useMemo(() => {
        if (!rootTask) return descendants;
        return [rootTask, ...descendants];
    }, [rootTask, descendants]);

    // Filter descendants by doc_sub_type — keep tasks whose type matches,
    // plus any ancestor needed to maintain the tree structure
    const filteredTasks = useMemo(() => {
        if (activeFilters.size === 0) return allTasks;

        // First pass: find tasks matching the filter
        const matchingIds = new Set<string>();
        for (const t of allTasks) {
            const typeLower = t.doc_sub_type.toLowerCase();
            for (const filter of activeFilters) {
                if (typeLower.includes(filter.toLowerCase())) {
                    matchingIds.add(t.identifier);
                    break;
                }
            }
        }

        // Second pass: include ancestors of matching tasks to preserve tree structure
        const includedIds = new Set(matchingIds);
        const taskMap = new Map(allTasks.map((t) => [t.identifier, t]));
        for (const id of matchingIds) {
            let current = taskMap.get(id);
            while (current && current.parent_folder_identifier) {
                if (includedIds.has(current.parent_folder_identifier)) break;
                includedIds.add(current.parent_folder_identifier);
                current = taskMap.get(current.parent_folder_identifier);
            }
        }

        return allTasks.filter((t) => includedIds.has(t.identifier));
    }, [allTasks, activeFilters]);

    // Direct children of the root task (from filtered set)
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
                        activeFilters={activeFilters}
                        onFilterChange={handleFilterChange}
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
