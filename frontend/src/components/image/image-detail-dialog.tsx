import {
    Box,
    VStack,
    Text,
    Center,
    Dialog,
    Portal,
    CloseButton,
    Image,
} from "@chakra-ui/react";
import { useImage } from "@/context/image-ctx";

export const ImageDetailDialog = () => {
    const { selectedImage, isDialogOpen, closeImageDialog } = useImage();

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
                                    <Box
                                        display="flex"
                                        justifyContent="center"
                                        alignItems="center"
                                        maxH="600px"
                                        overflow="hidden"
                                        borderRadius="md"
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

