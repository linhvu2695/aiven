import { Avatar, Box, HStack, Text } from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";

interface ChatMessageInfo {
    content: string;
    role: string;
}

const roleBgColor: Record<string, string> = {
    user: "teal.500",
    assistant: "gray.600",
};

export const ChatMessage = (msg: ChatMessageInfo) => {
    return (
        <HStack
            flexDirection={msg.role === "user" ? "row-reverse" : "row"}
            spaceX={4}
        >
            <Avatar.Root size={"sm"}>
                <Avatar.Image
                    src={msg.role === "user" ? "/astronaut2.webp" : "/dinosaur.jpg"}
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
