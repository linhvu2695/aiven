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
    const { messages, setMessages } = useChat();
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

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        // Fetch
        try {
            let response;

            if (fileUpload.acceptedFiles.length > 0) {
                // Use FormData when files are uploaded
                const formData = new FormData();

                // Add messages data
                formData.append(
                    "messages",
                    JSON.stringify([
                        ...messages,
                        {
                            role: "user",
                            content: input,
                        },
                    ])
                );

                // Add agent ID
                if (agent?.id) {
                    formData.append("agent", agent.id);
                }

                // Add files
                fileUpload.acceptedFiles.forEach((file) => {
                    formData.append(`files`, file);
                });

                response = await fetch(BASE_URL + "/api/chat/", {
                    method: "POST",
                    body: formData,
                });
            } else {
                // Use JSON when no files
                response = await fetch(BASE_URL + "/api/chat/", {
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
            }

            const data = await response.json();

            if (!response.ok) {
                console.log(data);
                throw new Error(data.error);
            }

            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: data.response },
            ]);

            // Clear uploaded files and revoke URLs after successful send
            fileUpload.clearFiles();
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
