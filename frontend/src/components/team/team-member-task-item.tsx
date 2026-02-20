import { Box, HStack, Text, Badge, Link } from "@chakra-ui/react";
import { docSubTypeIcon, statusColor } from "@/components/work/work-utils";
import { WorkTaskProgressBar } from "@/components/work/work-task-progress-bar";
import { isObsoleteTask, type TeamTask } from "./team-types";

interface TeamMemberTaskItemProps {
    task: TeamTask;
    maxTime: number;
}

export const TeamMemberTaskItem = ({ task, maxTime }: TeamMemberTaskItemProps) => {
    const obsolete = isObsoleteTask(task);
    const { icon, color } = docSubTypeIcon(task.doc_sub_type || "");

    return (
        <HStack
            p={2}
            gap={2}
            _hover={{
                bg: { base: "gray.100", _dark: "gray.800" },
            }}
            borderRadius="md"
        >
            {icon && (
                <Box color={color} flexShrink={0}>
                    {icon}
                </Box>
            )}
            <HStack flex={1} gap={2} overflow="hidden" minW={0}>
                {task.cortex_share_link ? (
                    <Link
                        href={task.cortex_share_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        fontSize="sm"
                        truncate
                        color={obsolete ? "fg.subtle" : undefined}
                        _hover={{ textDecoration: "underline" }}
                    >
                        {task.title || task.identifier}
                    </Link>
                ) : (
                    <Text
                        fontSize="sm"
                        truncate
                        color={obsolete ? "fg.subtle" : undefined}
                    >
                        {task.title || task.identifier}
                    </Text>
                )}
                <Badge
                    size="sm"
                    colorPalette={statusColor(task.status)}
                    variant="subtle"
                    flexShrink={0}
                >
                    {task.status || "—"}
                </Badge>
            </HStack>
            {!obsolete && (
                <WorkTaskProgressBar
                    spent={task.time_spent_mn}
                    left={task.time_left_mn}
                    maxTime={maxTime}
                />
            )}
        </HStack>
    );
};
