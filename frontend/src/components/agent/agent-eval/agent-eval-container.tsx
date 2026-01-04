import {
    Container,
    Stack,
    Text,
    Heading,
    HStack,
    Box,
    Button,
    IconButton,
} from "@chakra-ui/react";
import { useState } from "react";
import { FaScaleBalanced } from "react-icons/fa6";
import { FaPlay, FaUndo } from "react-icons/fa";
import { useAgent } from "@/context/agent-ctx";
import { useAgentEval, type ToolArgsMatch, type TrajectoryMatch } from "@/context/agent-eval-ctx";
import { toaster, Tooltip } from "../../ui";
import { AgentEvalChat } from "./agent-eval-chat";
import { AgentEvalConfig } from "./agent-eval-config";
import { AgentEvalResult } from "./agent-eval-result";
import { BASE_URL } from "@/App";
import type { ChatMessageInfo } from "@/components/chat/chat-message-info";

// Helper function to serialize ChatMessageInfo to backend ChatMessage format
const serializeMessage = (msg: ChatMessageInfo) => {    
    return {
        role: msg.role,
        content: String(msg.content),
    }
};

// Helper function to build expected trajectory from messages and expected function calls
const buildExpectedTrajectory = (
    messages: ChatMessageInfo[],
    expectedFunctionCalls: Array<{
        function: { name: string };
        expectedInput: Record<string, any>;
        expectedOutput: Record<string, any>;
    }>
) => {
    // Input chat history
    const trajectory: Array<{
        role: string;
        content: string;
        tool_calls?: Array<{
            function: {
                name: string;
                arguments: string;
            };
        }>;
    }> = messages.map(serializeMessage);

    // Expected function calls
    if (expectedFunctionCalls.length > 0) {
        // One assistant message with all tool_calls
        trajectory.push({
            role: "assistant",
            content: "",
            tool_calls: expectedFunctionCalls.map((call) => ({
                function: {
                    name: call.function.name,
                    arguments: JSON.stringify(call.expectedInput),
                },
            })),
        });

        // All tool responses
        expectedFunctionCalls.forEach((call) => {
            trajectory.push({
                role: "tool",
                content: JSON.stringify(call.expectedOutput),
            });
        });
    }
    
    // Final assistant response
    trajectory.push({
        role: "assistant",
        content: "",
    });
    
    return trajectory;
};

// Handler function for evaluating the agent
const handleEvaluate = async (
    agent: { id: string } | null,
    messages: ChatMessageInfo[] | undefined,
    expectedFunctionCalls: Array<{
        function: { name: string };
        expectedInput: Record<string, any>;
        expectedOutput: Record<string, any>;
    }>,
    trajectoryMatchMode: TrajectoryMatch,
    toolArgsMatchMode: ToolArgsMatch,
    llmAsJudge: boolean,
    setIsEvaluating: (isEvaluating: boolean) => void,
    setEvalResult: (result: any) => void
) => {
    if (!agent?.id) {
        toaster.create({
            description: "Agent ID is required for evaluation",
            type: "error",
        });
        return;
    }
    
    if (!messages || messages.length === 0) {
        toaster.create({
            description: "Empty input messages",
            type: "error",
        });
        return;
    }
    
    setIsEvaluating(true);
    
    try {
        // Serialize input messages
        const inputMessages = messages.map(serializeMessage);
        
        // Build expected trajectory (input messages -> tool calls -> final response)
        const expectedTrajectory = buildExpectedTrajectory(messages, expectedFunctionCalls);
        
        // Make API call
        const response = await fetch(BASE_URL + "/api/agent/evaluate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                agent_id: agent.id,
                input_messages: inputMessages,
                expected_trajectory: expectedTrajectory,
                trajectory_match_mode: trajectoryMatchMode,
                tool_args_match_mode: toolArgsMatchMode,
                llm_as_a_judge: llmAsJudge,
            }),
        });
        
        if (!response.ok) {
            toaster.create({
                description: `Failed to evaluate agent: HTTP ${response.status}: ${response.statusText}`,
                type: "error",
            });
            return;
        }
        
        const result = await response.json();
        console.log("Evaluation result:", result);

        // Store result in context
        setEvalResult(result);

        toaster.create({
            description: "Evaluation completed successfully",
            type: "success",
        });
    } catch (error) {
        console.error("Error evaluating agent:", error);
        toaster.create({
            description: `Failed to evaluate agent`,
            type: "error",
        });
    } finally {
        setIsEvaluating(false);
    }
};

export const AgentEvalContainer = () => {
    const { agent } = useAgent();
    const {
        messages,
        expectedFunctionCalls,
        resetMessages,
        llmAsJudge,
        setLlmAsJudge,
        trajectoryMatch,
        toolArgsMatch,
        setTrajectoryMatch,
        setToolArgsMatch,
        setExpectedFunctionCalls,
        setEvalResult,
    } = useAgentEval();
    const [isEvaluating, setIsEvaluating] = useState(false);

    return (
        <Container
            height="100%"
            display="flex"
            flexDirection="column"
            justifyContent="space-between"
            data-testid="agent-eval-container"
        >
            {/* Header */}
            <Box p={4} borderBottom="1px" borderColor="border.default">
                <Heading size="xl" color="fg.default">
                    <HStack gap={3}>
                        <FaScaleBalanced color="teal.500" />
                        <Text>Evaluate {agent?.name || "Agent"}</Text>
                    </HStack>
                </Heading>
            </Box>

            <Stack
                className="agent-eval-content"
                flex={1}
                minH={0}
                display="flex"
                flexDirection="column"
                gap={4}
            >
                <HStack className="agent-eval-input" flex={1} minH={400} minW={0}>
                    <AgentEvalChat />

                    <Box
                        flex={1}
                        h="100%"
                        display="flex"
                        flexDirection="column"
                        minW={0}
                        p={4}
                    >
                        <AgentEvalConfig />
                    </Box>
                </HStack>

                <HStack className="agent-eval-buttons" gap={4} flexShrink={0}>
                    {/* Evaluate button */}
                    <Button
                        w="95%"
                        borderRadius="12px"
                        bgGradient="to-r"
                        gradientFrom="teal.700"
                        gradientTo="teal.500"
                        _hover={{
                            bgGradient: "to-r",
                            gradientFrom: "teal.600",
                            gradientTo: "teal.400",
                            boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
                        }}
                        onClick={() => handleEvaluate(agent, messages, expectedFunctionCalls, trajectoryMatch, toolArgsMatch, llmAsJudge, setIsEvaluating, setEvalResult)}
                        loading={isEvaluating}
                        disabled={isEvaluating || !agent?.id || !messages || messages.length === 0}
                    >
                        EVALUATE - {llmAsJudge ? "🤖 LLM As a Judge" : "💫 Trajectory Match"} <FaPlay />
                    </Button>

                    {/* Reset button */}
                    <Tooltip content="Reset">
                        <IconButton
                            aria-label={"Reset"}
                            onClick={() => {
                                resetMessages();
                                setLlmAsJudge(false);
                                setTrajectoryMatch("strict");
                                setToolArgsMatch("ignore");
                                setExpectedFunctionCalls([]);
                            }}
                            size={"sm"}
                            variant="solid"
                            _hover={{
                                transform: "scale(1.1)",
                            }}
                            transition="transform 0.2s"
                        >
                            <FaUndo />
                        </IconButton>
                    </Tooltip>
                </HStack>

                <Stack
                    className="agent-eval-result"
                    flex={1}
                    minH={0}
                    maxH="100%"
                    overflowY="auto"
                >
                    <AgentEvalResult />
                </Stack>
            </Stack>
        </Container>
    );
};
