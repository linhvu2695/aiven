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
} from "@chakra-ui/react";
import { FaMagic } from "react-icons/fa";
import { useImage } from "@/context/image-ctx";
import { Tooltip } from "../ui/tooltip";
import { useState } from "react";
import { ImageGenDialog } from "./image-gen-dialog";

export const ImageDetailDialog = () => {
    const { selectedImage, isDialogOpen, closeImageDialog, refreshImages } = useImage();
    const [isImageGenDialogOpen, setIsImageGenDialogOpen] = useState(false);

    const handleEditImage = () => {
        setIsImageGenDialogOpen(true);
    };

    const handleImageGenSuccess = () => {
        // Close both dialogs and refresh the image list
        setIsImageGenDialogOpen(false);
        closeImageDialog();
        refreshImages();
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
                                                        bgColor: "primary.500", 
                                                    }}
                                                    onClick={handleEditImage}
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
            
            {/* Image Generation Dialog */}
            <ImageGenDialog 
                isOpen={isImageGenDialogOpen}
                onClose={() => setIsImageGenDialogOpen(false)}
                onSuccess={handleImageGenSuccess}
            />
        </Dialog.Root>
    );
};

export default ImageDetailDialog;

