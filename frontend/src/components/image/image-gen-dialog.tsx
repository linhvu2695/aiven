import {
    Box,
    Dialog,
    Portal,
    CloseButton,
    Textarea,
    Button,
} from "@chakra-ui/react";
import { FaPaperPlane } from "react-icons/fa";
import { BASE_URL } from "@/App";
import { toaster } from "../ui/toaster";
import { Dropdown } from "@/components/ui/dropdown";
import { ASPECT_RATIO_OPTIONS } from "@/types/image";
import { ImageGenProviderSelector } from "./image-gen-provider-selector";
import { ImageGenPromptSelector } from "./image-gen-prompt-selector";
import { ImageGenProvider, useImageGen } from "@/context/image-gen-ctx";
import { useImage } from "@/context/image-ctx";
import { useEffect } from "react";
import { useColorMode } from "@/components/ui/color-mode";

interface ImageGenDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}

const ImageGenDialogContent = ({ isOpen, onClose, onSuccess }: ImageGenDialogProps) => {
    const { selectedImage } = useImage();
    const { colorMode } = useColorMode();
    const {
        prompt,
        setPrompt,
        imageId,
        setImageId,
        aspectRatio,
        setAspectRatio,
        model,
        isGenerating,
        setIsGenerating,
        resetState,
    } = useImageGen();

    // Set imageId from selectedImage when dialog opens
    useEffect(() => {
        if (isOpen && selectedImage?.id) {
            setImageId(selectedImage.id);
        }
    }, [isOpen, selectedImage?.id, setImageId]);

    const validateRequiredFields = (fieldName: string, fieldValue: string) => {
        if (!fieldValue.trim()) {
            toaster.create({
                description: `Missing ${fieldName}`,
                type: "warning",
            });
            return false;
        }
        return true;
    }

    const handleGenerateImage = async () => {
        if (!validateRequiredFields("prompt", prompt) 
            || !validateRequiredFields("model", model) 
            || !validateRequiredFields("aspect ratio", aspectRatio)) {
            return;
        }

        try {
            setIsGenerating(true);

            let url = `${BASE_URL}/api/image/generate?prompt=${encodeURIComponent(prompt)}&aspect_ratio=${encodeURIComponent(aspectRatio)}&model=${encodeURIComponent(model)}`;
            if (imageId) {
                url += `&image_id=${encodeURIComponent(imageId)}`;
            }
            
            const response = await fetch(url, 
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                }
            );

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
            resetState();
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
                    <Dialog.Content 
                        bg={colorMode === "dark" ? "rgba(0, 0, 0, 0.80)" : "rgba(255, 255, 255, 0.80)"}
                        backdropFilter="blur(8px)"
                    >
                        <Dialog.Header>
                            <Dialog.Title>{selectedImage?.id ? "Edit Image" : "Generate Image"}</Dialog.Title>
                        </Dialog.Header>

                        <Dialog.Body>
                            <Box
                                display="flex"
                                flexDirection="column"
                                gap={4}
                                paddingX={4}
                            >
                                {/* Prompt Input and Send Button */}
                                <Box
                                    display="flex"
                                    flexDirection="row"
                                    alignItems="center"
                                    justifyContent="space-between"
                                    gap={4}
                                    minH="40px"
                                >
                                    <Textarea
                                        outline="none"
                                        border="none"
                                        placeholder={selectedImage?.id 
                                            ? "Describe the changes you want to make to the image" 
                                            : "Describe the image you want to generate"}
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
                                            bgColor: "primary.500",
                                            boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
                                        }}
                                        onClick={handleGenerateImage}
                                        disabled={isGenerating}
                                        loading={isGenerating}
                                    >
                                        <FaPaperPlane size="3rem" />
                                    </Button>
                                </Box>

                                {/* Prompt Templates - Only show when editing existing image */}
                                {selectedImage?.id && (
                                    <ImageGenPromptSelector 
                                        onSelectPrompt={setPrompt}
                                        disabled={isGenerating}
                                    />
                                )}

                                {/* Settings Panel */}
                                <Box
                                    display="flex"
                                    flexDirection="row"
                                    gap={4}
                                    padding={4}
                                    _dark={{
                                        borderColor: "gray.600",
                                    }}
                                >
                                    {/* Provider and Model Selector */}
                                    <Box flex={1}>
                                        <ImageGenProviderSelector />
                                    </Box>

                                    {/* Aspect Ratio Selector */}
                                    <Box flex={1}>
                                        <Dropdown
                                            title="Aspect Ratio"
                                            value={aspectRatio}
                                            onValueChange={setAspectRatio}
                                            options={ASPECT_RATIO_OPTIONS}
                                            placeholder="Select aspect ratio"
                                            disabled={isGenerating}
                                            fontSize="sm"
                                            fontWeight="medium"
                                            mb={0}
                                        />
                                    </Box>
                                </Box>
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

// Wrapper component that provides the context
export const ImageGenDialog = (props: ImageGenDialogProps) => {
    return (
        <ImageGenProvider>
            <ImageGenDialogContent {...props} />
        </ImageGenProvider>
    );
};

export default ImageGenDialog;