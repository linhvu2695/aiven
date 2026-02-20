import { Box, HStack, VStack, Text, CloseButton } from "@chakra-ui/react";
import { TeamMemberTaskItem } from "./team-member-task-item";
import { formatMinutes } from "@/components/work/work-utils";
import { isObsoleteTask, type MemberWorkload, type TeamTask } from "./team-types";

export type TeamMemberTaskListVariant = "incomplete" | "completed";

interface TeamMemberTaskListProps {
    memberData: MemberWorkload;
    headerBg: string;
    onClose: () => void;
    variant?: TeamMemberTaskListVariant;
}

const sortIncomplete = (a: TeamTask, b: TeamTask) => {
    const da = a.estimated_completion_date
        ? new Date(a.estimated_completion_date as string).getTime()
        : Infinity;
    const db = b.estimated_completion_date
        ? new Date(b.estimated_completion_date as string).getTime()
        : Infinity;
    return da - db;
};

const sortCompleted = (a: TeamTask, b: TeamTask) => {
    const dateA = a.completion_date || a.estimated_completion_date;
    const dateB = b.completion_date || b.estimated_completion_date;
    const da = dateA ? new Date(dateA as string).getTime() : 0;
    const db = dateB ? new Date(dateB as string).getTime() : 0;
    return db - da; // most recent first
};

export const TeamMemberTaskList = ({
    memberData,
    headerBg,
    onClose,
    variant = "incomplete",
}: TeamMemberTaskListProps) => {
    const maxTime = Math.max(
        ...memberData.tasks.map((t) => t.time_spent_mn + (t.time_left_mn ?? 0)),
        1
    );
    const sortedTasks = [...memberData.tasks].sort(variant === "completed" ? sortCompleted : sortIncomplete);
    const headerLabel = variant === "completed" ? "completed" : "remaining";
    const count = memberData.tasks.length;

    const nonObsoleteTasks = memberData.tasks.filter((t) => !isObsoleteTask(t));
    const avgTimeSpentMn =
        nonObsoleteTasks.length > 0
            ? nonObsoleteTasks.reduce((s, t) => s + t.time_spent_mn, 0) / nonObsoleteTasks.length
            : 0;

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
                <VStack align="start" gap={0}>
                    <Text fontSize="sm" fontWeight="semibold">
                        {memberData.name} — {count} {headerLabel} task
                        {count !== 1 ? "s" : ""}
                    </Text>
                    <Text fontSize="2xs" color="fg.muted">
                        Spent average: {formatMinutes(Math.round(avgTimeSpentMn))}/task
                    </Text>
                </VStack>
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
