import { Box, HStack, Text, Button, Avatar, useDisclosure } from "@chakra-ui/react";
import { FaRobot } from "react-icons/fa";
import { useAgentEval } from "@/context/agent-eval-ctx";
import { AgentSelectionDialog } from "../agent-selection-dialog";
import type { Agent } from "@/context/agent-ctx";

export const AgentEvalLlmJudge = () => {
    const { judgeAgent, setJudgeAgent } = useAgentEval();
    const { open, onOpen, onClose } = useDisclosure();

    const handleJudgeAgentSelect = (selectedAgent: Agent) => {
        setJudgeAgent(selectedAgent);
        onClose();
    };

    return (
        <>
            <Box h="100%">
                {judgeAgent ? (
                    <Box>
                        <HStack mb={2} gap={3}>
                            <Avatar.Root size="md">
                                <Avatar.Image src={judgeAgent.avatar_image_url} />
                                <Avatar.Fallback name={judgeAgent.name} />
                            </Avatar.Root>
                            <Text fontSize="lg" fontWeight="semibold">
                                Judge: {judgeAgent.name}
                            </Text>
                        </HStack>
                        <Button
                            onClick={onOpen}
                            variant="outline"
                            w="50%"
                            colorPalette="teal"
                            borderRadius={"12px"}
                        >
                            Change Judge Agent
                        </Button>
                    </Box>
                ) : (
                    <Button
                        onClick={onOpen}
                        variant="outline"
                        w="50%"
                        colorPalette="teal"
                        borderRadius={"12px"}
                    >
                        <HStack gap={2}>
                            <FaRobot />
                            <Text>Select Judge Agent</Text>
                        </HStack>
                    </Button>
                )}
            </Box>

            {/* Select Judge Agent Dialog */}
            <AgentSelectionDialog
                open={open}
                onClose={onClose}
                title="Select a Judge Agent"
                onAgentSelect={handleJudgeAgentSelect}
            />
        </>
    );
};

