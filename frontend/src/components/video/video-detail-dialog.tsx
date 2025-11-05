import {
    Box,
    VStack,
    Text,
    Center,
    Dialog,
    Portal,
    CloseButton,
} from "@chakra-ui/react";
import { useVideo } from "@/context/video-ctx";

export const VideoDetailDialog = () => {
    const { selectedVideo, isDialogOpen, closeVideoDialog } = useVideo();

    return (
        <Dialog.Root 
            open={isDialogOpen} 
            onOpenChange={(e) => {
                if (!e.open) {
                    closeVideoDialog();
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
                                {selectedVideo?.title || selectedVideo?.filename || "Video Details"}
                            </Dialog.Title>
                        </Dialog.Header>

                        <Dialog.Body>
                            <VStack align="stretch" gap={4}>
                                {selectedVideo?.url ? (
                                    <Box
                                        display="flex"
                                        justifyContent="center"
                                        alignItems="center"
                                        borderWidth="1px"
                                        borderColor="gray.800"
                                        borderRadius="lg"
                                        maxH="600px"
                                        overflow="hidden"
                                    >
                                        <video
                                            src={selectedVideo.url}
                                            controls
                                            autoPlay
                                            style={{
                                                maxWidth: "100%",
                                                maxHeight: "600px",
                                                width: "100%",
                                                objectFit: "contain",
                                            }}
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
                                            Video not available
                                        </Text>
                                    </Center>
                                )}

                                {/* Video Metadata */}
                                <Box p={4} bg="bg.subtle" borderRadius="md">
                                    <VStack align="stretch" gap={3}>
                                        {selectedVideo?.description && (
                                            <Box>
                                                <Text fontWeight="bold" fontSize="sm" mb={1}>
                                                    Description:
                                                </Text>
                                                <Text fontSize="sm" color="gray.600">
                                                    {selectedVideo.description}
                                                </Text>
                                            </Box>
                                        )}
                                        
                                        <Box>
                                            <Text fontWeight="bold" fontSize="sm" mb={1}>
                                                Filename:
                                            </Text>
                                            <Text fontSize="sm" color="gray.600">
                                                {selectedVideo?.filename || "N/A"}
                                            </Text>
                                        </Box>

                                        {selectedVideo?.metadata && (
                                            <>
                                                {selectedVideo.metadata.duration && (
                                                    <Box>
                                                        <Text fontWeight="bold" fontSize="sm" mb={1}>
                                                            Duration:
                                                        </Text>
                                                        <Text fontSize="sm" color="gray.600">
                                                            {Math.floor(selectedVideo.metadata.duration / 60)}:
                                                            {String(Math.floor(selectedVideo.metadata.duration % 60)).padStart(2, '0')} minutes
                                                        </Text>
                                                    </Box>
                                                )}

                                                {selectedVideo.metadata.width && selectedVideo.metadata.height && (
                                                    <Box>
                                                        <Text fontWeight="bold" fontSize="sm" mb={1}>
                                                            Resolution:
                                                        </Text>
                                                        <Text fontSize="sm" color="gray.600">
                                                            {selectedVideo.metadata.width} × {selectedVideo.metadata.height}
                                                        </Text>
                                                    </Box>
                                                )}

                                                {selectedVideo.metadata.file_size && (
                                                    <Box>
                                                        <Text fontWeight="bold" fontSize="sm" mb={1}>
                                                            File Size:
                                                        </Text>
                                                        <Text fontSize="sm" color="gray.600">
                                                            {(selectedVideo.metadata.file_size / (1024 * 1024)).toFixed(2)} MB
                                                        </Text>
                                                    </Box>
                                                )}
                                            </>
                                        )}

                                        <Box>
                                            <Text fontWeight="bold" fontSize="sm" mb={1}>
                                                Uploaded:
                                            </Text>
                                            <Text fontSize="sm" color="gray.600">
                                                {selectedVideo?.uploaded_at 
                                                    ? new Date(selectedVideo.uploaded_at).toLocaleString()
                                                    : "N/A"
                                                }
                                            </Text>
                                        </Box>

                                        <Box>
                                            <Text fontWeight="bold" fontSize="sm" mb={1}>
                                                Video ID:
                                            </Text>
                                            <Text fontSize="sm" color="gray.600" fontFamily="monospace">
                                                {selectedVideo?.id}
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

export default VideoDetailDialog;

