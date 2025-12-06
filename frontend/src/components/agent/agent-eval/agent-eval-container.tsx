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
import { useAgentEval } from "@/context/agent-eval-ctx";
import { Tooltip } from "../../ui";
import { AgentEvalChat } from "./agent-eval-chat";
import { AgentEvalLlmJudge } from "./agent-eval-llm-judge";
import { AgentEvalTrajectoryMatch } from "./agent-eval-trajectory-match";

type EvalMode = "llm-judge" | "trajectory";

interface TabButtonProps {
    tab: EvalMode;
    label: string;
    currentTab: EvalMode;
    onClick: () => void;
}

const TabButton = ({ tab, label, currentTab, onClick }: TabButtonProps) => {
    const isActive = currentTab === tab;
    return (
        <Button
            onClick={onClick}
            borderRadius="8px 8px 0 0"
            bg={isActive ? "teal.500" : "white"}
            border="none"
            borderBottom={isActive ? "none" : "2px solid"}
            px={6}
            py={3}
            _hover={{
                bg: isActive ? "teal.500" : "teal.100",
            }}
            boxShadow={isActive ? "0 2px 4px rgba(0, 0, 0, 0.1)" : "none"}
            transition="all 0.2s"
        >
            {label}
        </Button>
    );
};

export const AgentEvalContainer = () => {
    const { agent } = useAgent();
    const {
        resetMessages,
        setJudgeAgent,
        setTrajectoryMatch,
        setToolArgsMatch,
        setExpectedFunctionCalls,
    } = useAgentEval();
    const [evalMode, setEvalMode] = useState<EvalMode>("llm-judge");

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
                display="flex"
                flexDirection="column"
                gap={4}
            >
                <HStack className="agent-eval-input" flex={1} minH={0}>
                    <AgentEvalChat />

                    <Box
                        flex={1}
                        h="100%"
                        display="flex"
                        flexDirection="column"
                    >
                        {/* Tab buttons */}
                        <Box mb={0}>
                            <HStack gap={2} align="flex-end">
                                <TabButton
                                    tab="llm-judge"
                                    label="LLM As a Judge"
                                    currentTab={evalMode}
                                    onClick={() => setEvalMode("llm-judge")}
                                />
                                <TabButton
                                    tab="trajectory"
                                    label="Trajectory"
                                    currentTab={evalMode}
                                    onClick={() => setEvalMode("trajectory")}
                                />
                            </HStack>
                            <Box h="2px" bg="teal.500" />
                        </Box>

                        <Box flex={1} minH={0} p={4}>
                            {evalMode === "llm-judge" && <AgentEvalLlmJudge />}
                            {evalMode === "trajectory" && (
                                <AgentEvalTrajectoryMatch />
                            )}
                        </Box>
                    </Box>
                </HStack>

                <HStack className="agent-eval-buttons" gap={4}>
                    {/* Evaluate button */}
                    <Button
                        w="100%"
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
                        onClick={() => {
                            // TODO: Implement evaluate logic
                        }}
                    >
                        Evaluate <FaPlay />
                    </Button>

                    {/* Reset button */}
                    <Tooltip content="Reset">
                        <IconButton
                            aria-label={"Reset"}
                            onClick={() => {
                                resetMessages();
                                setJudgeAgent(null);
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
                    overflowY="auto"
                    p={4}
                >
                    <Heading size="lg">Result</Heading>
                </Stack>
            </Stack>
        </Container>
    );
};
