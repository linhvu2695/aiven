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
    Input,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { toaster } from "@/components/ui/toaster";
import type {
    ImageInfo,
    ImageListResponse,
    ImageUrlsResponse,
} from "@/types/image";
import { ImageCard } from "@/components/image";

interface ImageWithUrl extends ImageInfo {
    url?: string;
}

export const ImagePage = () => {
    const [images, setImages] = useState<ImageWithUrl[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");

    const fetchImages = async () => {
        try {
            setLoading(true);
            const response = await fetch(BASE_URL + "/api/image/list", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    limit: 100,
                    offset: 0,
                    image_type: "general",
                    include_deleted: false,
                }),
            });

            if (!response.ok) throw new Error("Failed to fetch images");

            const data: ImageListResponse = await response.json();

            // Fetch pre-signed URLs for all images
            if (data.images.length > 0) {
                const imageIds = data.images.map((img) => img.id).join(",");
                const urlsResponse = await fetch(
                    `${BASE_URL}/api/image/serve/ids/${imageIds}`
                );

                if (urlsResponse.ok) {
                    const urlsData: ImageUrlsResponse =
                        await urlsResponse.json();

                    // Merge URLs with image data
                    const imagesWithUrls = data.images.map((image) => {
                        const urlInfo = urlsData.results.find(
                            (result) => result.image_id === image.id
                        );
                        return {
                            ...image,
                            url: urlInfo?.url,
                        };
                    });

                    setImages(imagesWithUrls);
                } else {
                    // If URL fetching fails, still show images without URLs
                    setImages(data.images);
                }
            } else {
                setImages([]);
            }
        } catch (error) {
            console.error("Error fetching images:", error);
            toaster.create({
                description: "Failed to load images",
                type: "error",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchImages();
    }, []);

    return (
        <Box h="100vh" overflow="hidden">
            {/* Search */}
            <HStack as="header" gap={4}>
                <Input
                    borderRadius={18}
                    width={"40vh"}
                    placeholder="Search images"
                    value={searchQuery}
                    onChange={(e) => {
                        setSearchQuery(e.target.value);
                    }}
                />
            </HStack>

            {/* Main Content */}
            <Flex h="calc(100vh - 120px)" p={4}>
                <Box flex={1} h="100%" overflow="auto">
                    {loading ? (
                        <Center h="100%">
                            <Spinner size="xl" color="teal.500" />
                        </Center>
                    ) : images.length === 0 ? (
                        <Center h="100%">
                            <VStack gap={2}>
                                <Text fontSize="xl" color="gray.500">
                                    No images found
                                </Text>
                                <Text fontSize="sm" color="gray.400">
                                    Generated images will appear here
                                </Text>
                            </VStack>
                        </Center>
                    ) : (
                        <Grid
                            templateColumns="repeat(auto-fill, minmax(300px, 1fr))"
                            gap={4}
                            p={4}
                        >
                            {images.map((image) => (
                                <ImageCard key={image.id} image={image} />
                            ))}
                        </Grid>
                    )}
                </Box>
            </Flex>
        </Box>
    );
};

export default ImagePage;
