import { 
    Box, 
    Drawer,
    VStack,
    Text,
    Button,
    Separator
} from "@chakra-ui/react";

export interface ConversationInfo {
    session_id: string;
    name: string;
    updated_at: string;
}

interface ConversationDrawerProps {
    isOpen: boolean;
    onClose: () => void;
    conversations: ConversationInfo[];
    onConversationSelect?: (sessionId: string) => void;
}

export const ConversationDrawer = ({ 
    isOpen, 
    onClose, 
    conversations, 
    onConversationSelect 
}: ConversationDrawerProps) => {
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const handleConversationClick = (sessionId: string) => {
        if (onConversationSelect) {
            onConversationSelect(sessionId);
        } else {
            // Fallback behavior
            console.log("Selected conversation:", sessionId);
        }
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