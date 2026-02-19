import {
    Dialog,
    Portal,
    Button,
    Input,
    VStack,
    Text,
    CloseButton,
} from "@chakra-ui/react";
import { useState } from "react";
import { BASE_URL } from "@/App";
import { toaster } from "@/components/ui/toaster";

interface LinkAuthTokenDialogProps {
    isOpen: boolean;
    onClose: () => void;
}

export const LinkAuthTokenDialog = ({ isOpen, onClose }: LinkAuthTokenDialogProps) => {
    const [token, setToken] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async () => {
        if (!token.trim()) {
            toaster.create({ description: "Token is required", type: "error" });
            return;
        }
        setLoading(true);
        try {
            const res = await fetch(`${BASE_URL}/api/work/auth-token`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token: token.trim() }),
            });
            if (!res.ok) throw new Error("Failed to set token");
            toaster.create({ description: "Link auth token updated", type: "success" });
            setToken("");
            onClose();
        } catch (err) {
            toaster.create({ description: "Failed to set auth token", type: "error" });
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog.Root open={isOpen} onOpenChange={(e) => !e.open && onClose()} placement="center">
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content maxW="md">
                        <Dialog.Header>
                            <Dialog.Title>Set Link Auth Token</Dialog.Title>
                        </Dialog.Header>
                        <Dialog.Body>
                            <VStack align="stretch" gap={3}>
                                <Text fontSize="sm" color="fg.muted">
                                    Enter the Orange Logic Link API token to use for work-related requests.
                                </Text>
                                <Input
                                    type="password"
                                    placeholder="Token"
                                    value={token}
                                    onChange={(e) => setToken(e.target.value)}
                                    autoComplete="off"
                                />
                            </VStack>
                        </Dialog.Body>
                        <Dialog.Footer>
                            <Button variant="outline" onClick={onClose}>
                                Cancel
                            </Button>
                            <Button onClick={handleSubmit} loading={loading}>
                                Save
                            </Button>
                        </Dialog.Footer>
                        <Dialog.CloseTrigger asChild>
                            <CloseButton size="sm" />
                        </Dialog.CloseTrigger>
                    </Dialog.Content>
                </Dialog.Positioner>
            </Portal>
        </Dialog.Root>
    );
};
