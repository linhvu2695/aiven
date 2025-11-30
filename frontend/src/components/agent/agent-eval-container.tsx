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
import { FaScaleBalanced } from "react-icons/fa6";
import { FaPlay, FaUndo } from "react-icons/fa";
import { useAgent } from "@/context/agent-ctx";
import { useAgentEval } from "@/context/agent-eval-ctx";
import { Tooltip } from "../ui";
import { AgentEvalChat } from "./agent-eval-chat";

export const AgentEvalContainer = () => {
    const { agent } = useAgent();
    const { resetMessages } = useAgentEval();

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

            <Stack className="agent-eval-content" flex={1} display="flex" flexDirection="column" gap={4}>
                <HStack className="agent-eval-input" flex={1} minH={0}>
                    <AgentEvalChat />

                    <Box>
                        <Text>Input</Text>
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
                            onClick={resetMessages}
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

                <Stack className="agent-eval-result" flex={1} minH={0} overflowY="auto" p={4}>
                    <Heading size="lg">Result</Heading>
                </Stack>
            </Stack>
        </Container>
    );
};
