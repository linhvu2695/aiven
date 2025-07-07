import { Box, Container, SimpleGrid, Text, VStack } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import type { Agent } from "@/context/agent-ctx";
import { BASE_URL } from "@/App";
import { useAgent } from "@/context/agent-ctx";

const AgentSelectionGridItem = (
    agentInfo: Agent & { onClick?: () => void }
) => {
    return (
        <Box
            borderRadius="lg"
            overflow="hidden"
            position="relative"
            cursor={"pointer"}
            bgImage={`url(${agentInfo.avatar})`}
            bgSize="cover"
            bgPos="center"
            h="300px"
            _hover={{
                transform: "scale(1.05)",
                transition: "transform 0.2s ease-in-out",
            }}
            onClick={agentInfo.onClick}
        >
            {/* Grid item */}
            <VStack
                position="absolute"
                bottom="0"
                left="0"
                right="0"
                bg="linear-gradient(to top, rgba(0,0,0,0.8), transparent)"
                p={4}
                align="start"
                spaceY={1}
            >
                <Text>{agentInfo.name}</Text>
            </VStack>
        </Box>
    );
};

export const AgentSelectionGrid = ({ onSelect }: { onSelect?: () => void }) => {
    const { setAgent } = useAgent();
    const [agents, setAgents] = useState<Agent[]>([]);

    const fetchAgents = async () => {
        try {
            const response = await fetch(BASE_URL + "/api/agent/search", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) throw new Error("Failed to fetch agent info");
            const data = await response.json();
            // Ensure agents have all Agent fields
            setAgents(
                data.agents.map((agent: any) => ({
                    id: agent.id,
                    name: agent.name,
                    description: agent.description,
                    avatar: agent.avatar,
                    model: agent.model,
                    persona: agent.persona,
                    tone: agent.tone,
                }))
            );
        } catch (error) {
            console.error("Error fetching agent info:", error);
        }
    };

    useEffect(() => {
        fetchAgents();
    }, []);

    return (
        <Container>
            <SimpleGrid columns={{ sm: 2, md: 3, lg: 5 }} gap={6}>
                {agents.map((agent) => (
                    <AgentSelectionGridItem
                        key={agent.id}
                        {...agent}
                        onClick={() => {
                            setAgent(agent);
                            if (onSelect) onSelect();
                        }}
                    />
                ))}
            </SimpleGrid>
        </Container>
    );
};
