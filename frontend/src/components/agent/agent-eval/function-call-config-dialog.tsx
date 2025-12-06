import {
    Dialog,
    Portal,
    CloseButton,
    VStack,
    Button,
    HStack,
    Text,
    Separator,
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
    const { expectedFunctionCalls, setExpectedFunctionCalls } = useAgentEval();
    const [expectedInput, setExpectedInput] = useState<Record<string, any>>({});
    const [expectedOutput, setExpectedOutput] = useState<Record<string, any>>({});

    // Initialize values from functionCall when dialog opens
    useEffect(() => {
        if (isOpen) {
            setExpectedInput(functionCall.expectedInput || {});
            setExpectedOutput(functionCall.expectedOutput || {});
        }
    }, [isOpen, functionCall]);

    const handleSave = () => {
        // Update the function call with new values
        const updatedFunctionCalls = expectedFunctionCalls.map((fc) =>
            fc.id === functionCall.id
                ? {
                      ...fc,
                      expectedInput,
                      expectedOutput,
                  }
                : fc
        );

        setExpectedFunctionCalls(updatedFunctionCalls);
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
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content>
                        <Dialog.Header>
                            <Dialog.Title>
                                <HStack gap={2} align="center">
                                    <Text>Configure expectations:</Text>
                                    <CodeText>{functionCall.function.name}</CodeText>
                                </HStack>
                            </Dialog.Title>
                        </Dialog.Header>

                        <Dialog.Body>
                            <VStack gap={6} align="stretch">
                                {/* Expected Input */}
                                <SchemaFormSection
                                    title="Expected Input"
                                    schema={functionCall.function.inputSchema}
                                    values={expectedInput}
                                    onChange={setExpectedInput}
                                />

                                <Separator />

                                {/* Expected Output */}
                                <SchemaFormSection
                                    title="Expected Output"
                                    schema={functionCall.function.outputSchema}
                                    values={expectedOutput}
                                    onChange={setExpectedOutput}
                                />
                            </VStack>
                        </Dialog.Body>

                        <Dialog.Footer>
                            <HStack gap={2}>
                                <Button variant="outline" onClick={onClose}>
                                    Cancel
                                </Button>
                                <Button
                                    colorPalette="teal"
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

