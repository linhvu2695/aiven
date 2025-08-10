import { BASE_URL } from "@/App";
import { AgentContainer } from "@/components/agent/agent-container";
import { ChatContainer } from "@/components/chat/chat-container";
import { ConversationDrawer, type ConversationInfo } from "@/components/chat/conversation-drawer";
import { useAgent } from "@/context/agent-ctx";
import { 
    Box, 
    HStack, 
    IconButton
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { LuMessageSquare } from "react-icons/lu";

export const AgentChatPage = () => {
    const { agent, setAgent, setAgentDraft } = useAgent();
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);
    const [conversations, setConversations] = useState<ConversationInfo[]>([]);

    const fetchConversations = async () => {
        try {
            const response = await fetch(
                BASE_URL + "/api/chat/conversations?limit=100",
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                }
            );

            if (!response.ok) throw new Error("Failed to fetch conversations");
            const data = await response.json();
            setConversations(data);
        } catch (error) {
            console.error("Error fetching conversations:", error);
        }
    };

    const handleConversationDeleted = (sessionId: string) => {
        // Remove the deleted conversation from the list
        setConversations(prevConversations => 
            prevConversations.filter(conversation => conversation.session_id !== sessionId)
        );
    };

    useEffect(() => {
        const fetchAgent = async () => {
            try {
                const response = await fetch(
                    BASE_URL + `/api/agent/id=${agent?.id ?? "685fff58d3367dc42c178987"}`,
                    {
                        method: "GET",
                        headers: {
                            "Content-Type": "application/json",
                        },
                    }
                );

                if (!response.ok) throw new Error("Failed to fetch agent info");
                const data = await response.json();
                setAgent(data);
                setAgentDraft(data);
            } catch (error) {
                console.error("Error fetching agent info:", error);
            }
        };
        fetchAgent();
    }, [agent?.id]);


    return (
        <>
            <HStack as="main" position="relative">
                <IconButton
                    aria-label="Open conversations"
                    onClick={() => {
                        setIsDrawerOpen(true);
                        fetchConversations();
                    }}
                    size={"sm"}
                    position="absolute"
                    top={0}
                    left={6}
                    zIndex={10}
                    variant="solid"
                    _hover={{
                        transform: "scale(1.1)",
                        bgColor: "teal.500",
                    }}
                >
                    <LuMessageSquare />
                </IconButton>
                
                <Box as="aside" flex={1} height={"88vh"}>
                    <AgentContainer />
                </Box>
                <Box as="section" flex={2} height={"88vh"}>
                    <ChatContainer />
                </Box>
            </HStack>

            <ConversationDrawer
                isOpen={isDrawerOpen}
                onClose={() => setIsDrawerOpen(false)}
                conversations={conversations}
                onConversationDeleted={handleConversationDeleted}
            />
        </>
    );
};
