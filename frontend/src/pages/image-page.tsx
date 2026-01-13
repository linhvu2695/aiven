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
    IconButton
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { toaster } from "@/components/ui/toaster";
import type {
    ImageListResponse,
    ImageUrlsResponse,
} from "@/types/image";
import { ImageCard, ImageDetailDialog, ImageViewDialog, ImageGenDialog } from "@/components/image";
import { useImage } from "@/context/image-ctx";
import type { ImageWithUrl } from "@/types/image";
import { useImageView } from "@/context/image-view-ctx";
import { FaArrowLeft, FaArrowRight, FaListUl, FaMagic, FaUpload } from "react-icons/fa";
import { Tooltip } from "@/components/ui";
import { ImageUploadDialog } from "@/components/image";

export const ImagePage = () => {
    const [images, setImages] = useState<ImageWithUrl[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [totalImages, setTotalImages] = useState(0);
    const { openImageDialog, isGenDialogOpen, setIsGenDialogOpen, registerRefreshCallback } = useImage();
    const { pageSize, openViewDialog, getViewRatioSize } = useImageView();
    const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);

    const fetchImages = async (page: number = currentPage) => {
        try {
            setLoading(true);
            const response = await fetch(BASE_URL + "/api/image/list", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    page: page,
                    page_size: pageSize,
                    image_type: "general",
                    include_deleted: false,
                }),
            });

            if (!response.ok) throw new Error("Failed to fetch images");

            const data: ImageListResponse = await response.json();
            
            setTotalImages(data.total);
            setCurrentPage(data.page);

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

    // Register the refresh callback with the context
    useEffect(() => {
        registerRefreshCallback(() => fetchImages(currentPage));
    }, [currentPage, pageSize, registerRefreshCallback]);

    useEffect(() => {
        fetchImages(currentPage);
    }, [currentPage, pageSize]);

    const totalPages = Math.ceil(totalImages / pageSize);

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
                    Images
                </Text>

                {/* Search */}
                <Input
                    borderRadius={18}
                    width={"40vh"}
                    placeholder="Search images"
                    value={searchQuery}
                    onChange={(e) => {
                        setSearchQuery(e.target.value);
                    }}
                />

                {/* Upload Image */}
                <Tooltip content="Upload Image">
                    <IconButton
                        aria-label="Upload Image"
                        size="md"
                        variant="ghost"
                        borderRadius={"full"}
                        onClick={() => setIsUploadDialogOpen(true)}
                    >
                        <FaUpload />
                    </IconButton>
                </Tooltip>

                {/* Edit View */}
                <Tooltip content="Edit View">
                    <IconButton
                        aria-label="Edit View"
                        size="md"
                        variant="ghost"
                        borderRadius={"full"}
                        onClick={openViewDialog}
                    >
                        <FaListUl />
                    </IconButton>
                </Tooltip>

                {/* Generate Image */}
                <Tooltip content="Generate Image">
                    <IconButton
                        aria-label="Generate Image"
                        size="md"
                        variant="ghost"
                        borderRadius={"full"}
                        onClick={() => setIsGenDialogOpen(true)}
                    >
                        <FaMagic />
                    </IconButton>
                </Tooltip>
                
            </HStack>

            {/* Main Content */}
            <Flex h="calc(100vh - 150px)" p={4} direction="column">
                <Box flex={1} overflow="auto">
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
                            </VStack>
                        </Center>
                    ) : (
                        <Grid
                            templateColumns={`repeat(auto-fill, minmax(${getViewRatioSize()}px, 1fr))`}
                            gap={4}
                            p={4}
                        >
                            {images.map((image) => (
                                <ImageCard 
                                    key={image.id} 
                                    image={image}
                                    onClick={() => openImageDialog(image)}
                                    onDelete={() => fetchImages(currentPage)}
                                />
                            ))}
                        </Grid>
                    )}
                </Box>

                {/* Pagination Controls */}
                {!loading && totalImages > 0 && (
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
                                ({totalImages} images)
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

            <ImageDetailDialog />
            <ImageViewDialog />
            <ImageGenDialog 
                isOpen={isGenDialogOpen} 
                onClose={() => setIsGenDialogOpen(false)}
                onSuccess={() => fetchImages(currentPage)}
            />
            <ImageUploadDialog
                isOpen={isUploadDialogOpen}
                onClose={() => setIsUploadDialogOpen(false)}
                onSuccess={() => fetchImages(currentPage)}
            />
        </Box>
    );
};

export default ImagePage;
