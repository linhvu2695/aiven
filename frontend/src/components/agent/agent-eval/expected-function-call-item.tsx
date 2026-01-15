import { Box, HStack, Text, IconButton, useDisclosure } from "@chakra-ui/react";
import { FaTrash, FaCog } from "react-icons/fa";
import { useAgentEval, type ExpectedFunctionCall } from "@/context/agent-eval-ctx";
import { FunctionCallConfigDialog } from "./function-call-config-dialog";

interface ExpectedFunctionCallItemProps {
    functionCall: ExpectedFunctionCall;
    index: number;
}

export const ExpectedFunctionCallItem = ({
    functionCall,
    index,
}: ExpectedFunctionCallItemProps) => {
    const { expectedFunctionCalls, setExpectedFunctionCalls } = useAgentEval();
    const {
        open: isConfigDialogOpen,
        onOpen: onConfigDialogOpen,
        onClose: onConfigDialogClose,
    } = useDisclosure();

    const handleRemoveFunctionCall = (id: string) => {
        setExpectedFunctionCalls(expectedFunctionCalls.filter((fc) => fc.id !== id));
    };

    return (
        <>
            <Box
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
                    <Text fontWeight="semibold" color="gray.500">
                        {index + 1}.
                    </Text>
                    <Text fontWeight="semibold">{functionCall.function.name}</Text>
                </HStack>
                <HStack gap={1}>
                    <IconButton
                        aria-label="Configure function call"
                        size="sm"
                        variant="ghost"
                        colorPalette="primary"
                        onClick={onConfigDialogOpen}
                    >
                        <FaCog />
                    </IconButton>
                    <IconButton
                        aria-label="Remove function call"
                        size="sm"
                        variant="ghost"
                        colorPalette="red"
                        onClick={() => handleRemoveFunctionCall(functionCall.id)}
                    >
                        <FaTrash />
                    </IconButton>
                </HStack>
            </Box>

            <FunctionCallConfigDialog
                isOpen={isConfigDialogOpen}
                onClose={onConfigDialogClose}
                functionCall={functionCall}
            />
        </>
    );
};

