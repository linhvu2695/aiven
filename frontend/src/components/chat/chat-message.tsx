import { Avatar, Box, HStack, Text } from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { useAgent } from "@/context/agent-ctx";
import type { ChatMessageInfo } from "./chat-message-info";

const roleBgColor: Record<string, string> = {
    user: "teal.500",
    assistant: "gray.600",
};

export const ChatMessage = (msg: ChatMessageInfo) => {
    const { agent } = useAgent();

    return (
        <HStack
            flexDirection={msg.role === "user" ? "row-reverse" : "row"}
            gap={4}
            alignItems="flex-start"
        >
            <Avatar.Root size={"sm"}>
                <Avatar.Image
                    src={msg.role === "user" ? "/astronaut2.webp" : agent?.avatar}
                    borderWidth="1px"
                    borderColor="white"
                    _hover={{
                        boxShadow: "0px 0px 8px teal",
                        borderColor: "teal.500",
                    }}
                    cursor="pointer"
                ></Avatar.Image>
            </Avatar.Root>

            <Box
                bg={roleBgColor[msg.role] ?? "gray.600"}
                color="white"
                p={3}
                borderRadius={14}
                maxWidth="70%"
            >
                {/* File preview if present */}
                {msg.file && (
                    <Box mb={2}>
                        {msg.file.type.startsWith("image/") && msg.filePreview && (
                            <img src={msg.filePreview} alt={msg.file.name} style={{ maxWidth: "200px", borderRadius: 8 }} />
                        )}
                        {msg.file.type.startsWith("audio/") && msg.filePreview && (
                            <audio controls src={msg.filePreview} style={{ maxWidth: "200px" }} />
                        )}
                        {msg.file.type === "application/pdf" && (
                            <a href={msg.filePreview || "#"} target="_blank" rel="noopener noreferrer">
                                📄 {msg.file.name}
                            </a>
                        )}
                        {!msg.file.type.startsWith("image/") && !msg.file.type.startsWith("audio/") && msg.file.type !== "application/pdf" && (
                            <span>📎 {msg.file.name}</span>
                        )}
                    </Box>
                )}

                {/* Message content */}
                <ReactMarkdown
                    remarkPlugins={[remarkGfm, remarkBreaks]}
                    components={{
                        p: ({ children }) => <Text mb={2}>{children}</Text>,
                        h1: ({ children }) => <Text as="h1" fontSize="2xl" fontWeight="bold" mb={2}>{children}</Text>,
                        h2: ({ children }) => <Text as="h2" fontSize="xl" fontWeight="semibold" mb={2}>{children}</Text>,
                        code: ({ children }) => (
                            <Box
                                as="code"
                                bg="gray.700"
                                color="teal.200"
                                px={2}
                                py={1}
                                borderRadius="md"
                                fontSize="sm"
                                fontFamily="mono"
                                display="inline-block"
                                mb={2}
                            >
                                {children}
                            </Box>
                        ),
                    }}
                >
                    {msg.content}
                </ReactMarkdown>
            </Box>
        </HStack>
    );
};
