import { Box, HStack, VStack, Text, CloseButton } from "@chakra-ui/react";
import { TeamMemberTaskItem } from "./team-member-task-item";
import type { MemberWorkload } from "./team-types";

interface TeamMemberTaskListProps {
    memberData: MemberWorkload;
    headerBg: string;
    onClose: () => void;
}

export const TeamMemberTaskList = ({
    memberData,
    headerBg,
    onClose,
}: TeamMemberTaskListProps) => {
    const maxTime = Math.max(
        ...memberData.tasks.map((t) => t.time_spent_mn + t.time_left_mn),
        1
    );
    const sortedTasks = [...memberData.tasks].sort((a, b) => {
        const da = a.estimated_completion_date
            ? new Date(a.estimated_completion_date as string).getTime()
            : Infinity;
        const db = b.estimated_completion_date
            ? new Date(b.estimated_completion_date as string).getTime()
            : Infinity;
        return da - db;
    });

    return (
        <Box
            borderWidth="1px"
            borderColor="border.default"
            borderRadius="md"
            overflow="hidden"
            mt={2}
        >
            <HStack
                justify="space-between"
                px={4}
                py={2}
                bg={headerBg}
                borderBottomWidth="1px"
                borderColor="border.default"
            >
                <Text fontSize="sm" fontWeight="semibold">
                    {memberData.name} — {memberData.tasks.length} remaining task
                    {memberData.tasks.length !== 1 ? "s" : ""}
                </Text>
                <CloseButton size="sm" onClick={onClose} />
            </HStack>
            <VStack align="stretch" gap={0} maxH="400px" overflowY="auto" p={2}>
                {sortedTasks.map((task) => (
                    <TeamMemberTaskItem
                        key={task.identifier}
                        task={task}
                        maxTime={maxTime}
                    />
                ))}
            </VStack>
        </Box>
    );
};
