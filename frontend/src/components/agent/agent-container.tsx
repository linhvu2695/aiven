import { Button, Container, useDisclosure } from "@chakra-ui/react";
import { AgentCard } from "./agent-card";
import { AgentSelectionDialog } from "./agent-selection-dialog";
import { useChat } from "@/context/chat-ctx";
import { useAgent, type Agent } from "@/context/agent-ctx";

export const AgentContainer = () => {
    const { open, onOpen, onClose } = useDisclosure();
    const { resetMessages } = useChat();
    const { setAgent } = useAgent();

    const handleAgentSelect = (agent: Agent) => {
        setAgent(agent);
        resetMessages();
        onClose();
    };
    return (
        <>
            <Container
                margin={4}
                display="flex"
                flexDirection="column"
                alignItems="center"
                gap={4}
                data-testid="agent-container"
            >
                <AgentCard />
                <Button
                    borderRadius={"18px"}
                    _hover={{
                        transform: "scale(1.1)",
                        bgColor: "primary.500",
                        boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
                    }}
                    onClick={onOpen}
                    data-testid="select-agent-button"
                >
                    Select Agent
                </Button>
            </Container>

            {/* Select agent popup */}
            <AgentSelectionDialog
                open={open}
                onClose={onClose}
                title="Select an Agent"
                onAgentSelect={handleAgentSelect}
            />
        </>
    );
};
