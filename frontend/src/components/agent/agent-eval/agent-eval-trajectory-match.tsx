import {
    Box,
    HStack,
    Text,
    Button,
    IconButton,
    VStack,
    useDisclosure,
} from "@chakra-ui/react";
import { FaPlus, FaTrash } from "react-icons/fa";
import { useAgentEval, type TrajectoryMatch, type ToolArgsMatch } from "@/context/agent-eval-ctx";
import { Dropdown } from "../../ui/dropdown";
import { FunctionSelectionDialog } from "./function-selection-dialog";

export interface MCPFunction {
    name: string;
    description: string | null;
    inputSchema: Record<string, any> | null;
    outputSchema: Record<string, any> | null;
}

export const AgentEvalTrajectoryMatch = () => {
    const {
        trajectoryMatch,
        setTrajectoryMatch,
        toolArgsMatch,
        setToolArgsMatch,
        expectedToolCalls,
        setExpectedToolCalls,
    } = useAgentEval();

    const {
        open: isFunctionDialogOpen,
        onOpen: onFunctionDialogOpen,
        onClose: onFunctionDialogClose,
    } = useDisclosure();

    const handleRemoveToolCall = (id: string) => {
        setExpectedToolCalls(expectedToolCalls.filter((tc) => tc.id !== id));
    };

    return (
        <>
            <Box
                h="100%"
                display="flex"
                flexDirection="column"
                gap={4}
            >
                {/* Configuration dropdowns */}
                <HStack gap={4} align="flex-end">
                    <Dropdown
                        title="Trajectory match"
                        value={trajectoryMatch}
                        onValueChange={(value) =>
                            setTrajectoryMatch(value as TrajectoryMatch)
                        }
                        options={[
                            {
                                value: "strict",
                                label: "Strict",
                            },
                            {
                                value: "unordered",
                                label: "Unordered",
                            },
                            {
                                value: "superset",
                                label: "Superset",
                            },
                            {
                                value: "subset",
                                label: "Subset",
                            },
                        ]}
                        flex={1}
                    />
                    <Dropdown
                        title="Tool args match"
                        value={toolArgsMatch}
                        onValueChange={(value) =>
                            setToolArgsMatch(value as ToolArgsMatch)
                        }
                        options={[
                            {
                                value: "ignore",
                                label: "Ignore",
                            },
                            {
                                value: "strict",
                                label: "Strict",
                            },
                            {
                                value: "superset",
                                label: "Superset",
                            },
                            {
                                value: "subset",
                                label: "Subset",
                            },
                        ]}
                        flex={1}
                    />
                </HStack>

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
                        <Text>Add Expected Tool Call</Text>
                    </HStack>
                </Button>

                {/* Expected tool calls list */}
                {expectedToolCalls.length > 0 && (
                    <VStack
                        align="stretch"
                        gap={2}
                        maxH="300px"
                        overflowY="auto"
                    >
                        {expectedToolCalls.map((toolCall, index) => {
                            return (
                                <Box
                                    key={toolCall.id}
                                    p={3}
                                    border="1px solid"
                                    borderColor="gray.200"
                                    borderRadius="md"
                                    display="flex"
                                    justifyContent="space-between"
                                    alignItems="center"
                                    _dark={{
                                        borderColor: "gray.700",
                                    }}
                                >
                                    <HStack gap={2}>
                                        <Text
                                            fontWeight="semibold"
                                            color="gray.500"
                                        >
                                            {index + 1}.
                                        </Text>
                                        <Text fontWeight="semibold">
                                            {toolCall.toolName}
                                        </Text>
                                    </HStack>
                                    <IconButton
                                        aria-label="Remove tool call"
                                        size="sm"
                                        variant="ghost"
                                        colorPalette="red"
                                        onClick={() =>
                                            handleRemoveToolCall(toolCall.id)
                                        }
                                    >
                                        <FaTrash />
                                    </IconButton>
                                </Box>
                            );
                        })}
                    </VStack>
                )}
            </Box>

            {/* Function Selection Dialog */}
            <FunctionSelectionDialog
                isOpen={isFunctionDialogOpen}
                onClose={onFunctionDialogClose}
            />
        </>
    );
};

