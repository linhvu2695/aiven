import { Avatar, Box, HStack, Text, VStack } from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { useAgent } from "@/context/agent-ctx";
import type { ChatMessageInfo } from "./chat-message-info";
import { FilePreview } from "./file-preview";

interface ParsedMessageContent {
    text: string;
    file: File | null;
    filePreview: string | null;
    imageData: string | null;
    mimeType: string | null;
    hasFileContent: boolean;
    isImageContent: boolean;
}

const parseMessageContent = (msg: ChatMessageInfo): ParsedMessageContent => {
    let text = "";
    let file: File | null = null;
    let filePreview: string | null = null;
    let imageData: string | null = null;
    let mimeType: string | null = null;

    if (typeof msg.content === "string") {
        // Frontend message
        text = msg.content;
        file = msg.file || null;
        filePreview = msg.filePreview || null;
    } else {
        // Backend message
        msg.content.forEach((item) => {
            if (item.type === "image") {
                imageData = item.data || null;
                mimeType = item.mime_type || null;
            } else if (item.type === "text") {
                text = item.text || "";
            }
        });
    }

    // Check if we have any file content (either frontend File or backend image data)
    const hasFileContent = Boolean(file || imageData);
    
    // Check if content is an image
    const isFileImage = file && file.type?.startsWith("image/");
    const isMimeTypeImage = mimeType && String(mimeType).startsWith("image/");
    const isImageContent = Boolean(isFileImage || isMimeTypeImage);

    return {
        text,
        file,
        filePreview,
        imageData,
        mimeType,
        hasFileContent,
        isImageContent,
    };
};

const roleBgColor: Record<string, string> = {
    user: "teal.500",
    assistant: "gray.600",
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
    
    const {
        text,
        file,
        filePreview,
        imageData,
        mimeType,
        hasFileContent,
        isImageContent,
    } = parseMessageContent(msg);

    // Render separate bubbles for file and text
    if (hasFileContent && text) {
        return (
            <VStack
                gap={2}
                alignItems={msg.role === "user" ? "flex-end" : "flex-start"}
            >
                {/* File Preview */}
                <MessageBubble
                    role={msg.role}
                    agent={agent}
                    isImage={isImageContent}
                >
                    <FilePreview
                        file={file}
                        filePreview={filePreview}
                        imageData={imageData}
                        mimeType={mimeType}
                    />
                </MessageBubble>

                {/* Text Content */}
                <MessageBubble role={msg.role} agent={agent}>
                    <MessageContent content={text} />
                </MessageBubble>
            </VStack>
        );
    }

    // Single bubble for file or text only
    return (
        <MessageBubble 
            role={msg.role} 
            agent={agent}
            isImage={isImageContent && !text}
        >
            {hasFileContent && (
                <Box mb={text ? 2 : 0}>
                    <FilePreview
                        file={file}
                        filePreview={filePreview}
                        imageData={imageData}
                        mimeType={mimeType}
                    />
                </Box>
            )}
            {text && <MessageContent content={text} />}
        </MessageBubble>
    );
};
