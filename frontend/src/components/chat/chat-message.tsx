import { Avatar, Box, HStack, Text } from "@chakra-ui/react";

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
                <Text whiteSpace="pre-wrap">{msg.content}</Text>
            </Box>
        </HStack>
    );
};
