import { Container, HStack, Box } from "@chakra-ui/react";
import { ChatContainer } from "./components/chat/chat-container";
import Navbar from "./components/navbar";
import { AgentContainer } from "./components/agent/agent-container";
import { ChatModelProvider } from "./context/chat-model-ctx";

export const BASE_URL = import.meta.env.VITE_API_BASE_URL;

function App() {
    return (
        <Container maxW={"1800px"}>
            <Navbar />
            <ChatModelProvider>
                <HStack>
                    <Box flex={1} height={"88vh"}>
                        <AgentContainer />
                    </Box>
                    <Box flex={2} height={"88vh"}>
                        <ChatContainer />
                    </Box>
                </HStack>
            </ChatModelProvider>
        </Container>
    );
}

export default App;
