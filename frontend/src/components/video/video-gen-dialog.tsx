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
import { VIDEO_ASPECT_RATIO_OPTIONS, VIDEO_DURATION_OPTIONS } from "@/types/video";
import { VideoGenProviderSelector } from "./video-gen-provider-selector";
import { VideoGenProvider, useVideoGen } from "@/context/video-gen-ctx";
import { useColorMode } from "@/components/ui/color-mode";

interface VideoGenDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}

const VideoGenDialogContent = ({ isOpen, onClose, onSuccess }: VideoGenDialogProps) => {
    const { colorMode } = useColorMode();
    const {
        prompt,
        setPrompt,
        imageId,
        aspectRatio,
        setAspectRatio,
        duration,
        setDuration,
        model,
        isGenerating,
        setIsGenerating,
        resetState,
    } = useVideoGen();

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

    const handleGenerateVideo = async () => {
        if (!validateRequiredFields("prompt", prompt) 
            || !validateRequiredFields("model", model) 
            || !validateRequiredFields("aspect ratio", aspectRatio)) {
            return;
        }

        try {
            setIsGenerating(true);

            let url = `${BASE_URL}/api/video/generate?prompt=${encodeURIComponent(prompt)}&aspect_ratio=${encodeURIComponent(aspectRatio)}&model=${encodeURIComponent(model)}&duration=${duration}`;
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
                throw new Error(`Failed to generate video: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success) {
                toaster.create({
                    description: `Video generation job created! Job ID: ${result.job_id}`,
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
                    description: result.message || "Failed to generate video",
                    type: "error",
                });
            }
        } catch (error) {
            console.error("Error generating video:", error);
            toaster.create({
                description: error instanceof Error ? error.message : "Failed to generate video",
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
                            <Dialog.Title>Generate Video</Dialog.Title>
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
                                        placeholder="Describe the video you want to generate"
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
                                        onClick={handleGenerateVideo}
                                        disabled={isGenerating}
                                        loading={isGenerating}
                                    >
                                        <FaPaperPlane size="3rem" />
                                    </Button>
                                </Box>

                                {/* Settings Panel */}
                                <Box
                                    display="flex"
                                    flexDirection="column"
                                    gap={4}
                                    padding={4}
                                    _dark={{
                                        borderColor: "gray.600",
                                    }}
                                >
                                    {/* Provider and Model Selector */}
                                    <Box flex={1}>
                                        <VideoGenProviderSelector />
                                    </Box>

                                    {/* Aspect Ratio and Duration Selectors */}
                                    <Box
                                        display="flex"
                                        flexDirection="row"
                                        gap={4}
                                    >
                                        {/* Aspect Ratio Selector */}
                                        <Box flex={1}>
                                            <Dropdown
                                                title="Aspect Ratio"
                                                value={aspectRatio}
                                                onValueChange={setAspectRatio}
                                                options={VIDEO_ASPECT_RATIO_OPTIONS}
                                                placeholder="Select aspect ratio"
                                                disabled={isGenerating}
                                                fontSize="sm"
                                                fontWeight="medium"
                                                mb={0}
                                            />
                                        </Box>

                                        {/* Duration Selector */}
                                        <Box flex={1}>
                                            <Dropdown
                                                title="Duration"
                                                value={duration.toString()}
                                                onValueChange={(val) => setDuration(parseInt(val))}
                                                options={VIDEO_DURATION_OPTIONS}
                                                placeholder="Select duration"
                                                disabled={isGenerating}
                                                fontSize="sm"
                                                fontWeight="medium"
                                                mb={0}
                                            />
                                        </Box>
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
export const VideoGenDialog = (props: VideoGenDialogProps) => {
    return (
        <VideoGenProvider>
            <VideoGenDialogContent {...props} />
        </VideoGenProvider>
    );
};

export default VideoGenDialog;

