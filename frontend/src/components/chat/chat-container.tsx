import {
    Button,
    Container,
    Input,
    Stack,
    Spinner,
    useFileUploadContext,
    Float,
} from "@chakra-ui/react";
import { FileUpload } from "@chakra-ui/react";
import { useRef, useState } from "react";
import { FaPaperclip, FaPaperPlane } from "react-icons/fa";
import { LuRefreshCw } from "react-icons/lu";
import { ChatMessage } from "./chat-message";
import { BASE_URL } from "@/App";
import { useAgent } from "@/context/agent-ctx";
import { useChat } from "@/context/chat-ctx";
import type { ChatMessageInfo } from "./chat-message-info";
import { LuX, LuFile, LuFileAudio, LuFileText } from "react-icons/lu";

export const ChatContainer = () => {
    return (
        <FileUpload.Root
            maxFiles={1}
            accept={["image/*", "audio/*", "application/pdf"]}
            height="100%"
        >
            <ChatContainerContent />
        </FileUpload.Root>
    );
};

const ChatContainerContent = () => {
    const { agent } = useAgent();
    const { messages, setMessages, sessionId, setSessionId, resetSession } =
        useChat();
    const messagesEndRef = useRef<HTMLDivElement | null>(null);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const fileUpload = useFileUploadContext();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "end",
        });
    };

    const handleStreamingResponse = async (
        response: Response,
        assistantMessageIndex: number
    ) => {
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (reader) {
            let buffer = "";
            let currentMessageId: string | null = null;
            let currentMessageIndex = assistantMessageIndex;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                // Decode chunk and add to buffer
                buffer += decoder.decode(value, { stream: true });

                // Process complete lines
                const lines = buffer.split("\n");
                buffer = lines.pop() || ""; // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        const dataStr = line.slice(6); // Remove 'data: ' prefix
                        try {
                            const data = JSON.parse(dataStr);

                            // Capture session_id if present (first chunk or completion)
                            if (data.session_id && !sessionId) {
                                setSessionId(data.session_id);
                            }

                            if (data.type === "token" && data.token) {
                                // Check if we got a new message_id
                                if (data.message_id && data.message_id !== currentMessageId) {
                                    // New message detected
                                    if (currentMessageId !== null) {
                                        // Not the first message, create a new one
                                        setMessages((prev) => [
                                            ...prev,
                                            {
                                                role: "assistant",
                                                content: data.token,
                                                message_id: data.message_id,
                                            },
                                        ]);
                                        currentMessageIndex = currentMessageIndex + 1;
                                    } else {
                                        // First message, update the existing empty one
                                        setMessages((prev) => {
                                            const newMessages = [...prev];
                                            newMessages[currentMessageIndex] = {
                                                ...newMessages[currentMessageIndex],
                                                content: data.token,
                                                message_id: data.message_id,
                                            };
                                            return newMessages;
                                        });
                                    }
                                    currentMessageId = data.message_id;
                                } else {
                                    // Same message, append token
                                    setMessages((prev) => {
                                        const newMessages = [...prev];
                                        newMessages[currentMessageIndex] = {
                                            ...newMessages[currentMessageIndex],
                                            content:
                                                newMessages[currentMessageIndex]
                                                    .content + data.token,
                                        };
                                        return newMessages;
                                    });
                                }
                            } else if (data.type === "done") {
                                // Final session_id confirmation (safety net)
                                if (data.session_id && !sessionId) {
                                    setSessionId(data.session_id);
                                }

                                // Streaming completed
                                return;
                            } else if (data.type === "error") {
                                throw new Error(
                                    data.message || "Streaming error"
                                );
                            }
                        } catch (e) {
                            console.warn("Failed to parse SSE data:", dataStr);
                        }
                    }
                }
            }
        }
    };

    const sendStreamingRequestWithFiles = async (
        userInput: string,
        assistantMessageIndex: number
    ) => {
        const formData = new FormData();

        // Add current message data
        formData.append(
            "message",
            JSON.stringify({
                role: "user",
                content: userInput,
            })
        );

        // Add agent ID
        if (agent?.id) {
            formData.append("agent", agent.id);
        }

        // Add session ID
        if (sessionId) {
            formData.append("session_id", sessionId);
        }

        // Add files
        fileUpload.acceptedFiles.forEach((file) => {
            formData.append(`files`, file);
        });

        const response = await fetch(BASE_URL + "/api/chat/stream", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        await handleStreamingResponse(response, assistantMessageIndex);
    };

    const sendStreamingRequestJSON = async (
        userInput: string,
        assistantMessageIndex: number
    ) => {
        const requestBody = {
            message: {
                role: "user",
                content: userInput,
            },
            agent: agent?.id,
            session_id: sessionId ?? "",
        };

        const response = await fetch(BASE_URL + "/api/chat/stream", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        await handleStreamingResponse(response, assistantMessageIndex);
    };

    const handleSendMessage = async () => {
        if (!input.trim()) return;

        // Create user message with files if any
        const userMessage: ChatMessageInfo = {
            role: "user",
            content: input,
            file:
                fileUpload.acceptedFiles.length > 0
                    ? fileUpload.acceptedFiles[0]
                    : undefined,
            filePreview:
                fileUpload.acceptedFiles.length > 0 &&
                fileUpload.acceptedFiles[0].type.startsWith("image/")
                    ? URL.createObjectURL(fileUpload.acceptedFiles[0])
                    : null,
        };

        const currentInput = input;

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        // Add empty assistant message that we'll update with streaming content
        const assistantMessageIndex = messages.length + 1;
        setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

        try {
            if (fileUpload.acceptedFiles.length > 0) {
                await sendStreamingRequestWithFiles(
                    currentInput,
                    assistantMessageIndex
                );
            } else {
                await sendStreamingRequestJSON(
                    currentInput,
                    assistantMessageIndex
                );
            }

            // Clear uploaded files after successful send
            fileUpload.clearFiles();
        } catch (error) {
            console.error("Streaming error:", error);

            // Update the assistant message with error
            setMessages((prev) => {
                const newMessages = [...prev];
                newMessages[assistantMessageIndex] = {
                    ...newMessages[assistantMessageIndex],
                    content:
                        "❌ An error occurred while processing your request. Please try again.",
                };
                return newMessages;
            });
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
            data-testid="chat-container"
        >
            {/* Messages */}
            <Stack spaceY={3} align="stretch" overflowY="auto" p={4}>
                {messages.map((msg, idx) => (
                    <ChatMessage
                        key={idx}
                        content={msg.content}
                        role={msg.role}
                        file={msg.file}
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

            {/* User input */}
            <Stack gap={2} mt={4}>
                {/* Uploaded files */}
                <FileUploadList />

                <Stack flexDirection={"row"} alignItems={"center"}>
                    {/* New conversation button */}
                    <Button
                        bg={"none"}
                        color={"white"}
                        w={"40px"}
                        onClick={resetSession}
                        title="Start new conversation"
                        _hover={{
                            transform: "scale(1.1)",
                            bgColor: "teal.500",
                        }}
                    >
                        <LuRefreshCw size={"1.5rem"} />
                    </Button>

                    {/* Media upload button */}
                    <FileUpload.HiddenInput />
                    <FileUpload.Trigger asChild>
                        <Button bg={"none"} color={"white"} w={"40px"}>
                            <FaPaperclip size={"3rem"} />
                        </Button>
                    </FileUpload.Trigger>

                    {/* Message input */}
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

                    {/* Send button */}
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
            </Stack>
        </Container>
    );
};

const FileUploadList = () => {
    const fileUpload = useFileUploadContext();
    const files = fileUpload.acceptedFiles;
    if (files.length === 0) return null;

    const renderFilePreview = (file: File) => {
        if (file.type.startsWith("image/")) {
            return (
                <FileUpload.ItemPreviewImage
                    width="100%"
                    height="100%"
                    rounded="md"
                    objectFit="cover"
                />
            );
        } else if (file.type.startsWith("audio/")) {
            return (
                <Stack
                    alignItems="center"
                    justifyContent="center"
                    width="100%"
                    height="100%"
                    bg="gray.700"
                    rounded="md"
                    p={2}
                >
                    <LuFileAudio size="24px" color="white" />
                    <FileUpload.ItemName
                        fontSize="2xs"
                        color="white"
                        textAlign="center"
                        mt={1}
                        lineClamp={2}
                        overflow="hidden"
                        wordBreak="break-word"
                        width="100%"
                    />
                </Stack>
            );
        } else if (file.type === "application/pdf") {
            return (
                <Stack
                    alignItems="center"
                    justifyContent="center"
                    width="100%"
                    height="100%"
                    bg="red.700"
                    rounded="md"
                    p={2}
                >
                    <LuFileText size="24px" color="white" />
                    <FileUpload.ItemName
                        fontSize="2xs"
                        color="white"
                        textAlign="center"
                        mt={1}
                        lineClamp={2}
                        overflow="hidden"
                        wordBreak="break-word"
                        width="100%"
                    />
                </Stack>
            );
        } else {
            return (
                <Stack
                    alignItems="center"
                    justifyContent="center"
                    width="100%"
                    height="100%"
                    bg="gray.600"
                    rounded="md"
                    p={2}
                >
                    <LuFile size="24px" color="white" />
                    <FileUpload.ItemName
                        fontSize="2xs"
                        color="white"
                        textAlign="center"
                        mt={1}
                        lineClamp={2}
                        overflow="hidden"
                        wordBreak="break-word"
                        width="100%"
                    />
                </Stack>
            );
        }
    };

    return (
        <FileUpload.ItemGroup>
            {files.map((file) => (
                <FileUpload.Item
                    w="auto"
                    maxW="128px"
                    maxH="128px"
                    p={0}
                    file={file}
                    key={file.name}
                >
                    {renderFilePreview(file)}
                    <Float placement="top-end">
                        <FileUpload.ItemDeleteTrigger>
                            <LuX size={"1rem"} />
                        </FileUpload.ItemDeleteTrigger>
                    </Float>
                </FileUpload.Item>
            ))}
        </FileUpload.ItemGroup>
    );
};
