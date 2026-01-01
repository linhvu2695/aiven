import {
    Box,
    Stack,
    Text,
    Heading,
    Badge,
    VStack,
    HStack,
    Code,
    Button,
} from "@chakra-ui/react";
import { FaCheckCircle, FaTimesCircle, FaChevronDown, FaChevronUp } from "react-icons/fa";
import { useAgentEval } from "@/context/agent-eval-ctx";
import type { EvalResult } from "@/context/agent-eval-ctx";
import { useState } from "react";

const TrajectoryItem = ({ item, index }: { item: EvalResult["actual_trajectory"][0]; index: number }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    
    return (
        <Box
            p={3}
            borderRadius="8px"
            border="1px solid"
            borderColor="border.default"
            bg="bg.muted"
        >
            {/* Header */}
            <HStack justify="space-between" mb={2}>
                <HStack gap={2}>
                    {/* Emoji for role */}
                    <Text>{
                        item.role === "user" ? "👤" 
                        : item.role === "assistant" ? "🤖" 
                        : item.role === "system" ? "⚙"
                        : item.role === "tool" ? "🔧"
                        : "❓"
                    }</Text>
                    <Badge bg="fg.subtle">
                        {item.role}
                    </Badge>
                    <Text fontSize="sm" color="fg.muted">
                        Step {index + 1}
                    </Text>
                </HStack>
                {(item.content.length > 100 || item.tool_calls) && (
                    <Button
                        size="xs"
                        variant="ghost"
                        onClick={() => setIsExpanded(!isExpanded)}
                    >
                        {isExpanded ? <FaChevronUp /> : <FaChevronDown />}
                    </Button>
                )}
            </HStack>
            
            {/* Content */}
            {item.content && (
                <Box>
                    <Text
                        fontSize="sm"
                        color="fg.default"
                        whiteSpace="pre-wrap"
                        wordBreak="break-word"
                        style={
                            !isExpanded
                                ? {
                                      display: "-webkit-box",
                                      WebkitLineClamp: 3,
                                      WebkitBoxOrient: "vertical",
                                      overflow: "hidden",
                                  }
                                : undefined
                        }
                    >
                        {item.content || "(empty)"}
                    </Text>
                </Box>
            )}
            
            {/* Tool Calls */}
            {item.tool_calls && item.tool_calls.length > 0 && (
                <Box mt={2}>
                    <Text fontSize="xs" fontWeight="bold" color="fg.muted">
                        Tool Calls:
                    </Text>
                    {item.tool_calls.map((toolCall, idx) => (
                        <Box
                            key={idx}
                            p={2}
                            borderRadius="4px"
                            bg="bg.subtle"
                            mt={1}
                        >
                            <Text fontSize="xs" fontWeight="semibold" color="fg.default">
                                {toolCall.function.name}
                            </Text>
                            <Code fontSize="xs" mt={1} display="block" whiteSpace="pre-wrap">
                                {toolCall.function.arguments}
                            </Code>
                        </Box>
                    ))}
                </Box>
            )}
        </Box>
    );
};

const EmptyAgentEvalResult = () => {
    return (
        <Box p={4}>
            <Text color="fg.muted" textAlign="center">
                No evaluation result yet.
            </Text>
        </Box>
    );
};

export const AgentEvalResult = () => {
    const { evalResult } = useAgentEval();
    const [isTrajectoryExpanded, setIsTrajectoryExpanded] = useState(false);

    if (!evalResult) {
        return (
            <EmptyAgentEvalResult />
        );
    }

    const isPass = evalResult.score;
    const statusColor = isPass ? "green" : "red";
    const StatusIcon = isPass ? FaCheckCircle : FaTimesCircle;

    return (
        <Stack gap={4} p={4}>
            {/* Header with status */}
            <HStack justify="space-between" align="center">
                <Heading size="lg">Evaluation Result</Heading>
                <HStack gap={2}>
                    <StatusIcon color={isPass ? "green" : "red"} size={24} />
                    <Badge
                        colorScheme={statusColor}
                        fontSize="md"
                        px={3}
                        py={1}
                        borderRadius="full"
                    >
                        {isPass ? "PASS" : "FAIL"}
                    </Badge>
                </HStack>
            </HStack>

            {/* Summary */}
            <Box
                p={4}
                borderRadius="8px"
                border="2px solid"
                borderColor={`${statusColor}`}
            >
                <VStack align="stretch" gap={2}>
                    {/* Evaluation Key */}
                    <HStack>
                        <Text fontWeight="semibold" color="fg.default">
                            Evaluation Key:
                        </Text>
                        <Code fontSize="sm">{evalResult.key}</Code>
                    </HStack>
                    
                    {/* Comment */}
                    {evalResult.comment && (
                        <HStack>
                            <Text fontWeight="semibold" color="fg.default">
                                Comment:
                            </Text>
                            <Text color="fg.muted">
                                {evalResult.comment}
                            </Text>
                        </HStack>
                    )}
                    
                    {/* Message */}
                    <HStack>
                        <Text fontWeight="semibold" color="fg.default">
                            Message:
                        </Text>
                        <Text color="fg.muted">
                            {evalResult.message}
                        </Text>
                    </HStack>
                </VStack>
            </Box>

            {/* Actual Trajectory */}
            <Box>
                <Button
                    variant="ghost"
                    w="100%"
                    justifyContent="space-between"
                    p={3}
                    borderRadius="8px"
                    borderColor="border.default"
                    _hover={{ bg: "bg.subtle" }}
                    onClick={() => setIsTrajectoryExpanded(!isTrajectoryExpanded)}
                >
                    <HStack>
                        <Heading size="md">Actual Trajectory</Heading>
                        <Badge colorScheme="blue">
                            {evalResult.actual_trajectory.length} steps
                        </Badge>
                    </HStack>
                    {isTrajectoryExpanded ? <FaChevronUp /> : <FaChevronDown />}
                </Button>
                
                {isTrajectoryExpanded && (
                    <Stack gap={3} mt={3}>
                        {evalResult.actual_trajectory.map((item, index) => (
                            <TrajectoryItem key={index} item={item} index={index} />
                        ))}
                    </Stack>
                )}
            </Box>
        </Stack>
    );
};

