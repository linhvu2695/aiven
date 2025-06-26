import { Container, HStack, Box } from "@chakra-ui/react";
import { ChatContainer } from "./components/chat/chat-container";
import Navbar from "./components/navbar";
import { AgentContainer } from "./components/agent/agent-container";

export const BASE_URL = import.meta.env.VITE_API_BASE_URL;

function App() {
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
