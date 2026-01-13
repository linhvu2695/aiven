import {
    Box,
    Button,
    Dialog,
    Portal,
    VStack,
    HStack,
    Textarea,
    Image,
    Text,
    CloseButton,
    Input,
} from "@chakra-ui/react";
import { useState, useRef } from "react";
import { FaUpload, FaCloudUploadAlt } from "react-icons/fa";
import { BASE_URL } from "@/App";
import { toaster } from "../ui/toaster";
import { DeleteItemButton } from "../ui";
import { useColorMode } from "@/components/ui/color-mode";

interface ImageUploadDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}

export const ImageUploadDialog = ({ isOpen, onClose, onSuccess }: ImageUploadDialogProps) => {
    const { colorMode } = useColorMode();
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [isUploading, setIsUploading] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setSelectedImage(file);
            
            // Create preview URL
            const reader = new FileReader();
            reader.onload = (e) => {
                setImagePreview(e.target?.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleUpload = async () => {
        if (!selectedImage) {
            toaster.create({
                description: "Please select an image to upload",
                type: "warning",
            });
            return;
        }

        setIsUploading(true);
        try {
            const formData = new FormData();
            formData.append("file", selectedImage);
            if (title.trim()) {
                formData.append("title", title.trim());
            }
            if (description.trim()) {
                formData.append("description", description.trim());
            }

            const response = await fetch(`${BASE_URL}/api/image/upload`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "Failed to upload image");
            }

            const result = await response.json();

            if (result.success) {
                toaster.create({
                    description: "Image uploaded successfully!",
                    type: "success",
                });
                
                handleReset();
                onClose();
                
                if (onSuccess) {
                    onSuccess();
                }
            } else {
                throw new Error(result.message || "Failed to upload image");
            }
        } catch (error) {
            console.error("Failed to upload image:", error);
            toaster.create({
                description: error instanceof Error ? error.message : "Failed to upload image",
                type: "error",
            });
        } finally {
            setIsUploading(false);
        }
    };

    const handleReset = () => {
        setSelectedImage(null);
        setImagePreview(null);
        setTitle("");
        setDescription("");
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    const handleClose = () => {
        if (!isUploading) {
            handleReset();
            onClose();
        }
    };

    return (
        <Dialog.Root
            open={isOpen}
            onOpenChange={(e) => {
                if (!e.open) handleClose();
            }}
            placement="center"
            size="lg"
        >
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content 
                        maxW="600px" 
                        w="90vw"
                        bg={colorMode === "dark" ? "rgba(0, 0, 0, 0.90)" : "rgba(255, 255, 255, 0.95)"}
                        backdropFilter="blur(8px)"
                    >
                        <Dialog.Header>
                            <Dialog.Title>Upload Image</Dialog.Title>
                        </Dialog.Header>

                        <Dialog.Body>
                            <VStack gap={4} align="stretch">
                                {/* Image Preview / Upload Area */}
                                {imagePreview ? (
                                    <Box position="relative">
                                        <Image
                                            src={imagePreview}
                                            alt="Upload preview"
                                            w="100%"
                                            maxH="300px"
                                            objectFit="contain"
                                            borderRadius="lg"
                                            border="1px solid"
                                            borderColor="gray.200"
                                        />
                                        <DeleteItemButton
                                            aria-label="Remove image"
                                            onClick={() => {
                                                setSelectedImage(null);
                                                setImagePreview(null);
                                                if (fileInputRef.current) {
                                                    fileInputRef.current.value = "";
                                                }
                                            }}
                                        />
                                    </Box>
                                ) : (
                                    <Box
                                        border="2px dashed"
                                        borderColor="gray.400"
                                        borderRadius="lg"
                                        p={12}
                                        textAlign="center"
                                        cursor="pointer"
                                        onClick={() => fileInputRef.current?.click()}
                                        _hover={{ 
                                            bg: colorMode === "dark" ? "whiteAlpha.100" : "blackAlpha.50",
                                            borderColor: "teal.400"
                                        }}
                                        transition="all 0.2s"
                                        minH="200px"
                                        display="flex"
                                        alignItems="center"
                                        justifyContent="center"
                                    >
                                        <VStack gap={4}>
                                            <FaUpload size={48} color="var(--chakra-colors-gray-400)" />
                                            <Text fontSize="lg" fontWeight="medium">
                                                Click to select image
                                            </Text>
                                            <Text fontSize="md" color="gray.500">
                                                JPG, PNG, GIF, WebP up to 10MB
                                            </Text>
                                        </VStack>
                                    </Box>
                                )}
                                
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    onChange={handleImageSelect}
                                    style={{ display: "none" }}
                                />

                                {/* Title Input */}
                                <Box>
                                    <Text fontSize="sm" fontWeight="medium" mb={2}>
                                        Title (optional)
                                    </Text>
                                    <Input
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        placeholder="Give your image a title"
                                        disabled={isUploading}
                                    />
                                </Box>
                                
                                {/* Description Input */}
                                <Box>
                                    <Text fontSize="sm" fontWeight="medium" mb={2}>
                                        Description (optional)
                                    </Text>
                                    <Textarea
                                        value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        placeholder="Add a description..."
                                        rows={3}
                                        disabled={isUploading}
                                    />
                                </Box>
                            </VStack>
                        </Dialog.Body>

                        <Dialog.Footer>
                            <HStack gap={3}>
                                <Button 
                                    variant="outline" 
                                    onClick={handleClose}
                                    disabled={isUploading}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    colorScheme="teal"
                                    onClick={handleUpload}
                                    loading={isUploading}
                                    disabled={isUploading || !selectedImage}
                                    _hover={{
                                        transform: "scale(1.02)",
                                        bgColor: "teal.500",
                                    }}
                                >
                                    <FaCloudUploadAlt /> Upload
                                </Button>
                            </HStack>
                        </Dialog.Footer>

                        <Dialog.CloseTrigger asChild>
                            <CloseButton size="sm" />
                        </Dialog.CloseTrigger>
                    </Dialog.Content>
                </Dialog.Positioner>
            </Portal>
        </Dialog.Root>
    );
};

export default ImageUploadDialog;
