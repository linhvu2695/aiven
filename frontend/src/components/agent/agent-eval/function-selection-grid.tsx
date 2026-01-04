import {
    Box,
    Grid,
    GridItem,
    Text,
    VStack,
} from "@chakra-ui/react";
import { useState, useEffect, useMemo } from "react";
import { useAgentEval, type ExpectedFunctionCall, type MCPFunction } from "@/context/agent-eval-ctx";
import { BASE_URL } from "@/App";
import { useAgent } from "@/context/agent-ctx";
import type { ToolInfo } from "@/types/tool";

interface FunctionSelectionGridProps {
    onClose: () => void;
}

export const FunctionSelectionGrid = ({
    onClose,
}: FunctionSelectionGridProps) => {
    const { setExpectedFunctionCalls, expectedFunctionCalls } = useAgentEval();
    const { agent } = useAgent();
    const [availableFunctions, setAvailableFunctions] = useState<MCPFunction[]>([]);
    const [tools, setTools] = useState<ToolInfo[]>([]);

    // Fetch available tools
    useEffect(() => {
        const fetchTools = async (): Promise<ToolInfo[]> => {
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

        fetchTools().then(setTools);
    }, []);

    // Fetch available MCP functions
    useEffect(() => {
        const fetchAvailableFunctions = async (): Promise<MCPFunction[]> => {
            try {
                const response = await fetch(BASE_URL + "/api/tool/mcp", {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                if (!response.ok)
                    throw new Error("Failed to fetch available MCP functions");

                const data = await response.json();
                return data.tools;
            } catch (error) {
                console.error("Error fetching available MCP functions:", error);
                return [];
            }
        };

        fetchAvailableFunctions().then(setAvailableFunctions);
    }, []);

    // Calculate enabled MCP functions from agent's tools
    const enabledMCPFunctions = useMemo(() => {
        if (!agent?.tools || tools.length === 0) {
            return new Set<string>();
        }

        const enabledFunctions = new Set<string>();
        const toolMap = new Map(tools.map(tool => [tool.id, tool]));

        for (const toolId of agent.tools) {
            const tool = toolMap.get(toolId);
            if (tool) {
                tool.mcp_functions.forEach(func => enabledFunctions.add(func));
            }
        }

        return enabledFunctions;
    }, [agent?.tools, tools]);

    const handleFunctionSelect = (functionName: string) => {
        const func = availableFunctions.find((f) => f.name === functionName);
        if (func && enabledMCPFunctions.has(functionName)) {
            const newFunctionCall: ExpectedFunctionCall = {
                id: `function-call-${Date.now()}`,
                function: func,
                expectedInput: {},
                expectedOutput: {},
            };
            setExpectedFunctionCalls([...expectedFunctionCalls, newFunctionCall]);
            onClose();
        }
    };

    const isFunctionEnabled = (functionName: string) => {
        return enabledMCPFunctions.has(functionName);
    };

    return (
        <Grid
            templateColumns="repeat(auto-fit, minmax(200px, 1fr))"
            gap={4}
            p={2}
        >
            {availableFunctions.map((func) => {
                const isEnabled = isFunctionEnabled(func.name);
                return (
                    <GridItem key={func.name}>
                        <Box
                            p={4}
                            border="1px solid"
                            borderColor={isEnabled ? "gray.700" : "gray.400"}
                            borderRadius="md"
                            cursor={isEnabled ? "pointer" : "not-allowed"}
                            opacity={isEnabled ? 1 : 0.5}
                            transition="all 0.2s"
                            _hover={isEnabled ? {
                                bg: { base: "teal.500", _dark: "teal.700" },
                                borderColor: "transparent",
                            } : {}}
                            onClick={() => handleFunctionSelect(func.name)}
                        >
                            {/* Content */}
                            <VStack align="start" gap={2}>
                                <Text fontWeight="bold" fontSize="sm">
                                    {func.name}
                                </Text>
                                {func.description && (
                                    <Text
                                        fontSize="xs"
                                        color={{
                                            base: "gray.600",
                                            _dark: "gray.200",
                                        }}
                                        lineClamp={2}
                                    >
                                        {func.description} 
                                    </Text>
                                )}
                            </VStack>
                        </Box>
                    </GridItem>
                );
            })}
        </Grid>
    );
};

