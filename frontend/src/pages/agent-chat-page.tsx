import { BASE_URL } from "@/App";
import { AgentContainer } from "@/components/agent/agent-container";
import { ChatContainer } from "@/components/chat/chat-container";
import { useAgent } from "@/context/agent-ctx";
import { Box, HStack } from "@chakra-ui/react";
import { useEffect } from "react";

export const AgentChatPage = () => {
    const { agent, setAgent, setAgentDraft } = useAgent();

    useEffect(() => {
        const fetchAgent = async () => {
            try {
                const response = await fetch(
                    BASE_URL + `/api/agent/id=${agent?.id ?? "685fff58d3367dc42c178987"}`,
                    {
                        method: "GET",
                        headers: {
                            "Content-Type": "application/json",
                        },
                    }
                );

                if (!response.ok) throw new Error("Failed to fetch agent info");
                const data = await response.json();
                setAgent(data);
                setAgentDraft(data);
            } catch (error) {
                console.error("Error fetching agent info:", error);
            }
        };
        fetchAgent();
    }, [agent?.id]);

    return (
        <HStack as="main">
            <Box as="aside" flex={1} height={"88vh"}>
                <AgentContainer />
            </Box>
            <Box as="section" flex={2} height={"88vh"}>
                <ChatContainer />
            </Box>
        </HStack>
    );
};
