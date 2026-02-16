import {
    Box,
    VStack,
    HStack,
    Text,
    Input,
    IconButton,
    Badge,
    Spinner,
} from "@chakra-ui/react";
import { useState } from "react";
import { FaPlus, FaTimes, FaCloudDownloadAlt } from "react-icons/fa";
import { Tooltip } from "@/components/ui/tooltip";
import type { TaskDetail } from "./work-types";
import { statusColor, docSubTypeIcon } from "./work-utils";

interface WorkTaskListPanelProps {
    monitoredTasks: TaskDetail[];
    selectedTaskId: string | null;
    onSelect: (taskId: string) => void;
    onAdd: (taskId: string, forceRefresh: boolean) => Promise<void>;
    onRemove: (taskId: string) => void;
    isAdding: boolean;
}

export const WorkTaskListPanel = ({
    monitoredTasks,
    selectedTaskId,
    onSelect,
    onAdd,
    onRemove,
    isAdding,
}: WorkTaskListPanelProps) => {
    const [input, setInput] = useState("");

    const handleAdd = async (forceRefresh: boolean) => {
        if (!input.trim()) return;
        await onAdd(input.trim(), forceRefresh);
        setInput("");
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter") {
            handleAdd(false);
        }
    };

    return (
        <Box h="100%" display="flex" flexDirection="column" borderRightWidth="1px" borderColor="border.default">
            {/* Add task input */}
            <Box p={3} borderBottomWidth="1px" borderColor="border.default">
                <HStack gap={2}>
                    <Input
                        placeholder="Add task ID"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        size="sm"
                    />
                    <Tooltip content="Add task">
                        <IconButton
                            aria-label="Add task"
                            size="sm"
                            onClick={() => handleAdd(false)}
                            disabled={!input.trim() || isAdding}
                        >
                            {isAdding ? <Spinner size="xs" /> : <FaPlus />}
                        </IconButton>
                    </Tooltip>
                    <Tooltip content="Add task (fetch latest from OrangeLogic)">
                        <IconButton
                            aria-label="Add task with fresh data"
                            size="sm"
                            variant="outline"
                            onClick={() => handleAdd(true)}
                            disabled={!input.trim() || isAdding}
                        >
                            {isAdding ? <Spinner size="xs" /> : <FaCloudDownloadAlt />}
                        </IconButton>
                    </Tooltip>
                </HStack>
            </Box>

            {/* Task list */}
            <Box flex={1} overflowY="auto">
                {monitoredTasks.length === 0 ? (
                    <Box p={4} textAlign="center">
                        <Text color="fg.muted" fontSize="sm">
                            No tasks added yet.
                        </Text>
                    </Box>
                ) : (
                    <VStack gap={0} align="stretch">
                        {monitoredTasks.map((task) => {
                            const isSelected = selectedTaskId === task.identifier;
                            const { icon: docIcon, color: docIconColor } = docSubTypeIcon(task.doc_sub_type);

                            return (
                                <HStack
                                    key={task.identifier}
                                    px={3}
                                    py={2}
                                    gap={2}
                                    cursor="pointer"
                                    bg={isSelected ? { base: "gray.100", _dark: "gray.800" } : undefined}
                                    _hover={{ bg: { base: "gray.50", _dark: "gray.900" } }}
                                    borderBottomWidth="1px"
                                    borderColor="border.default"
                                    onClick={() => onSelect(task.identifier)}
                                >
                                    {docIcon && (
                                        <Box color={docIconColor} flexShrink={0}>
                                            {docIcon}
                                        </Box>
                                    )}
                                    <VStack gap={0} align="start" flex={1} overflow="hidden">
                                        <Text fontSize="sm" fontWeight="medium" truncate w="100%">
                                            {task.title || task.identifier}
                                        </Text>
                                        <HStack gap={1}>
                                            <Badge size="sm" variant="outline" colorPalette="gray">
                                                {task.identifier}
                                            </Badge>
                                            <Badge
                                                size="sm"
                                                colorPalette={statusColor(task.status)}
                                                variant="subtle"
                                            >
                                                {task.status || "—"}
                                            </Badge>
                                        </HStack>
                                    </VStack>
                                    <IconButton
                                        aria-label="Remove task"
                                        variant="ghost"
                                        size="2xs"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onRemove(task.identifier);
                                        }}
                                    >
                                        <FaTimes />
                                    </IconButton>
                                </HStack>
                            );
                        })}
                    </VStack>
                )}
            </Box>
        </Box>
    );
};
