import {
    Button,
    CloseButton,
    Container,
    Dialog,
    Portal,
    useDisclosure,
} from "@chakra-ui/react";
import { AgentCard } from "./agent-card";
import { AgentSelectionGrid } from "./agent-selection-grid";
import { useChat } from "@/context/chat-ctx";

export const AgentContainer = () => {
    const { open, onOpen, onClose } = useDisclosure();
    const { resetMessages } = useChat();

    const handleAgentSelect = () => {
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
                        bgColor: "teal.500",
                        boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
                    }}
                    onClick={onOpen}
                    data-testid="select-agent-button"
                >
                    Select Agent
                </Button>
            </Container>

            {/* Select agent popup */}
            <Dialog.Root
                open={open}
                onOpenChange={(e) => {
                    if (!e.open) onClose();
                }}
                size="xl"
                placement="center"
            >
                <Portal>
                    <Dialog.Backdrop />
                    <Dialog.Positioner>
                        <Dialog.Content>
                            <Dialog.Header>
                                <Dialog.Title>Select an Agent</Dialog.Title>
                            </Dialog.Header>

                            <Dialog.Body>
                                <AgentSelectionGrid onSelect={handleAgentSelect} />
                            </Dialog.Body>

                            <Dialog.CloseTrigger asChild>
                                <CloseButton size="sm" />
                            </Dialog.CloseTrigger>
                        </Dialog.Content>
                    </Dialog.Positioner>
                </Portal>
            </Dialog.Root>
        </>
    );
};
