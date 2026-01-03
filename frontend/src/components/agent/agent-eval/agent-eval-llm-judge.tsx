import { Box, HStack, Text, Button, Avatar, useDisclosure, VStack, Separator, IconButton } from "@chakra-ui/react";
import { FaPlus, FaRobot, FaTimes } from "react-icons/fa";
import { useAgentEval } from "@/context/agent-eval-ctx";
import { AgentSelectionDialog } from "../agent-selection-dialog";
import type { Agent } from "@/context/agent-ctx";
import { ExpectedFunctionCallItem } from "./expected-function-call-item";
import { FunctionSelectionDialog } from "./function-selection-dialog";

export const AgentEvalLlmJudge = () => {
    const { judgeAgent, setJudgeAgent, expectedFunctionCalls } = useAgentEval();
    const { open, onOpen, onClose } = useDisclosure();
    
    const {
        open: isFunctionDialogOpen,
        onOpen: onFunctionDialogOpen,
        onClose: onFunctionDialogClose,
    } = useDisclosure();

    const handleJudgeAgentSelect = (selectedAgent: Agent) => {
        setJudgeAgent(selectedAgent);
        onClose();
    };

    return (
        <>
            <Box
                h="100%"
                display="flex"
                flexDirection="column"
                gap={4}
            >
                {judgeAgent ? (
                    <Box>
                        <HStack mb={2} gap={3}>
                            <Box position="relative" display="inline-block">
                                <Avatar.Root size="md">
                                    <Avatar.Image src={judgeAgent.avatar_image_url} />
                                    <Avatar.Fallback name={judgeAgent.name} />
                                </Avatar.Root>
                                <IconButton
                                    aria-label="Remove judge agent"
                                    size="xs"
                                    variant="ghost"
                                    position="absolute"
                                    top={-4}
                                    right={-4}
                                    color="red.500"
                                    zIndex={10}
                                    onClick={() => setJudgeAgent(null)}
                                    opacity={0.7}
                                    _hover={{ opacity: 1 }}
                                    bg="transparent"
                                    borderRadius="full"
                                >
                                    <FaTimes />
                                </IconButton>
                            </Box>
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

                {/* Separator */}
                <Separator />

                {/* Add button */}
                <Button
                    onClick={onFunctionDialogOpen}
                    variant="outline"
                    colorPalette="teal"
                    borderRadius="12px"
                    w="fit-content"
                >
                    <HStack gap={2}>
                        <FaPlus />
                        <Text>Add Expected Function Call</Text>
                    </HStack>
                </Button>

                {/* Expected function calls list */}
                {expectedFunctionCalls.length > 0 && (
                    <VStack
                        align="stretch"
                        gap={2}
                        maxH="300px"
                        overflowY="auto"
                    >
                        {expectedFunctionCalls.map((functionCall, index) => (
                            <ExpectedFunctionCallItem
                                key={functionCall.id}
                                functionCall={functionCall}
                                index={index}
                            />
                        ))}
                    </VStack>
                )}
            </Box>

            {/* Select Judge Agent Dialog */}
            <AgentSelectionDialog
                open={open}
                onClose={onClose}
                title="Select a Judge Agent"
                onAgentSelect={handleJudgeAgentSelect}
            />

            {/* Function Selection Dialog */}
            <FunctionSelectionDialog
                isOpen={isFunctionDialogOpen}
                onClose={onFunctionDialogClose}
            />
        </>
    );
};

