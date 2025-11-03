import { Box, Card, Image, Text, VStack } from "@chakra-ui/react";
import type { VideoWithUrl } from "@/types/video";

interface VideoCardProps {
    video: VideoWithUrl;
    onClick?: () => void;
    onDelete?: () => void;
}

export const VideoCard = ({ video, onClick, onDelete }: VideoCardProps) => {
    return (
        <Card.Root key={video.id} overflow="hidden">
            <Card.Body p={0}>
                {/* Video */}
                {video.thumbnail_url ? (
                    <Image
                        src={video.thumbnail_url}
                        alt={video.title || video.filename || "Untitled"}
                        width="100%"
                        height="100%"
                        objectFit="cover"
                    />
                ) : (
                    <Box
                        width="100%"
                        height="100%"
                        bg="gray.200"
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                    >
                        <Text color="gray.500">No preview available</Text>
                    </Box>
                )}

                {/* Details */}
                <VStack align="stretch" p={3} gap={1}>
                    <Text fontWeight="semibold" fontSize="sm" lineClamp={1}>
                        {video.title || video.filename || "Untitled"}
                    </Text>
                    {video.description && (
                        <Text fontSize="xs" color="gray.600" lineClamp={2}>
                            {video.description}
                        </Text>
                    )}

                    {/* Metadata */}
                    <VStack fontSize="xs" color="gray.500" gap={3} mt={1}>
                        {video.uploaded_at && (
                            <Text>
                                Uploaded at{" "}
                                {new Date(video.uploaded_at).toLocaleString()}
                            </Text>
                        )}
                    </VStack>
                </VStack>
            </Card.Body>
        </Card.Root>
    );
};

