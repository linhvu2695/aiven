import { Box, HStack, VStack, IconButton } from "@chakra-ui/react";
import { useState } from "react";
import { FaSitemap, FaColumns, FaStream } from "react-icons/fa";
import { Tooltip } from "@/components/ui/tooltip";
import { WorkTaskTreePanel, WorkTaskListPanel, WorkParticipantsPanel, WorkKanbanPanel, WORK_VIEW_MODES, type WorkViewMode } from "@/components/work";
import { WorkGanttPanel } from "@/components/work/work-gantt-panel";
import { WorkProvider } from "@/context/work-ctx";
import { FaPeopleGroup } from "react-icons/fa6";

const VIEW_MODE_ICONS: Record<WorkViewMode, React.ReactNode> = {
    hierarchy: <FaSitemap />,
    participants: <FaPeopleGroup />,
    kanban: <FaColumns />,
    gantt: <FaStream />,
};

const WorkPageContent = () => {
    const [viewMode, setViewMode] = useState<WorkViewMode>("hierarchy");

    return (
        <HStack h="100vh" overflow="hidden" gap={0} align="stretch">
            {/* Left panel: task list */}
            <Box w="360px" flexShrink={0}>
                <WorkTaskListPanel />
            </Box>

            {/* Mode toolbar */}
            <VStack
                py={4}
                px={1}
                gap={1}
                borderRightWidth="1px"
                borderColor="border.default"
                bg="bg.subtle"
                flexShrink={0}
            >
                {WORK_VIEW_MODES.map((mode) => (
                    <Tooltip key={mode.id} content={mode.label} positioning={{ placement: "right" }}>
                        <IconButton
                            aria-label={mode.label}
                            variant={viewMode === mode.id ? "solid" : "ghost"}
                            size="sm"
                            onClick={() => setViewMode(mode.id)}
                        >
                            {VIEW_MODE_ICONS[mode.id]}
                        </IconButton>
                    </Tooltip>
                ))}
            </VStack>

            {/* Right panel: content based on mode */}
            <Box flex={1} h="100%" overflow="hidden">
                {viewMode === "hierarchy" && <WorkTaskTreePanel />}
                {viewMode === "participants" && <WorkParticipantsPanel />}
                {viewMode === "kanban" && <WorkKanbanPanel />}
                {viewMode === "gantt" && <WorkGanttPanel />}
            </Box>
        </HStack>
    );
};

export const WorkPage = () => (
    <WorkProvider>
        <WorkPageContent />
    </WorkProvider>
);

export default WorkPage;
