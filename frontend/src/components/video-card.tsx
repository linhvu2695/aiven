import {
    Box,
    Card,
    IconButton,
    Image,
    Text,
    VStack,
    useDisclosure,
} from "@chakra-ui/react";
import { useRef, useState } from "react";
import { FaPlay, FaPause } from "react-icons/fa";
import type { VideoWithUrl } from "@/types/video";
import { DeleteItemButton, DetailItemButton } from "@/components/ui";
import { VideoDeleteDialog } from "./video-delete-dialog";

interface VideoCardProps {
    video: VideoWithUrl;
    onDetailClick?: () => void;
    onDelete?: () => void;
}

export const VideoCard = ({
    video,
    onDetailClick,
    onDelete,
}: VideoCardProps) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [isHovered, setIsHovered] = useState(false);
    const [showVideo, setShowVideo] = useState(false);
    const videoRef = useRef<HTMLVideoElement>(null);
    const { open, onOpen, onClose } = useDisclosure();

    const handlePlayClick = () => {
        setShowVideo(true);
        setIsPlaying(true);
    };

    const handleTogglePlayPause = () => {
        if (videoRef.current) {
            if (isPlaying) {
                videoRef.current.pause();
                setIsPlaying(false);
            } else {
                videoRef.current.play();
                setIsPlaying(true);
            }
        }
    };

    return (
        <>
            <Card.Root key={video.id} overflow="hidden" position="relative">
                {/* Delete button */}
                <DeleteItemButton
                    aria-label="Delete video"
                    onClick={(e) => {
                        e?.stopPropagation();
                        onOpen();
                    }}
                />

                <Card.Body p={0}>
                    {/* Video or Thumbnail */}
                    <Box
                        position="relative"
                        width="100%"
                        height="100%"
                        onMouseEnter={() => setIsHovered(true)}
                        onMouseLeave={() => setIsHovered(false)}
                    >
                        {showVideo && video.url ? (
                            <>
                                <video
                                    ref={videoRef}
                                    src={video.url}
                                    controls
                                    autoPlay
                                    style={{
                                        width: "100%",
                                        height: "100%",
                                        objectFit: "cover",
                                    }}
                                    onPlay={() => setIsPlaying(true)}
                                    onPause={() => setIsPlaying(false)}
                                />
                                {/* Play/Pause button overlay */}
                                <Box
                                    position="absolute"
                                    top={0}
                                    left={0}
                                    right={0}
                                    bottom={0}
                                    display="flex"
                                    alignItems="center"
                                    justifyContent="center"
                                    bg={
                                        isHovered
                                            ? "blackAlpha.400"
                                            : "transparent"
                                    }
                                    transition="background-color 0.2s"
                                    pointerEvents="none"
                                >
                                    <IconButton
                                        aria-label={
                                            isPlaying ? "Pause" : "Play"
                                        }
                                        size="xl"
                                        colorScheme="teal"
                                        rounded="full"
                                        onClick={handleTogglePlayPause}
                                        opacity={isHovered ? 1 : 0}
                                        transform={
                                            isHovered
                                                ? "scale(1.1)"
                                                : "scale(1)"
                                        }
                                        transition="all 0.2s"
                                        pointerEvents="auto"
                                        bg="rgb(255, 255, 255, 0.4)"
                                        backdropFilter="blur(8px)"
                                        _hover={{
                                            transform: "scale(1.2)",
                                        }}
                                    >
                                        {isPlaying ? <FaPause /> : <FaPlay />}
                                    </IconButton>
                                </Box>
                            </>
                        ) : (
                            <>
                                {/* Thumbnail */}
                                {video.thumbnail_url ? (
                                    <Image
                                        src={video.thumbnail_url}
                                        alt={
                                            video.title ||
                                            video.filename ||
                                            "Untitled"
                                        }
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
                                        <Text color="gray.500">
                                            No preview available
                                        </Text>
                                    </Box>
                                )}

                                {/* Play button overlay */}
                                {video.url && (
                                    <Box
                                        position="absolute"
                                        top={0}
                                        left={0}
                                        right={0}
                                        bottom={0}
                                        display="flex"
                                        alignItems="center"
                                        justifyContent="center"
                                        bg={
                                            isHovered
                                                ? "blackAlpha.400"
                                                : "transparent"
                                        }
                                        transition="background-color 0.2s"
                                    >
                                        <IconButton
                                            aria-label="Play video"
                                            size="xl"
                                            colorScheme="teal"
                                            rounded="full"
                                            onClick={handlePlayClick}
                                            opacity={isHovered ? 1 : 0.7}
                                            transform={
                                                isHovered
                                                    ? "scale(1.1)"
                                                    : "scale(1)"
                                            }
                                            transition="all 0.2s"
                                            _hover={{
                                                transform: "scale(1.2)",
                                            }}
                                        >
                                            <FaPlay />
                                        </IconButton>
                                    </Box>
                                )}
                            </>
                        )}
                    </Box>

                    {/* Details */}
                    <VStack
                        align="stretch"
                        p={3}
                        gap={1}
                        onClick={onDetailClick}
                        cursor="pointer"
                    >
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
                                    {new Date(
                                        video.uploaded_at
                                    ).toLocaleString()}
                                </Text>
                            )}
                        </VStack>
                    </VStack>
                </Card.Body>
            </Card.Root>

            <VideoDeleteDialog
                isOpen={open}
                onClose={onClose}
                videoId={video.id}
                videoName={video.title || video.filename}
                onDelete={onDelete}
            />
        </>
    );
};
