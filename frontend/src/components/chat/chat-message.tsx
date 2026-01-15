import {
    Avatar,
    Box,
    HStack,
    IconButton,
    Text,
    VStack,
} from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { FaTimes } from "react-icons/fa";
import { useAgent } from "@/context/agent-ctx";
import type { ChatMessageInfo } from "./chat-message-info";
import { FilePreview } from "./file-preview";
import { DEFAULT_USER_AVATAR } from "@/utils/constants";

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
    user: "primary.500",
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
                    color="primary.200"
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

const RemoveMessageButton = ({
    role,
    onRemove,
}: {
    role: string;
    onRemove: () => void;
}) => (
    <IconButton
        aria-label="Remove message"
        size="xs"
        variant="ghost"
        bg="transparent"
        position="absolute"
        color="red.500"
        top={-3}
        right={role === "user" ? undefined : -4}
        left={role === "user" ? -4 : undefined}
        zIndex={10}
        onClick={onRemove}
        opacity={0.7}
        _hover={{ opacity: 1 }}
    >
        <FaTimes />
    </IconButton>
);

const MessageBubble = ({
    role,
    agent,
    children,
    isImage = false,
    onRemove,
}: {
    role: string;
    agent: any;
    children: React.ReactNode;
    isImage?: boolean;
    onRemove?: () => void;
}) => (
    <HStack
        flexDirection={role === "user" ? "row-reverse" : "row"}
        gap={4}
        alignItems="flex-start"
    >
        <Avatar.Root size={"sm"}>
            <Avatar.Image
                src={
                    role === "user"
                        ? DEFAULT_USER_AVATAR
                        : agent?.avatar_image_url
                }
                borderWidth="1px"
                borderColor="white"
                _hover={{
                    boxShadow: "0px 0px 8px var(--chakra-colors-primary-500)",
                    borderColor: "primary.500",
                }}
                cursor="pointer"
            />
        </Avatar.Root>

        <Box
            position="relative"
            bg={roleBgColor[role] ?? "gray.600"}
            color="white"
            p={isImage ? 0 : 3}
            borderRadius={14}
        >
            {onRemove && <RemoveMessageButton role={role} onRemove={onRemove} />}
            {children}
        </Box>
    </HStack>
);

export const ChatMessage = (
    msg: ChatMessageInfo & { onRemove?: () => void }
) => {
    const { agent } = useAgent();
    const { onRemove } = msg;

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
                    onRemove={onRemove}
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
            onRemove={onRemove}
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
