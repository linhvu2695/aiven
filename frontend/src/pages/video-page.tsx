import { BASE_URL } from "@/App";
import {
    Box,
    Flex,
    VStack,
    Grid,
    Text,
    Spinner,
    Center,
    HStack,
    IconButton,
    Card,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { toaster } from "@/components/ui/toaster";
import type {
    VideoListResponse,
    VideoUrlsResponse,
    VideoInfo,
} from "@/types/video";
import { FaArrowLeft, FaArrowRight } from "react-icons/fa";

interface VideoWithUrl extends VideoInfo {
    url?: string;
}

export const VideoPage = () => {
    const [videos, setVideos] = useState<VideoWithUrl[]>([]);
    const [loading, setLoading] = useState(true);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalVideos, setTotalVideos] = useState(0);
    const pageSize = 12;

    const fetchVideos = async (page: number = currentPage) => {
        try {
            setLoading(true);
            const response = await fetch(BASE_URL + "/api/video/list", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    page: page,
                    page_size: pageSize,
                    video_type: "general",
                    include_deleted: false,
                }),
            });

            if (!response.ok) throw new Error("Failed to fetch videos");

            const data: VideoListResponse = await response.json();

            setTotalVideos(data.total);
            setCurrentPage(data.page);

            // Fetch pre-signed URLs for all videos
            if (data.videos.length > 0) {
                const videoIds = data.videos.map((vid) => vid.id).join(",");
                const urlsResponse = await fetch(
                    `${BASE_URL}/api/video/serve/ids/${videoIds}`
                );

                if (urlsResponse.ok) {
                    const urlsData: VideoUrlsResponse =
                        await urlsResponse.json();

                    // Merge URLs with video data
                    const videosWithUrls = data.videos.map((video) => {
                        const urlInfo = urlsData.results.find(
                            (result) => result.video_id === video.id
                        );
                        return {
                            ...video,
                            url: urlInfo?.url,
                        };
                    });

                    setVideos(videosWithUrls);
                } else {
                    // If URL fetching fails, still show videos without URLs
                    setVideos(data.videos);
                }
            } else {
                setVideos([]);
            }
        } catch (error) {
            console.error("Error fetching videos:", error);
            toaster.create({
                description: "Failed to load videos",
                type: "error",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchVideos(currentPage);
    }, [currentPage]);

    const totalPages = Math.ceil(totalVideos / pageSize);

    const handlePreviousPage = () => {
        if (currentPage > 1) {
            setCurrentPage(currentPage - 1);
        }
    };

    const handleNextPage = () => {
        if (currentPage < totalPages) {
            setCurrentPage(currentPage + 1);
        }
    };

    return (
        <Box h="100vh" overflow="hidden">
            {/* Header */}
            <HStack as="header" gap={4} p={4}>
                <Text fontSize="2xl" fontWeight="bold">
                    Videos
                </Text>
            </HStack>

            {/* Main Content */}
            <Flex h="calc(100vh - 120px)" p={4} direction="column">
                <Box flex={1} overflow="auto">
                    {loading ? (
                        <Center h="100%">
                            <Spinner size="xl" color="teal.500" />
                        </Center>
                    ) : videos.length === 0 ? (
                        <Center h="100%">
                            <VStack gap={2}>
                                <Text fontSize="xl" color="gray.500">
                                    No videos found
                                </Text>
                            </VStack>
                        </Center>
                    ) : (
                        <Grid
                            templateColumns="repeat(auto-fill, minmax(200px, 1fr))"
                            gap={4}
                            p={4}
                        >
                            {videos.map((video) => (
                                <Card.Root key={video.id} overflow="hidden">
                                    <Card.Body p={0}>
                                        {/* Video */}
                                        {video.url ? (
                                            <Box
                                                width="100%"
                                                height="100%"
                                                bg="black"
                                            >
                                                <video
                                                    src={video.url}
                                                    controls
                                                    style={{
                                                        width: "100%",
                                                        height: "100%",
                                                        objectFit: "cover",
                                                    }}
                                                />
                                            </Box>
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

                                        {/* Details */}
                                        <VStack
                                            align="stretch"
                                            p={3}
                                            gap={1}
                                        >
                                            <Text
                                                fontWeight="semibold"
                                                fontSize="sm"
                                                lineClamp={1}
                                            >
                                                {video.title ||
                                                    video.filename ||
                                                    "Untitled"}
                                            </Text>
                                            {video.description && (
                                                <Text
                                                    fontSize="xs"
                                                    color="gray.600"
                                                    lineClamp={2}
                                                >
                                                    {video.description}
                                                </Text>
                                            )}

                                            {/* Metadata */}
                                            <VStack
                                                fontSize="xs"
                                                color="gray.500"
                                                gap={3}
                                                mt={1}
                                            >
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
                            ))}
                        </Grid>
                    )}
                </Box>

                {/* Pagination Controls */}
                {!loading && totalVideos > 0 && (
                    <HStack justify="center" p={4} gap={4}>
                        <IconButton
                            onClick={handlePreviousPage}
                            disabled={currentPage === 1}
                            variant="ghost"
                            aria-label="Previous page"
                        >
                            <FaArrowLeft />
                        </IconButton>
                        <HStack gap={2}>
                            <Text fontWeight="medium">
                                Page {currentPage} of {totalPages}
                            </Text>
                            <Text fontSize="sm" color="gray.500">
                                ({totalVideos} videos)
                            </Text>
                        </HStack>
                        <IconButton
                            onClick={handleNextPage}
                            disabled={currentPage >= totalPages}
                            variant="ghost"
                            aria-label="Next page"
                        >
                            <FaArrowRight />
                        </IconButton>
                    </HStack>
                )}
            </Flex>
        </Box>
    );
};

export default VideoPage;
