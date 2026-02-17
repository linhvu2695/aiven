import {
    Box,
    VStack,
    HStack,
    Text,
    IconButton,
    Badge,
} from "@chakra-ui/react";
import { FaTimes } from "react-icons/fa";
import type { TaskDetail } from "./work-types";
import { statusColor, docSubTypeIcon } from "./work-utils";
import { useWorkContext } from "@/context/work-ctx";

interface WorkTaskListItemProps {
    task: TaskDetail;
    isSelected: boolean;
}

export const WorkTaskListItem = ({ task, isSelected }: WorkTaskListItemProps) => {
    const { selectTask, removeTask } = useWorkContext();
    const { icon: docIcon, color: docIconColor } = docSubTypeIcon(task.doc_sub_type);

    return (
        <HStack
            px={3}
            py={2}
            gap={2}
            cursor="pointer"
            bg={isSelected ? { base: "gray.100", _dark: "gray.800" } : undefined}
            _hover={{ bg: { base: "gray.50", _dark: "gray.900" } }}
            borderBottomWidth="1px"
            borderColor="border.default"
            onClick={() => selectTask(task.identifier)}
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
                <HStack gap={1} flexWrap="wrap">
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
                    {task.importance_for_next_release && (
                        <Badge
                            size="sm"
                            variant="subtle"
                            colorPalette={
                                task.importance_for_next_release.includes("1") ? "red"
                                : task.importance_for_next_release.includes("2") ? "yellow"
                                : task.importance_for_next_release.includes("3") ? "green"
                                : "gray"
                            }
                        >
                            {task.importance_for_next_release}
                        </Badge>
                    )}
                </HStack>
            </VStack>
            <IconButton
                aria-label="Remove task"
                variant="ghost"
                size="2xs"
                onClick={(e) => {
                    e.stopPropagation();
                    removeTask(task.identifier);
                }}
            >
                <FaTimes />
            </IconButton>
        </HStack>
    );
};
