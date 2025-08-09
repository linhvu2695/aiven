import { 
    Box, 
    Drawer,
    VStack,
    Text,
    Button,
    Separator
} from "@chakra-ui/react";
import { useChat } from "@/context/chat-ctx";
import { BASE_URL } from "@/App";
import type { ChatMessageInfo } from "@/components/chat/chat-message-info";

export interface ConversationInfo {
    session_id: string;
    name: string;
    updated_at: string;
}

interface ConversationDrawerProps {
    isOpen: boolean;
    onClose: () => void;
    conversations: ConversationInfo[];
}

export const ConversationDrawer = ({ 
    isOpen, 
    onClose, 
    conversations 
}: ConversationDrawerProps) => {
    const { setSessionId, setMessages } = useChat();

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const convertMessagesToChatMessageInfo = (messages: any[]): ChatMessageInfo[] => {
        return messages.map((msg) => {
            // Handle different message types from LangChain BaseMessage
            let role = "assistant"; // default
            
            if (msg.type === "human" || msg.type === "user") {
                role = "user";
            } else if (msg.type === "ai" || msg.type === "assistant") {
                role = "assistant";
            } else if (msg.type === "system") {
                role = "system";
            }

            return {
                content: msg.content || "",
                role: role,
                // Note: Files are not preserved in stored conversations for now
                file: undefined,
                filePreview: null
            };
        });
    };

    const loadConversation = async (sessionId: string) => {
        try {
            const response = await fetch(
                `${BASE_URL}/api/chat/conversations/${sessionId}`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                }
            );

            if (!response.ok) {
                throw new Error("Failed to fetch conversation");
            }

            const conversation = await response.json();
            
            // Convert messages from BaseMessage format to ChatMessageInfo format
            const chatMessages = convertMessagesToChatMessageInfo(conversation.messages || []);
            
            // Update chat context with loaded conversation
            setSessionId(sessionId);
            setMessages(chatMessages);
            
        } catch (error) {
            console.error("Error loading conversation:", error);
        }
    };

    const handleConversationClick = async (sessionId: string) => {
        await loadConversation(sessionId);
        onClose();
    };

    return (
        <Drawer.Root 
            open={isOpen} 
            onOpenChange={(e) => !e.open && onClose()}
            placement="start"
            size="md"
        >
            <Drawer.Backdrop />
            <Drawer.Positioner>
                <Drawer.Content>
                    <Drawer.Header>
                        <Drawer.Title>
                            <Text fontSize="lg" fontWeight="bold">Recent Conversations</Text>
                        </Drawer.Title>
                        <Text fontSize="sm" color="gray.500">Latest 100</Text>
                        <Drawer.CloseTrigger />
                    </Drawer.Header>

                    <Drawer.Body padding={0}>
                        <VStack gap={0} align="stretch">
                            {conversations.length === 0 ? (
                                <Box p={4}>
                                    <Text color="gray.500">No conversations found</Text>
                                </Box>
                            ) : (
                                conversations.map((conversation, index) => (
                                    <Box key={conversation.session_id}>
                                        <Button
                                            variant="ghost"
                                            width="100%"
                                            height="auto"
                                            py={3}
                                            px={4}
                                            justifyContent="flex-start"
                                            textAlign="left"
                                            borderRadius={0}
                                            _hover={{ bg: { _dark: "teal.800", base: "gray.200" }}}
                                            onClick={() => handleConversationClick(conversation.session_id)}
                                        >
                                            <VStack align="flex-start" gap={1} width="100%">
                                                <Text fontSize="sm" fontWeight="medium" lineClamp={2}>
                                                    {conversation.name || `Conversation ${conversation.session_id.slice(-8)}`}
                                                </Text>
                                                <Text fontSize="xs" color="gray.500">
                                                    {formatDate(conversation.updated_at)}
                                                </Text>
                                            </VStack>
                                        </Button>
                                        {index < conversations.length - 1 && <Separator />}
                                    </Box>
                                ))
                            )}
                        </VStack>
                    </Drawer.Body>
                </Drawer.Content>
            </Drawer.Positioner>
        </Drawer.Root>
    );
};