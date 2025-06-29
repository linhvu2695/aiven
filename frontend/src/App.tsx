import { Container, HStack, Box } from "@chakra-ui/react";
import { ChatContainer } from "./components/chat/chat-container";
import Navbar from "./components/navbar";
import { AgentContainer } from "./components/agent/agent-container";
import { useAgent } from "./context/agent-ctx";
import { useEffect } from "react";

export const BASE_URL = import.meta.env.VITE_API_BASE_URL;

function App() {
    const { setAgent, setAgentDraft } = useAgent();

    useEffect(() => {
        const fetchAgent = async () => {
            try {
                const response = await fetch(
                    BASE_URL + "/api/agent/685fff58d3367dc42c178987",
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
    }, [setAgent]);

    return (
        <Container maxW={"1800px"}>
            <Navbar />
            <HStack>
                <Box flex={1} height={"88vh"}>
                    <AgentContainer />
                </Box>
                <Box flex={2} height={"88vh"}>
                    <ChatContainer />
                </Box>
            </HStack>
        </Container>
    );
}

export default App;
