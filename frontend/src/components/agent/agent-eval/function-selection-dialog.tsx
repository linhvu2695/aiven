import {
    Dialog,
    Portal,
    CloseButton,
} from "@chakra-ui/react";
import { FunctionSelectionGrid } from "./function-selection-grid";

interface FunctionSelectionDialogProps {
    isOpen: boolean;
    onClose: () => void;
}

export const FunctionSelectionDialog = ({
    isOpen,
    onClose,
}: FunctionSelectionDialogProps) => {
    return (
        <Dialog.Root
            open={isOpen}
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
                            <Dialog.Title>
                                Select Expected Tool Call
                            </Dialog.Title>
                        </Dialog.Header>

                        <Dialog.Body>
                            <FunctionSelectionGrid onClose={onClose} />
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

