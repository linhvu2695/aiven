import {
    Dialog,
    Portal,
    CloseButton,
    VStack,
    Button,
    HStack,
    Text,
    Separator,
    Badge,
    Box,
} from "@chakra-ui/react";
import { useState, useEffect } from "react";
import { useAgentEval, type ExpectedFunctionCall } from "@/context/agent-eval-ctx";
import { SchemaFormSection } from "./schema-form-section";
import { CodeText } from "@/components/ui";

interface FunctionCallConfigDialogProps {
    isOpen: boolean;
    onClose: () => void;
    functionCall: ExpectedFunctionCall;
}

export const FunctionCallConfigDialog = ({
    isOpen,
    onClose,
    functionCall,
}: FunctionCallConfigDialogProps) => {
    const { expectedFunctionCalls, setExpectedFunctionCalls, getMockedFunctionOutput, setMockedFunctionOutput, removeMockedFunctionOutput, mockedFunctionOutputs } = useAgentEval();
    const [expectedInput, setExpectedInput] = useState<Record<string, any>>({});
    const [mockOutput, setMockOutput] = useState<Record<string, any>>({});

    const functionName = functionCall?.function?.name || "";
    const isMocked = functionName in mockedFunctionOutputs;

    // Initialize values from functionCall and context when dialog opens
    useEffect(() => {
        if (isOpen) {
            setExpectedInput(functionCall.expectedInput || {});
            setMockOutput(getMockedFunctionOutput(functionName));
        }
    }, [isOpen, functionCall, functionName, getMockedFunctionOutput]);

    const handleSave = () => {
        // Update the function call with expected input
        const updatedFunctionCalls = expectedFunctionCalls.map((fc) =>
            fc.id === functionCall.id
                ? {
                      ...fc,
                      expectedInput,
                  }
                : fc
        );
        setExpectedFunctionCalls(updatedFunctionCalls);

        // Save mock output to context (applies to all calls of this function)
        setMockedFunctionOutput(functionName, mockOutput);

        onClose();
    };

    const handleClearMock = () => {
        removeMockedFunctionOutput(functionName);
        setMockOutput({});
        onClose();
    };

    return (
        <Dialog.Root
            open={isOpen}
            onOpenChange={(e) => {
                if (!e.open) {
                    onClose();
                }
            }}
            size="xl"
            placement="center"
        >
            <Portal>
                <Dialog.Backdrop/>
                <Dialog.Positioner>
                    <Dialog.Content>
                        <Dialog.Header>
                            <Dialog.Title>
                                <HStack gap={2} align="center">
                                    <Text>Configure expectations:</Text>
                                    <CodeText>{functionCall?.function?.name || ""}</CodeText>
                                </HStack>
                                <Text fontSize="xs" color="gray.500" fontStyle="italic">
                                    {functionCall?.function?.description || ""}
                                </Text>
                            </Dialog.Title>
                        </Dialog.Header>

                        <Dialog.Body maxH={"70vh"} overflowY="auto">
                            <VStack gap={6} align="stretch">
                                {/* Expected Input */}
                                <SchemaFormSection
                                    title="Expected Input"
                                    schema={functionCall?.function?.inputSchema || {}}
                                    values={expectedInput}
                                    onChange={setExpectedInput}
                                />

                                <Separator />

                                {/* Mock Output */}
                                <Box
                                    p={3}
                                    borderRadius="md"
                                    border="1px solid"
                                    borderColor={isMocked ? "orange.400" : "transparent"}
                                    bg={isMocked ? "orange.50" : "transparent"}
                                    _dark={{
                                        borderColor: isMocked ? "orange.500" : "transparent",
                                        bg: isMocked ? "orange.900/20" : "transparent",
                                    }}
                                >
                                    <VStack align="stretch" gap={2}>
                                        <HStack justify="space-between" align="center">
                                            {/* Mock Output title */}
                                            <HStack gap={2}>
                                                <Text fontWeight="semibold" fontSize="sm">Mock Output</Text>
                                                {isMocked && (
                                                    <Badge colorPalette="orange" size="sm" variant="solid">
                                                        MOCKED
                                                    </Badge>
                                                )}
                                            </HStack>

                                            {/* Clear Mock button */}
                                            {isMocked && (
                                                <Button
                                                    size="xs"
                                                    variant="outline"
                                                    colorPalette="red"
                                                    onClick={handleClearMock}
                                                >
                                                    Clear Mock
                                                </Button>
                                            )}
                                        </HStack>

                                        {/* Mock Output schema */}
                                        <SchemaFormSection
                                            title=""
                                            schema={functionCall?.function?.outputSchema || {}}
                                            values={mockOutput}
                                            onChange={setMockOutput}
                                        />
                                    </VStack>
                                </Box>
                            </VStack>
                        </Dialog.Body>

                        <Dialog.Footer>
                            <HStack gap={2}>
                                <Button variant="outline" onClick={onClose}>
                                    Cancel
                                </Button>
                                <Button
                                    colorPalette="primary"
                                    onClick={handleSave}
                                >
                                    Save
                                </Button>
                            </HStack>
                        </Dialog.Footer>

                        <Dialog.CloseTrigger asChild>
                            <CloseButton size="sm" />
                        </Dialog.CloseTrigger>
                    </Dialog.Content>
                </Dialog.Positioner>
            </Portal>
        </Dialog.Root>
    );
};

