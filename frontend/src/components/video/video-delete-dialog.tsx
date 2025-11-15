import {
    Dialog,
    Portal,
    CloseButton,
    Button,
    Spinner,
} from "@chakra-ui/react";
import { useState } from "react";
import { toaster } from "@/components/ui/toaster";
import { BASE_URL } from "@/App";

interface VideoDeleteDialogProps {
    isOpen: boolean;
    onClose: () => void;
    videoId: string;
    videoName?: string;
    onDelete?: () => void;
}

export const VideoDeleteDialog = ({
    isOpen,
    onClose,
    videoId,
    videoName,
    onDelete,
}: VideoDeleteDialogProps) => {
    const [isDeleting, setIsDeleting] = useState(false);

    const handleDelete = async () => {
        setIsDeleting(true);
        try {
            const res = await fetch(BASE_URL + `/api/video/${videoId}`, {
                method: "DELETE",
            });
            if (res.ok) {
                toaster.create({
                    description: "Video deleted successfully",
                    type: "success",
                });
            } else {
                console.log(res);
                toaster.create({
                    description: "Failed to delete video",
                    type: "error",
                });
            }
        } catch (err) {
            console.log(err);
            toaster.create({
                description: "Error deleting video",
                type: "error",
            });
        } finally {
            setIsDeleting(false);
        }
        
        onClose();
        if (onDelete) onDelete();
    };

    return (
        <Dialog.Root
            open={isOpen}
            onOpenChange={(e) => {
                if (!e.open) onClose();
            }}
            size="sm"
            placement="center"
        >
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content>
                        <Dialog.Header>
                            <Dialog.Title>Delete Video</Dialog.Title>
                        </Dialog.Header>
                        <Dialog.Body>
                            Do you want to delete video <b>{videoName || videoId}</b>?
                        </Dialog.Body>
                        <Dialog.Footer>
                            <Dialog.ActionTrigger asChild>
                                <Button variant="solid" disabled={isDeleting}>
                                    Cancel
                                </Button>
                            </Dialog.ActionTrigger>
                            <Button
                                variant={"outline"}
                                colorScheme="red"
                                onClick={handleDelete}
                                disabled={isDeleting}
                            >
                                {isDeleting ? (
                                    <>
                                        <Spinner size="sm" mr={2} />
                                        Deleting...
                                    </>
                                ) : (
                                    "Delete"
                                )}
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

export default VideoDeleteDialog;

