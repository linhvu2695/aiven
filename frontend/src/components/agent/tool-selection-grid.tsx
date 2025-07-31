import {
    Grid,
    GridItem,
    Box,
    IconButton,
    VStack,
    Text,
} from "@chakra-ui/react";
import { FaCheck, FaTimes } from "react-icons/fa";
import { type Tool } from "@/context/agent-ctx";

interface ToolSelectionGridProps {
    availableTools: Tool[];
    isToolAssigned: (toolId: string) => boolean;
    selectedToolIds: Set<string>;
    onToggleToolSelection: (toolId: string) => void;
    onRemoveTool: (toolId: string) => void;
}

export const ToolSelectionGrid = ({
    availableTools,
    isToolAssigned,
    selectedToolIds,
    onToggleToolSelection,
    onRemoveTool,
}: ToolSelectionGridProps) => {
    return (
        <Grid
            templateColumns="repeat(auto-fit, minmax(200px, 1fr))"
            gap={4}
            p={2}
        >
            {availableTools.map((tool) => {
                const isAssigned = isToolAssigned(tool.id);
                const isSelected = selectedToolIds.has(tool.id);

                return (
                    <GridItem key={tool.id}>
                        <Box
                            position="relative"
                            p={4}
                            border={isAssigned ? "2px solid" : "1px solid"}
                            borderColor={isAssigned ? "teal.800" : "gray.700"}
                            borderRadius="md"
                            cursor="pointer"
                            transition="all 0.2s"
                            _hover={{
                                bg: { base: "teal.500", _dark: "teal.700" },
                                borderColor: "transparent",
                            }}
                            onClick={() =>
                                !isAssigned && onToggleToolSelection(tool.id)
                            }
                        >
                            {/* Remove button for assigned tools */}
                            {isAssigned && (
                                <IconButton
                                    position="absolute"
                                    top={2}
                                    right={2}
                                    size="xs"
                                    variant="solid"
                                    _hover={{
                                        bg: "red.500",
                                        color: "white",
                                    }}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onRemoveTool(tool.id);
                                    }}
                                >
                                    <FaTimes />
                                </IconButton>
                            )}

                            {/* Selection indicator */}
                            {(isAssigned || isSelected) && (
                                <Box
                                    position="absolute"
                                    bottom={2}
                                    right={2}
                                    color={
                                        isAssigned ? "green.600" : "teal.600"
                                    }
                                >
                                    <FaCheck size={16} />
                                </Box>
                            )}

                            {/* Content */}
                            <VStack
                                align="start"
                                gap={2}
                            >
                                <Text fontWeight="bold" fontSize="sm">
                                    {tool.name}
                                </Text>
                                <Text
                                    fontSize="xs"
                                    color={{ base: "gray.600", _dark: "gray.200" }}
                                    lineClamp={2}
                                >
                                    {tool.description}{tool.emoji}
                                </Text>
                            </VStack>
                        </Box>
                    </GridItem>
                );
            })}
        </Grid>
    );
};
