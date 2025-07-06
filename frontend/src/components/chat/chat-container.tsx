import { Button, Container, Input, Stack, Spinner } from "@chakra-ui/react";
import { useRef, useState } from "react";
import { FaPaperclip, FaPaperPlane } from "react-icons/fa";
import { ChatMessage } from "./chat-message";
import { BASE_URL } from "@/App";
import { useAgent } from "@/context/agent-ctx";

export const ChatContainer = () => {
    const { agent } = useAgent();
    const messagesEndRef = useRef<HTMLDivElement | null>(null);
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState([
        { role: "assistant", content: "Hello. What can I do for you?" },
    ]);
    const [isLoading, setIsLoading] = useState(false);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "end",
        });
    };

    const handleSendMessage = async () => {
        if (!input.trim()) return;

        setMessages((prev) => [...prev, { role: "user", content: input }]);
        setInput("");
        setIsLoading(true);

        // Fetch
        try {
            const response = await fetch(BASE_URL + "/api/chat/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    messages: [
                        ...messages,
                        {
                            role: "user",
                            content: input,
                        },
                    ],
                    agent: agent?.id,
                }),
            });
            const data = await response.json();

            if (!response.ok) {
                console.log(data);
                throw new Error(data.error);
            }

            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: data.response },
            ]);
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);
            scrollToBottom();
        }
    };

    return (
        <Container
            height="100%"
            display="flex"
            flexDirection="column"
            justifyContent="space-between"
        >
            <Stack spaceY={3} align="stretch" overflowY="auto" p={4}>
                {messages.map((msg, idx) => (
                    <ChatMessage
                        key={idx}
                        content={msg.content}
                        role={msg.role}
                    />
                ))}
                {isLoading && (
                    <Stack
                        direction="row"
                        justifyContent="center"
                        alignItems="center"
                        py={2}
                    >
                        <Spinner size="lg" color="teal.400" />
                    </Stack>
                )}
                <div ref={messagesEndRef} />
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
    );
};
