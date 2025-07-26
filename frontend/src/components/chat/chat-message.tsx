import { Avatar, Box, HStack, Text, VStack } from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { useAgent } from "@/context/agent-ctx";
import type { ChatMessageInfo } from "./chat-message-info";

const roleBgColor: Record<string, string> = {
    user: "teal.500",
    assistant: "gray.600",
};

const FilePreview = ({
    file,
    filePreview,
}: {
    file: File;
    filePreview?: string | null;
}) => {
    const previewUrl =
        filePreview ||
        (file.type.startsWith("image/") ? URL.createObjectURL(file) : null);

    if (file.type.startsWith("image/")) {
        return previewUrl ? (
            <img
                src={previewUrl}
                alt={file.name}
                style={{ maxWidth: "200px", borderRadius: 8 }}
                onError={(e) => {
                    console.error("Image failed to load:", previewUrl);
                    e.currentTarget.style.display = "none";
                }}
            />
        ) : (
            <span>🖼️ {file.name}</span>
        );
    }

    if (file.type.startsWith("audio/")) {
        return previewUrl ? (
            <audio controls src={previewUrl} style={{ maxWidth: "200px" }} />
        ) : (
            <span>🎵 {file.name}</span>
        );
    }

    if (file.type === "application/pdf") {
        return (
            <a
                href={previewUrl || "#"}
                target="_blank"
                rel="noopener noreferrer"
            >
                📄 {file.name}
            </a>
        );
    }

    return <span>📎 {file.name}</span>;
};

const MessageContent = ({ content }: { content: string }) => (
    <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkBreaks]}
        components={{
            p: ({ children }) => <Text mb={2}>{children}</Text>,
            h1: ({ children }) => (
                <Text as="h1" fontSize="2xl" fontWeight="bold" mb={2}>
                    {children}
                </Text>
            ),
            h2: ({ children }) => (
                <Text as="h2" fontSize="xl" fontWeight="semibold" mb={2}>
                    {children}
                </Text>
            ),
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
        {content}
    </ReactMarkdown>
);

const MessageBubble = ({
    role,
    agent,
    children,
    isImage = false,
}: {
    role: string;
    agent: any;
    children: React.ReactNode;
    isImage?: boolean;
}) => (
    <HStack
        flexDirection={role === "user" ? "row-reverse" : "row"}
        gap={4}
        alignItems="flex-start"
    >
        <Avatar.Root size={"sm"}>
            <Avatar.Image
                src={role === "user" ? "/astronaut2.webp" : agent?.avatar}
                borderWidth="1px"
                borderColor="white"
                _hover={{
                    boxShadow: "0px 0px 8px teal",
                    borderColor: "teal.500",
                }}
                cursor="pointer"
            />
        </Avatar.Root>

        <Box
            bg={roleBgColor[role] ?? "gray.600"}
            color="white"
            p={isImage ? 0 : 3}
            borderRadius={14}
        >
            {children}
        </Box>
    </HStack>
);

export const ChatMessage = (msg: ChatMessageInfo) => {
    const { agent } = useAgent();
    const hasFile = !!msg.file;
    const hasText = !!msg.content.trim();

    // Render separate bubbles for file and text
    if (hasFile && hasText) {
        return (
            <VStack
                gap={2}
                alignItems={msg.role === "user" ? "flex-end" : "flex-start"}
            >
                <MessageBubble
                    role={msg.role}
                    agent={agent}
                    isImage={msg.file?.type.startsWith("image/")}
                >
                    <FilePreview
                        file={msg.file!}
                        filePreview={msg.filePreview}
                    />
                </MessageBubble>
                <MessageBubble role={msg.role} agent={agent}>
                    <MessageContent content={msg.content} />
                </MessageBubble>
            </VStack>
        );
    }

    // Single bubble for file or text only
    return (
        <MessageBubble role={msg.role} agent={agent}>
            {hasFile && (
                <Box mb={hasText ? 2 : 0}>
                    <FilePreview
                        file={msg.file!}
                        filePreview={msg.filePreview}
                    />
                </Box>
            )}
            {hasText && <MessageContent content={msg.content} />}
        </MessageBubble>
    );
};
