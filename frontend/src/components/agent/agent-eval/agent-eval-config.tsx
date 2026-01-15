import { Box, HStack, Text, Button, useDisclosure, VStack, Separator, Checkbox } from "@chakra-ui/react";
import { FaPlus } from "react-icons/fa";
import { useAgentEval, type TrajectoryMatch, type ToolArgsMatch } from "@/context/agent-eval-ctx";
import { ExpectedFunctionCallItem } from "./expected-function-call-item";
import { FunctionSelectionDialog } from "./function-selection-dialog";
import { Dropdown } from "../../ui/dropdown";

export const AgentEvalConfig = () => {
    const {
        llmAsJudge,
        setLlmAsJudge,
        trajectoryMatch,
        setTrajectoryMatch,
        toolArgsMatch,
        setToolArgsMatch,
        expectedFunctionCalls,
    } = useAgentEval();
    
    const {
        open: isFunctionDialogOpen,
        onOpen: onFunctionDialogOpen,
        onClose: onFunctionDialogClose,
    } = useDisclosure();

    return (
        <>
            <Box
                h="100%"
                display="flex"
                flexDirection="column"
                gap={4}
            >
                {/* LLM as Judge Checkbox */}
                <Checkbox.Root
                    checked={llmAsJudge}
                    onCheckedChange={(details) => setLlmAsJudge(details.checked as boolean)}
                    size="lg"
                >
                    <Checkbox.HiddenInput />
                    <Checkbox.Control />
                    <Checkbox.Label>
                        <Text fontSize="md" fontWeight="medium">
                            Use LLM as Judge
                        </Text>
                    </Checkbox.Label>
                </Checkbox.Root>

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
                                label: "Actual includes Expected",
                            },
                            {
                                value: "subset",
                                label: "Expected includes Actual",
                            },
                        ]}
                        flex={1}
                        disabled={llmAsJudge}
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
                                value: "exact",
                                label: "Exact",
                            },
                        ]}
                        flex={1}
                        disabled={llmAsJudge}
                    />
                </HStack>

                {/* Separator */}
                <Separator />

                {/* Add button */}
                <Button
                    onClick={onFunctionDialogOpen}
                    variant="outline"
                    colorPalette="primary"
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

            {/* Function Selection Dialog */}
            <FunctionSelectionDialog
                isOpen={isFunctionDialogOpen}
                onClose={onFunctionDialogClose}
            />
        </>
    );
};

