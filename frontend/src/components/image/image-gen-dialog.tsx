import {
    Box,
    Dialog,
    Portal,
    CloseButton,
    Textarea,
    Button,
} from "@chakra-ui/react";
import { FaPaperPlane } from "react-icons/fa";
import { useState } from "react";
import { BASE_URL } from "@/App";
import { toaster } from "../ui/toaster";

interface ImageGenDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}

export const ImageGenDialog = ({ isOpen, onClose, onSuccess }: ImageGenDialogProps) => {
    const [prompt, setPrompt] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);

    const handleGenerateImage = async () => {
        if (!prompt.trim()) {
            toaster.create({
                description: "Please enter a prompt",
                type: "warning",
            });
            return;
        }

        try {
            setIsGenerating(true);
            
            const response = await fetch(`${BASE_URL}/api/image/generate?prompt=${encodeURIComponent(prompt)}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error(`Failed to generate image: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success) {
                toaster.create({
                    description: "Image generated successfully!",
                    type: "success",
                });
                
                // Reset and close
                setPrompt("");
                onClose();
                
                // Call success callback if provided
                if (onSuccess) {
                    onSuccess();
                }
            } else {
                toaster.create({
                    description: result.message || "Failed to generate image",
                    type: "error",
                });
            }
        } catch (error) {
            console.error("Error generating image:", error);
            toaster.create({
                description: error instanceof Error ? error.message : "Failed to generate image",
                type: "error",
            });
        } finally {
            setIsGenerating(false);
        }
    };

    const handleClose = () => {
        if (!isGenerating) {
            setPrompt("");
            onClose();
        }
    };

    return (
        <Dialog.Root 
            open={isOpen} 
            onOpenChange={(e) => {
                if (!e.open) {
                    handleClose();
                }
            }}
            size="lg"
            placement="center"
        >
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content>
                        <Dialog.Header>
                            <Dialog.Title>Generate Image</Dialog.Title>
                        </Dialog.Header>

                        <Dialog.Body>
                            <Box
                                display="flex"
                                flexDirection="row"
                                alignItems="center"
                                justifyContent="space-between"
                                gap={4}
                                paddingX={4}
                                minH="40px"
                            >
                                <Textarea
                                    outline="none"
                                    border="none"
                                    placeholder="Describe the image you want to generate"
                                    value={prompt}
                                    onChange={(e) => {
                                        setPrompt(e.target.value);
                                    }}
                                    disabled={isGenerating}
                                    minH="120px"
                                    resize="vertical"
                                />
                                
                                {/* Send button */}
                                <Button
                                    alignItems="center"
                                    justifyContent="center"
                                    padding="8px"
                                    transition="all 0.3s ease"
                                    _hover={{
                                        transform: "scale(1.1)",
                                        bgColor: "teal.500",
                                        boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
                                    }}
                                    onClick={handleGenerateImage}
                                    disabled={isGenerating}
                                    loading={isGenerating}
                                >
                                    <FaPaperPlane size="3rem" />
                                </Button>
                            </Box>
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

export default ImageGenDialog;

