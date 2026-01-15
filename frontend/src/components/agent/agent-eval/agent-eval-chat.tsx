import {
    Stack,
    Box,
    HStack,
    Avatar,
    Textarea,
    Popover,
    VStack,
    IconButton,
    Text,
} from "@chakra-ui/react";
import { useState } from "react";
import { ChatMessage } from "../../chat";
import { FaPlus } from "react-icons/fa";
import { useAgent } from "@/context/agent-ctx";
import { useAgentEval } from "@/context/agent-eval-ctx";
import { useColorMode } from "../../ui";
import { DEFAULT_USER_AVATAR } from "@/utils/constants";

interface RoleAvatarOptionProps {
    role: "user" | "assistant";
    selectedRole: "user" | "assistant";
    avatarSrc: string;
    label: string;
    onSelect: () => void;
    showFallback?: boolean;
    fallbackName?: string;
}

const RoleAvatarOption = ({
    role,
    selectedRole,
    avatarSrc,
    label,
    onSelect,
    showFallback = false,
    fallbackName,
}: RoleAvatarOptionProps) => {
    const isSelected = selectedRole === role;

    return (
        <VStack
            gap={1}
            cursor="pointer"
            p={2}
            borderRadius="md"
            bg={isSelected ? "primary.600" : "gray.700"}
            _hover={{
                bg: isSelected ? "primary.600" : "gray.600",
            }}
            onClick={onSelect}
            flex={1}
        >
            <Avatar.Root size={"md"}>
                    <Avatar.Image
                                        src={avatarSrc}
                                        borderColor={isSelected ? "primary.400" : "gray.500"}
                                    />
                {showFallback && <Avatar.Fallback name={fallbackName} />}
            </Avatar.Root>
            <Text fontSize="xs" color="white">
                {label}
            </Text>
        </VStack>
    );
};

export const AgentEvalChat = () => {
    const { colorMode } = useColorMode();
    const { agent } = useAgent();
    const { messages, addMessage, setMessages, selectedRole, setSelectedRole } = useAgentEval();
    const [input, setInput] = useState("");
    const [isRolePopoverOpen, setIsRolePopoverOpen] = useState(false);

    const handleAddMessage = () => {
        if (!input.trim()) return;
        addMessage(input, selectedRole);
        setInput("");
        // Reset to default for next message (alternating)
        setSelectedRole(selectedRole === "user" ? "assistant" : "user");
    };

    const handleRemoveMessage = (idx: number) => {
        setMessages(messages.filter((_, i) => i !== idx));
    };

    return (
        <Stack
            className="agent-eval-messages"
            gap={0}
            align="stretch"
            overflowY="auto"
            w="50%"
            h="100%"
            bg={colorMode === "dark" ? "gray.900" : "gray.100"}
            borderRadius="12px"
        >
            {/* Messages */}
            <Stack
                spaceY={3}
                align="stretch"
                overflowY="auto"
                p={4}
                flex={1}
                minH={0}
            >
                {messages.map((msg, idx) => (
                    <ChatMessage
                        key={idx}
                        content={msg.content}
                        role={msg.role}
                        onRemove={() => {
                            handleRemoveMessage(idx);
                        }}
                    />
                ))}
            </Stack>

            {/* Chat input box */}
            <Box p={4} borderTop="1px" bg={colorMode === "dark" ? "gray.800" : "gray.200"}>
                <HStack gap={3} alignItems="flex-end">
                    {/* Avatar with Popover */}
                    <Popover.Root
                        open={isRolePopoverOpen}
                        onOpenChange={(e) => setIsRolePopoverOpen(e.open)}
                    >
                        {/* Avatar */}
                        <Popover.Trigger asChild>
                            <Box
                                cursor="pointer"
                                _hover={{
                                    transform: "scale(1.1)",
                                    transition: "transform 0.2s",
                                }}
                            >
                                <Avatar.Root size={"sm"} flexShrink={0}>
                                    <Avatar.Image
                                        src={selectedRole === "user" ? DEFAULT_USER_AVATAR : agent?.avatar_image_url}
                                        borderWidth="2px"
                                        borderColor={selectedRole === "user" ? "primary.500" : "primary.400"}
                                    />
                                    {!agent?.avatar_image_url && selectedRole === "assistant" && (
                                        <Avatar.Fallback name={agent?.name} />
                                    )}
                                </Avatar.Root>
                            </Box>
                        </Popover.Trigger>

                        {/* Popover */}
                        <Popover.Positioner>
                            <Popover.Content
                                bg={colorMode === "dark" ? "gray.800" : "gray.200"}
                                borderRadius="md"
                                p={3}
                                w="150px"
                            >
                                <VStack gap={2}>
                                    <HStack gap={3}>
                                        <RoleAvatarOption
                                            role="user"
                                            selectedRole={selectedRole}
                                            avatarSrc={DEFAULT_USER_AVATAR}
                                            label="User"
                                            onSelect={() => {
                                                setSelectedRole("user");
                                                setIsRolePopoverOpen(false);
                                            }}
                                        />
                                        <RoleAvatarOption
                                            role="assistant"
                                            selectedRole={selectedRole}
                                            avatarSrc={agent?.avatar_image_url || ""}
                                            label="Agent"
                                            onSelect={() => {
                                                setSelectedRole("assistant");
                                                setIsRolePopoverOpen(false);
                                            }}
                                            showFallback={!agent?.avatar_image_url}
                                            fallbackName={agent?.name}
                                        />
                                    </HStack>
                                </VStack>
                            </Popover.Content>
                        </Popover.Positioner>
                    </Popover.Root>

                    {/* Input */}
                    <Textarea
                        placeholder={selectedRole === "user" ? "Type your message..." : "Type agent's message..."}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault();
                                handleAddMessage();
                            }
                        }}
                        resize="none"
                        minH="60px"
                        maxH="120px"
                        flex={1}
                        bg={colorMode === "dark" ? "gray.800" : "gray.200"}
                        borderRadius="12px"
                        _focus={{
                            borderColor: "primary.500",
                            boxShadow: "0 0 0 1px var(--chakra-colors-primary-500)",
                        }}
                    />

                    {/* Add button */}
                    <IconButton
                        onClick={handleAddMessage}
                        disabled={!input.trim()}
                        aria-label="Add message"
                        flexShrink={0}
                        size={"sm"}
                        variant="solid"
                        _hover={{
                            transform: "scale(1.1)",
                            bgColor: "primary.500",
                        }}
                        transition="transform 0.2s"
                    >
                        <FaPlus />
                    </IconButton>
                </HStack>
            </Box>
        </Stack>
    );
};

