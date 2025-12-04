import {
    Box,
    HStack,
    Text,
    Button,
    IconButton,
    VStack,
    useDisclosure,
    Dialog,
    Portal,
    CloseButton,
} from "@chakra-ui/react";
import { useState, useEffect } from "react";
import { FaPlus, FaTrash } from "react-icons/fa";
import { useAgentEval, type TrajectoryMatch, type ToolArgsMatch, type ExpectedToolCall } from "@/context/agent-eval-ctx";
import { type Tool } from "@/context/agent-ctx";
import { Dropdown } from "../../ui/dropdown";
import { ToolSelectionGrid } from "../tool-selection-grid";
import { BASE_URL } from "@/App";

export const AgentEvalTrajectoryMatch = () => {
    const {
        trajectoryMatch,
        setTrajectoryMatch,
        toolArgsMatch,
        setToolArgsMatch,
        expectedToolCalls,
        setExpectedToolCalls,
    } = useAgentEval();

    const [availableTools, setAvailableTools] = useState<Tool[]>([]);
    const {
        open: isToolDialogOpen,
        onOpen: onToolDialogOpen,
        onClose: onToolDialogClose,
    } = useDisclosure();
    const [selectedToolId, setSelectedToolId] = useState<string>("");

    // Fetch available tools
    useEffect(() => {
        const fetchAvailableTools = async (): Promise<Tool[]> => {
            try {
                const response = await fetch(BASE_URL + "/api/tool/search", {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                if (!response.ok)
                    throw new Error("Failed to fetch available tools");

                const data = await response.json();
                return data.tools;
            } catch (error) {
                console.error("Error fetching available tools:", error);
                return [];
            }
        };

        fetchAvailableTools().then(setAvailableTools);
    }, []);

    const handleAddToolCall = () => {
        setSelectedToolId("");
        onToolDialogOpen();
    };

    const handleToolSelect = (toolId: string) => {
        const tool = availableTools.find((t) => t.id === toolId);
        if (tool) {
            const newToolCall: ExpectedToolCall = {
                id: `tool-call-${Date.now()}`,
                toolId: tool.id,
                toolName: tool.name,
                args: {},
            };
            setExpectedToolCalls([...expectedToolCalls, newToolCall]);
            onToolDialogClose();
        }
    };

    const handleRemoveToolCall = (id: string) => {
        setExpectedToolCalls(expectedToolCalls.filter((tc) => tc.id !== id));
    };

    // Always return false to allow selecting the same tool multiple times
    const isToolSelected = (_toolId: string) => {
        return false;
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
                    onClick={handleAddToolCall}
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
                            const tool = availableTools.find(
                                (t) => t.id === toolCall.toolId
                            );
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
                                            {tool?.emoji} {toolCall.toolName}
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

            {/* Tool Selection Dialog */}
            <Dialog.Root
                open={isToolDialogOpen}
                onOpenChange={(e) => {
                    if (!e.open) {
                        onToolDialogClose();
                    }
                }}
                size="xl"
                placement="center"
            >
                <Portal>
                    <Dialog.Backdrop />
                    <Dialog.Positioner>
                        <Dialog.Content>
                            <Dialog.Header>
                                <Dialog.Title>
                                    Select Expected Tool Call
                                </Dialog.Title>
                            </Dialog.Header>

                            <Dialog.Body>
                                <ToolSelectionGrid
                                    availableTools={availableTools}
                                    isToolAssigned={isToolSelected}
                                    selectedToolIds={
                                        selectedToolId
                                            ? new Set([selectedToolId])
                                            : new Set()
                                    }
                                    onToggleToolSelection={(toolId) => {
                                        setSelectedToolId(toolId);
                                        handleToolSelect(toolId);
                                    }}
                                    onRemoveTool={() => {}}
                                />
                            </Dialog.Body>

                            <Dialog.CloseTrigger asChild>
                                <CloseButton size="sm" />
                            </Dialog.CloseTrigger>
                        </Dialog.Content>
                    </Dialog.Positioner>
                </Portal>
            </Dialog.Root>
        </>
    );
};

