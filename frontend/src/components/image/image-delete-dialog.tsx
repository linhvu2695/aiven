import {
    Dialog,
    Portal,
    CloseButton,
    Button,
} from "@chakra-ui/react";
import { toaster } from "@/components/ui/toaster";
import { BASE_URL } from "@/App";

interface ImageDeleteDialogProps {
    isOpen: boolean;
    onClose: () => void;
    imageId: string;
    imageName?: string;
    onDelete?: () => void;
}

export const ImageDeleteDialog = ({
    isOpen,
    onClose,
    imageId,
    imageName,
    onDelete,
}: ImageDeleteDialogProps) => {
    const handleDelete = async () => {
        try {
            const res = await fetch(BASE_URL + `/api/image/${imageId}`, {
                method: "DELETE",
            });
            if (res.ok) {
                toaster.create({
                    description: "Image deleted successfully",
                    type: "success",
                });
            } else {
                console.log(res);
                toaster.create({
                    description: "Failed to delete image",
                    type: "error",
                });
            }
        } catch (err) {
            console.log(err);
            toaster.create({
                description: "Error deleting image",
                type: "error",
            });
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
                            <Dialog.Title>Delete Image</Dialog.Title>
                        </Dialog.Header>
                        <Dialog.Body>
                            Do you want to delete image <b>{imageName || imageId}</b>?
                        </Dialog.Body>
                        <Dialog.Footer>
                            <Dialog.ActionTrigger asChild>
                                <Button variant="solid">Cancel</Button>
                            </Dialog.ActionTrigger>
                            <Button
                                variant={"outline"}
                                colorScheme="red"
                                onClick={handleDelete}
                            >
                                Delete
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

export default ImageDeleteDialog;

