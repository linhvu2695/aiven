import { BASE_URL } from "@/App";
import { AgentContainer } from "@/components/agent";
import { AgentEvalContainer } from "@/components/agent/agent-eval-container";
import {
    ChatContainer,
    ConversationDrawer,
    type ConversationInfo,
} from "@/components/chat";
import { useAgent } from "@/context/agent-ctx";
import { AgentEvalProvider } from "@/context/agent-eval-ctx";
import { Box, HStack, IconButton, Text, VStack } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { FaRegComment } from "react-icons/fa";
import { FaClockRotateLeft, FaScaleBalanced } from "react-icons/fa6";

enum AgentContainerState {
    CHAT = "chat",
    EVALUATE = "evaluate",
}

export const AgentChatPage = () => {
    const { agent, setAgent, setAgentDraft } = useAgent();
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);
    const [agentContainerState, setAgentContainerState] = useState(
        AgentContainerState.EVALUATE
    );
    const [conversations, setConversations] = useState<ConversationInfo[]>([]);

    const fetchConversations = async () => {
        try {
            // Include agent_id in the API call to filter conversations by current agent
            const agentId = agent?.id || "";
            const response = await fetch(
                BASE_URL +
                    `/api/chat/conversations?limit=100&agent_id=${encodeURIComponent(
                        agentId
                    )}`,
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
        setConversations((prevConversations) =>
            prevConversations.filter(
                (conversation) => conversation.session_id !== sessionId
            )
        );
    };

    useEffect(() => {
        const fetchAgent = async () => {
            try {
                const response = await fetch(
                    BASE_URL +
                        `/api/agent/id=${
                            agent?.id ?? "685fff58d3367dc42c178987"
                        }`,
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

    // Refresh conversations when agent changes
    useEffect(() => {
        if (agent?.id && isDrawerOpen) {
            fetchConversations();
        }
    }, [agent?.id]);

    return (
        <>
            <HStack as="main" position="relative">
                <Box as="aside" flex={1} height={"88vh"} position="relative">
                    <AgentContainer />

                    {/* Agent buttons */}
                    <VStack
                        position="absolute"
                        top={10}
                        right={0}
                        zIndex={10}
                        gap={2}
                    >
                        {/* Chat button */}
                        <AgentButton
                            label="Chat"
                            icon={<FaRegComment />}
                            onClick={() =>
                                setAgentContainerState(AgentContainerState.CHAT)
                            }
                        />

                        {/* Open conversations button */}
                        <AgentButton
                            label="Open conversations"
                            icon={<FaClockRotateLeft />}
                            onClick={() => {
                                setAgentContainerState(
                                    AgentContainerState.CHAT
                                );
                                setIsDrawerOpen(true);
                                fetchConversations();
                            }}
                        />
                        <AgentButton
                            label="Evaluate agent"
                            icon={<FaScaleBalanced />}
                            onClick={() =>
                                setAgentContainerState(
                                    AgentContainerState.EVALUATE
                                )
                            }
                        />
                    </VStack>
                </Box>

                <Box as="section" flex={2} height={"88vh"}>
                    {agentContainerState === AgentContainerState.EVALUATE && (
                        <AgentEvalProvider>
                            <AgentEvalContainer />
                        </AgentEvalProvider>
                    )}
                    {agentContainerState === AgentContainerState.CHAT && (
                        <ChatContainer />
                    )}
                </Box>
            </HStack>

            <ConversationDrawer
                isOpen={isDrawerOpen}
                onClose={() => setIsDrawerOpen(false)}
                conversations={conversations}
                onConversationDeleted={handleConversationDeleted}
                agentName={agent?.name}
            />
        </>
    );
};

const AgentButton = ({
    label,
    icon,
    onClick,
}: {
    label: string;
    icon: React.ReactNode;
    onClick: () => void;
}) => {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <Box
            position="relative"
            display="flex"
            alignItems="center"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <IconButton
                aria-label={label}
                onClick={onClick}
                size={"sm"}
                variant="solid"
                _hover={{ transform: "scale(1.1)", bgColor: "teal.500" }}
                transition="transform 0.2s"
            >
                {icon}
            </IconButton>

            {/* Ribbon tooltip */}
            <Box
                position="absolute"
                left="100%"
                ml={2}
                overflow="hidden"
                whiteSpace="nowrap"
                transition="max-width 0.3s ease-in-out, opacity 0.3s ease-in-out"
                maxWidth={isHovered ? "200px" : "0"}
                opacity={isHovered ? 1 : 0}
                pointerEvents="none"
            >
                <Box
                    bg="teal.500"
                    color="white"
                    px={3}
                    py={1.5}
                    borderRadius="md"
                    boxShadow="md"
                    position="relative"
                >
                    <Text fontSize="sm" fontWeight="medium">
                        {label}
                    </Text>
                </Box>
            </Box>
        </Box>
    );
};
