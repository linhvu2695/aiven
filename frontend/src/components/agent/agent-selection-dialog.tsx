import { CloseButton, Dialog, Portal } from "@chakra-ui/react";
import { type Agent } from "@/context/agent-ctx";
import { AgentSelectionGrid } from "./agent-selection-grid";

interface AgentSelectionDialogProps {
    open: boolean;
    onClose: () => void;
    title: string;
    onAgentSelect: (agent: Agent) => void;
}

export const AgentSelectionDialog = ({
    open,
    onClose,
    title,
    onAgentSelect,
}: AgentSelectionDialogProps) => {
    return (
        <Dialog.Root
            open={open}
            onOpenChange={(e) => {
                if (!e.open) {
                    onClose();
                }
            }}
            size="xl"
            placement="center"
        >
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content>
                        <Dialog.Header>
                            <Dialog.Title>{title}</Dialog.Title>
                        </Dialog.Header>

                        <Dialog.Body>
                            <AgentSelectionGrid onAgentSelect={onAgentSelect} />
                        </Dialog.Body>

                        <Dialog.CloseTrigger asChild>
                            <CloseButton size="sm" />
                        </Dialog.CloseTrigger>
                    </Dialog.Content>
                </Dialog.Positioner>
            </Portal>
        </Dialog.Root>
    );
};

