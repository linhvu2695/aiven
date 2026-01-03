import {
    Box,
    HStack,
    Text,
    Button,
    VStack,
    useDisclosure,
} from "@chakra-ui/react";
import { FaPlus } from "react-icons/fa";
import { useAgentEval, type TrajectoryMatch, type ToolArgsMatch } from "@/context/agent-eval-ctx";
import { Dropdown } from "../../ui/dropdown";
import { FunctionSelectionDialog } from "./function-selection-dialog";
import { ExpectedFunctionCallItem } from "./expected-function-call-item";

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
                                value: "exact",
                                label: "Exact",
                            }
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

