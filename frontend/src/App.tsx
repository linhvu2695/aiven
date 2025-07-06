import { Container } from "@chakra-ui/react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Navbar from "./components/navbar";
import { AgentChatPage } from "./pages/agent-chat-page";
import { AgentManagementPage } from "./pages/agent-mngmnt-page";
import { AgentProvider } from "./context/agent-ctx";

export const BASE_URL = import.meta.env.VITE_API_BASE_URL;

function App() {
    return (
        <Container maxW={"1800px"}>
            <BrowserRouter>
                <Navbar />
                <Routes>
                    <Route
                        path="/chat"
                        element={
                            <AgentProvider>
                                <AgentChatPage />
                            </AgentProvider>
                        }
                    />
                    <Route
                        path="/agent"
                        element={
                            <AgentProvider>
                                <AgentManagementPage />
                            </AgentProvider>
                        }
                    />
                </Routes>
            </BrowserRouter>
        </Container>
    );
}

export default App;
