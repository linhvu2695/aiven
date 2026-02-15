import { Container } from "@chakra-ui/react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Navbar from "./components/navbar";
import { AgentChatPage } from "./pages/agent-chat-page";
import { AgentManagementPage } from "./pages/agent-mngmnt-page";
import KnowledgePage from "./pages/knowledge-page";
import PlantPage from "./pages/plant-page";
import { AgentProvider } from "./context/agent-ctx";
import { ArticleProvider } from "./context/article-ctx";
import { ChatProvider } from "./context/chat-ctx";
import { ImageProvider } from "./context/image-ctx";
import { ImageViewProvider } from "./context/image-view-ctx";
import { VideoProvider } from "./context/video-ctx";
import { Toaster } from "./components/ui/toaster";
import ImagePage from "./pages/image-page";
import VideoPage from "./pages/video-page";
import WorkPage from "./pages/work-page";

export const BASE_URL = import.meta.env.VITE_API_BASE_URL;

function App() {
    return (
        <Container maxW={"1800px"}>
            <Toaster/>
            <BrowserRouter>
                <ChatProvider>
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
                        <Route
                            path="/image"
                            element={
                                <ImageProvider>
                                    <ImageViewProvider>
                                        <ImagePage />
                                    </ImageViewProvider>
                                </ImageProvider>
                            }
                        />
                        <Route
                            path="/video"
                            element={
                                <VideoProvider>
                                    <VideoPage />
                                </VideoProvider>
                            }
                        />
                        <Route
                            path="/knowledge"
                            element={
                                <ArticleProvider>
                                    <KnowledgePage />
                                </ArticleProvider>
                            }
                        />
                        <Route
                            path="/plant"
                            element={<PlantPage />}
                        />
                        <Route
                            path="/work"
                            element={<WorkPage />}
                        />
                    </Routes>
                </ChatProvider>
            </BrowserRouter>
        </Container>
    );
}

export default App;
