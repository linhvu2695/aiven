import {
    Box,
    VStack,
    Card,
    Text,
    Center,
    Image,
    useDisclosure,
} from "@chakra-ui/react";
import type { ImageInfo } from "@/types/image";
import { DeleteItemButton } from "@/components/ui";
import { ImageDeleteDialog } from "./image-delete-dialog";
import { useImageView, ViewMode } from "@/context/image-view-ctx";

interface ImageWithUrl extends ImageInfo {
    url?: string;
}

interface ImageCardProps {
    image: ImageWithUrl;
    onClick?: () => void;
    onDelete?: () => void;
}

export const ImageCard = ({ image, onClick, onDelete }: ImageCardProps) => {
    const { open, onOpen, onClose } = useDisclosure();
    const { viewMode } = useImageView();

    return (
        <>
            <Card.Root 
                key={image.id} 
                overflow="hidden"
                cursor="pointer"
                position="relative"
                onClick={onClick}
                _hover={{
                    transform: "scale(1.02)",
                    transition: "transform 0.2s",
                    boxShadow: "lg",
                }}
            >
                {/* Delete button */}
                <DeleteItemButton
                    aria-label="Delete image"
                    onClick={(e) => {
                        e?.stopPropagation();
                        onOpen();
                    }}
                />

                <VStack align="stretch" gap={0}>
                {image.url ? (
                    <Image
                        src={image.url}
                        alt={
                            image.title ||
                            image.filename ||
                            image.description ||
                            "image"
                        }
                        width="100%"
                        height="300px"
                        objectFit="cover"
                        loading="lazy"
                    />
                ) : (
                    <Center
                        width="100%"
                        height="300px"
                        bg="gray.100"
                    >
                        <Text color="gray.500">
                            Image not available
                        </Text>
                    </Center>
                )}

                {/* Image Metadata - Show based on view mode */}
                {viewMode === ViewMode.DETAIL && (
                    <Box p={4}>
                        <VStack align="stretch" gap={2}>
                            <Text
                                fontWeight="bold"
                                fontSize="sm"
                                overflow="hidden"
                                textOverflow="ellipsis"
                                whiteSpace="nowrap"
                                title={image.title || image.filename || image.id}
                            >
                                {image.title || image.filename || image.id}
                            </Text>
                            {image.description && (
                                <Text
                                    fontSize="sm"
                                    color="gray.600"
                                    overflow="hidden"
                                    textOverflow="ellipsis"
                                    whiteSpace="nowrap"
                                    title={image.description}
                                >
                                    {image.description}
                                </Text>
                            )}
                            <Text
                                fontSize="xs"
                                color="gray.400"
                            >
                                Created:{" "}
                                {new Date(
                                    image.uploaded_at
                                ).toLocaleDateString()}
                            </Text>
                        </VStack>
                    </Box>
                )}
            </VStack>
        </Card.Root>

        <ImageDeleteDialog
            isOpen={open}
            onClose={onClose}
            imageId={image.id}
            imageName={image.title || image.filename}
            onDelete={onDelete}
        />
    </>
    );
};

