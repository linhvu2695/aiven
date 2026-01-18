import {
    Box,
    VStack,
    HStack,
    Text,
    IconButton,
    Input,
    Badge,
} from "@chakra-ui/react";
import { useState } from "react";
import { FaPlus, FaTrash, FaCheck, FaTimes } from "react-icons/fa";
import { useAgentEval } from "@/context/agent-eval-ctx";
import { Tooltip } from "../../ui";
import { useColorMode } from "@/components/ui/color-mode";

interface TestSuiteItemProps {
    name: string;
    isSelected: boolean;
    hasResult: boolean;
    resultPassed?: boolean;
    onSelect: () => void;
    onDelete: () => void;
    onRename: (name: string) => void;
    canDelete: boolean;
}

const TestSuiteItem = ({
    name,
    isSelected,
    hasResult,
    resultPassed,
    onSelect,
    onDelete,
    onRename,
    canDelete,
}: TestSuiteItemProps) => {
    const { colorMode } = useColorMode();
    const [isEditing, setIsEditing] = useState(false);
    const [editName, setEditName] = useState(name);

    const handleDoubleClick = () => {
        setEditName(name);
        setIsEditing(true);
    };

    const handleSave = () => {
        if (editName.trim()) {
            onRename(editName.trim());
        } else {
            setEditName(name);
        }
        setIsEditing(false);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter") {
            handleSave();
        } else if (e.key === "Escape") {
            setEditName(name);
            setIsEditing(false);
        }
    };

    return (
        <HStack
            w="100%"
            p={2}
            borderRadius="md"
            bg={isSelected ? (colorMode === "dark" ? "primary.900" : "primary.500") : "transparent"}
            _hover={{
                bg: isSelected ? (colorMode === "dark" ? "primary.900" : "primary.500") : "whiteAlpha.100",
            }}
            cursor="pointer"
            onClick={onSelect}
            gap={2}
            role="group"
        >
            {/* Result indicator */}
            <Box w="16px" flexShrink={0}>
                {hasResult && (
                    <Box
                        w="10px"
                        h="10px"
                        borderRadius="full"
                        bg={resultPassed ? "green.500" : "red.500"}
                    />
                )}
            </Box>

            {/* Test name */}
            {isEditing ? (
                <Input
                    size="xs"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    onBlur={handleSave}
                    onKeyDown={handleKeyDown}
                    autoFocus
                    onClick={(e) => e.stopPropagation()}
                    flex={1}
                    minW={0}
                />
            ) : (
                <Text
                    flex={1}
                    fontSize="sm"
                    color={isSelected ? "fg.default" : "fg.muted"}
                    truncate
                    onDoubleClick={handleDoubleClick}
                    title={name}
                >
                    {name}
                </Text>
            )}

            {/* Action buttons - show on hover */}
            {canDelete && (
                <HStack
                    gap={1}
                    opacity={0.3}
                    _groupHover={{ opacity: 1 }}
                    transition="opacity 0.2s"
                    onClick={(e) => e.stopPropagation()}
                >
                    <Tooltip content="Delete">
                        <IconButton
                            aria-label="Delete test"
                            size="xs"
                            variant="ghost"
                            color="red.400"
                            onClick={onDelete}
                            _hover={{ bg: "red.900", color: "red.200" }}
                        >
                            <FaTrash size={12} />
                        </IconButton>
                    </Tooltip>
                </HStack>
            )}
        </HStack>
    );
};

export const AgentEvalTestSuite = () => {
    const {
        testSuite,
        selectedTest,
        selectTest,
        addTest,
        removeTest,
        renameTest,
    } = useAgentEval();
    const { colorMode } = useColorMode();

    const canDelete = testSuite.tests.length > 1;

    // Count passed/failed tests
    const passedCount = testSuite.tests.filter(t => t.evalResult?.score === true).length;
    const failedCount = testSuite.tests.filter(t => t.evalResult?.score === false).length;

    return (
        <Box
            w="180px"
            minW="180px"
            h="100%"
            display="flex"
            flexDirection="column"
            bg="bg.subtle"
        >
            {/* Header */}
            <HStack
                p={3}
                bg={colorMode === "dark" ? "gray.800" : "gray.200"}
                justifyContent="space-between"
            >
                <HStack gap={2}>
                    <Text fontSize="sm" fontWeight="semibold" color="fg.default">
                        Tests
                    </Text>
                    <Badge colorPalette="gray" size="sm" variant="solid">
                        {testSuite.tests.length}
                    </Badge>
                </HStack>
                <Tooltip content="Add Test">
                    <IconButton
                        aria-label="Add test"
                        size="xs"
                        variant="ghost"
                        onClick={() => addTest()}
                        _hover={{ bg: colorMode === "dark" ? "primary.900" : "primary.500" }}
                    >
                        <FaPlus size={10} />
                    </IconButton>
                </Tooltip>
            </HStack>

            {/* Summary badges */}
            {(passedCount > 0 || failedCount > 0) && (
                <HStack p={2} gap={2} borderBottom="1px solid" borderColor={colorMode === "dark" ? "gray.700" : "gray.200"}>
                    {passedCount > 0 && (
                        <HStack gap={1} fontSize="xs" color="green.400">
                            <FaCheck size={10} />
                            <Text>{passedCount}</Text>
                        </HStack>
                    )}
                    {failedCount > 0 && (
                        <HStack gap={1} fontSize="xs" color="red.400">
                            <FaTimes size={10} />
                            <Text>{failedCount}</Text>
                        </HStack>
                    )}
                </HStack>
            )}

            {/* Test list */}
            <VStack
                flex={1}
                overflowY="auto"
                p={2}
                gap={1}
                align="stretch"
            >
                {testSuite.tests.map((test) => (
                    <TestSuiteItem
                        key={test.id}
                        name={test.name}
                        isSelected={test.id === selectedTest?.id}
                        hasResult={test.evalResult !== null}
                        resultPassed={test.evalResult?.score}
                        onSelect={() => selectTest(test.id)}
                        onDelete={() => removeTest(test.id)}
                        onRename={(name) => renameTest(test.id, name)}
                        canDelete={canDelete}
                    />
                ))}
            </VStack>
        </Box>
    );
};
