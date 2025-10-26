import {
    Box,
    VStack,
    Text,
    Center,
    Dialog,
    Portal,
    CloseButton,
    Image,
    IconButton,
    Textarea,
    Button,
} from "@chakra-ui/react";
import { FaMagic, FaPaperPlane } from "react-icons/fa";
import { useImage } from "@/context/image-ctx";
import { Tooltip } from "../ui/tooltip";
import { useState } from "react";
import { BASE_URL } from "@/App";
import { toaster } from "../ui/toaster";

export const ImageDetailDialog = () => {
    const { selectedImage, isDialogOpen, closeImageDialog } = useImage();
    const [prompt, setPrompt] = useState("");
    const [showPromptContainer, setShowPromptContainer] = useState(false);
    const [isEditing, setIsEditing] = useState(false);

    const handleSendMessage = async (prompt: string) => {
        if (!prompt.trim()) {
            toaster.create({
                description: "Please enter a prompt",
                type: "warning",
            });
            return;
        }

        if (!selectedImage?.id) {
            toaster.create({
                description: "Missing image ID",
                type: "error",
            });
            return;
        }

        try {
            setIsEditing(true);
            
            const response = await fetch(`${BASE_URL}/api/image/generate?
                prompt=${encodeURIComponent(prompt)}
                &image_id=${selectedImage.id}`, 
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error(`Failed to edit image: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success) {
                toaster.create({
                    description: "Image edited successfully! Refreshing...",
                    type: "success",
                });
                
                // Close the prompt container and reset
                setShowPromptContainer(false);
                setPrompt("");
                
                setTimeout(() => {
                    closeImageDialog();
                }, 1500);
            } else {
                toaster.create({
                    description: result.message || "Failed to edit image",
                    type: "error",
                });
            }
        } catch (error) {
            console.error("Error editing image:", error);
            toaster.create({
                description: error instanceof Error ? error.message : "Failed to edit image",
                type: "error",
            });
        } finally {
            setIsEditing(false);
        }
    };

    return (
        <Dialog.Root 
            open={isDialogOpen} 
            onOpenChange={(e) => {
                if (!e.open) {
                    closeImageDialog();
                }
            }}
            size="xl"
            placement="center"
        >
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content maxW="5xl">
                        <Dialog.Header>
                            <Dialog.Title>
                                {selectedImage?.title || selectedImage?.filename || "Image Details"}
                            </Dialog.Title>
                        </Dialog.Header>

                        <Dialog.Body>
                            <VStack align="stretch" gap={4}>
                                {selectedImage?.url ? (
                                    <Box position="relative">
                                        {/* Buttons Container */}
                                        <VStack 
                                            position="absolute"
                                            left="0"
                                            top="50%"
                                            transform="translateY(-50%)"
                                            zIndex={10}
                                            gap={2} 
                                            p={2}
                                            borderWidth="1px"
                                            borderColor="gray.800"
                                            borderRadius="lg"
                                            padding={4}
                                            justifyContent="flex-start"
                                            bg="rgba(255, 255, 255, 0.05)"
                                            backdropFilter="blur(8px)"
                                            boxShadow="lg"
                                            minH="calc(600px - 40px)"
                                        >
                                            <Tooltip content="Edit image">
                                                <IconButton
                                                    aria-label="Edit image"
                                                    size="lg"
                                                    variant="ghost"
                                                    padding={4}
                                                    _hover={{ 
                                                        transform: "scale(1.1)",
                                                        bgColor: "teal.500", 
                                                    }}
                                                    onClick={() => setShowPromptContainer(!showPromptContainer)}
                                                >
                                                    <FaMagic />
                                                </IconButton>
                                            </Tooltip>
                                            
                                        </VStack>

                                        {/* Image Container */}
                                        <Box
                                            display="flex"
                                            justifyContent="center"
                                            alignItems="center"
                                            borderWidth="1px"
                                            borderColor="gray.800"
                                            borderRadius="lg"
                                            maxH="600px"
                                            overflow="hidden"
                                            marginLeft="40px"
                                        >
                                            <Image
                                                src={selectedImage.url}
                                                alt={
                                                    selectedImage.title ||
                                                    selectedImage.filename ||
                                                    selectedImage.description ||
                                                    "image"
                                                }
                                                maxW="100%"
                                                maxH="600px"
                                                objectFit="contain"
                                            />
                                        </Box>

                                        {/* Prompt Container */}
                                        {showPromptContainer && (
                                            <Box
                                                display="flex"
                                                flexDirection="row"
                                                alignItems="center"
                                                justifyContent="space-between"
                                                gap={4}
                                                zIndex={10}
                                                position="absolute"
                                                bottom="-40px"
                                                left="15%"
                                                paddingX={6}
                                                minW="700px"
                                                minH="100px"
                                                bg="rgba(0, 0, 0, 0.25)"
                                                backdropFilter="blur(8px)"
                                                boxShadow="lg"
                                                borderWidth="1px"
                                                borderColor="gray.800"
                                                borderRadius="lg"
                                            >

                                                <Textarea
                                                    outline="none"
                                                    border="none"
                                                    placeholder="Describe what you want to change about the image"
                                                    value={prompt}
                                                    onChange={(e) => {
                                                        setPrompt(e.target.value);
                                                    }}
                                                    disabled={isEditing}
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
                                                    onClick={() => handleSendMessage(prompt)}
                                                    disabled={isEditing}
                                                    loading={isEditing}
                                                >
                                                    <FaPaperPlane size="3rem" />
                                                </Button>
                                            </Box>
                                        )}
                                    </Box>
                                ) : (
                                    <Center
                                        width="100%"
                                        height="400px"
                                        bg="gray.100"
                                        borderRadius="md"
                                    >
                                        <Text color="gray.500">
                                            Image not available
                                        </Text>
                                    </Center>
                                )}

                                {/* Image Metadata */}
                                <Box p={4} bg="bg.subtle" borderRadius="md">
                                    <VStack align="stretch" gap={3}>
                                        {selectedImage?.description && (
                                            <Box>
                                                <Text fontWeight="bold" fontSize="sm" mb={1}>
                                                    Description:
                                                </Text>
                                                <Text fontSize="sm" color="gray.600">
                                                    {selectedImage.description}
                                                </Text>
                                            </Box>
                                        )}
                                        
                                        <Box>
                                            <Text fontWeight="bold" fontSize="sm" mb={1}>
                                                Filename:
                                            </Text>
                                            <Text fontSize="sm" color="gray.600">
                                                {selectedImage?.filename || "N/A"}
                                            </Text>
                                        </Box>

                                        <Box>
                                            <Text fontWeight="bold" fontSize="sm" mb={1}>
                                                Created:
                                            </Text>
                                            <Text fontSize="sm" color="gray.600">
                                                {selectedImage?.uploaded_at 
                                                    ? new Date(selectedImage.uploaded_at).toLocaleString()
                                                    : "N/A"
                                                }
                                            </Text>
                                        </Box>

                                        <Box>
                                            <Text fontWeight="bold" fontSize="sm" mb={1}>
                                                Image ID:
                                            </Text>
                                            <Text fontSize="sm" color="gray.600" fontFamily="monospace">
                                                {selectedImage?.id}
                                            </Text>
                                        </Box>
                                    </VStack>
                                </Box>
                            </VStack>
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

export default ImageDetailDialog;

