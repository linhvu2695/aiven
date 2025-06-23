import { Button, Container, Input, Stack } from "@chakra-ui/react";
import { useState } from "react";
import { FaPaperclip, FaPaperPlane } from "react-icons/fa";
import { ChatMessage } from "./chat-message";

export const ChatContainer = () => {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState([
        { role: "assistant", content: "Hello. What can I do for you?" },
        { role: "user", content: "Hi" },
    ]);

    const handleSendMessage = async () => {
        if (!input.trim()) return;

        setMessages((prev) => [...prev, { role: "user", content: input }]);
        setInput("");

        // Fetch
    };

    return (
        <Stack>
            <Container
                maxW="100vh"
                maxH="100vh"
                height="100vh"
                display="flex"
                flexDirection="column"
                justifyContent="space-between"
            >
                <Stack spaceX={3} align="stretch" overflowY="auto" p={4}>
                    {messages.map((msg, idx) => (
                        <ChatMessage
                            key={idx}
                            content={msg.content}
                            role={msg.role}
                        />
                    ))}
                </Stack>

                <Stack flexDirection={"row"} mt={4} alignItems={"center"}>
                    <Button bg={"none"} color={"white"}>
                        <FaPaperclip size={"3rem"} />
                    </Button>

                    <Input
                        size={"2xl"}
                        placeholder="What do you want to say..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault();
                                handleSendMessage();
                            }
                        }}
                        border={"none"}
                        focusRing={"none"}
                    />
                    <Button
                        alignItems="center"
                        justifyContent="center"
                        padding="8px"
                        transition="all 0.3s ease"
                        _hover={{
                            transform: "scale(1.1)",
                            bgColor: "teal.500",
                            boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
                        }}
                        onClick={() => handleSendMessage()}
                    >
                        <FaPaperPlane size="3rem" />
                    </Button>
                </Stack>
            </Container>
        </Stack>
    );
};
