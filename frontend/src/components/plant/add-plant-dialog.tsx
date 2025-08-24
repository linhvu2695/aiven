import {
    Box,
    Button,
    Dialog,
    Portal,
    VStack,
    HStack,
    Input,
    Textarea,
    Select,
    Image,
    Text,
    CloseButton,
    createListCollection,
} from "@chakra-ui/react";
import { useState, useRef } from "react";
import { FaUpload, FaMagic, FaPlus } from "react-icons/fa";
import { BASE_URL } from "@/App";
import { toaster } from "../ui/toaster";

// Plant species options based on the backend enum
const PLANT_SPECIES = [
    { value: "succulent", label: "Succulent" },
    { value: "tropical", label: "Tropical" },
    { value: "flowering", label: "Flowering" },
    { value: "herb", label: "Herb" },
    { value: "fern", label: "Fern" },
    { value: "tree", label: "Tree" },
    { value: "vegetable", label: "Vegetable" },
    { value: "fruit", label: "Fruit" },
    { value: "cactus", label: "Cactus" },
    { value: "orchid", label: "Orchid" },
    { value: "other", label: "Other" },
];

interface PlantFormData {
    name: string;
    species: string;
    species_details: string;
    description: string;
    location: string;
    watering_frequency_days: string;
    light_requirements: string;
    humidity_preference: string;
    temperature_range: string;
}

interface AddPlantDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onPlantAdded?: () => void;
}

export const AddPlantDialog = ({ isOpen, onClose, onPlantAdded }: AddPlantDialogProps) => {
    const [formData, setFormData] = useState<PlantFormData>({
        name: "",
        species: "",
        species_details: "",
        description: "",
        location: "",
        watering_frequency_days: "",
        light_requirements: "",
        humidity_preference: "",
        temperature_range: "",
    });

    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleInputChange = (field: keyof PlantFormData, value: string) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
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

    const handleAIAnalysis = async () => {
        if (!selectedImage) return;

        setIsAnalyzing(true);
        try {
            // First create a temporary plant to get an ID for the photo
            const tempPlantResponse = await fetch(`${BASE_URL}/api/plant/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name: "Temporary Plant for Analysis",
                    species: "other",
                }),
            });

            if (!tempPlantResponse.ok) {
                throw new Error("Failed to create temporary plant");
            }

            const tempPlantData = await tempPlantResponse.json();
            const tempPlantId = tempPlantData.id;

            // Upload the image to the temporary plant
            const formData = new FormData();
            formData.append("file", selectedImage);
            formData.append("title", "Plant analysis photo");

            const photoResponse = await fetch(`${BASE_URL}/api/plant/${tempPlantId}/photo`, {
                method: "POST",
                body: formData,
            });

            if (!photoResponse.ok) {
                throw new Error("Failed to upload photo");
            }

            // Analyze the plant health (this will return mock data for now)
            const analysisResponse = await fetch(`${BASE_URL}/api/plant/${tempPlantId}/analyze`, {
                method: "POST",
            });

            if (!analysisResponse.ok) {
                throw new Error("Failed to analyze plant");
            }

            await analysisResponse.json();

            // Mock AI analysis results based on the response
            setFormData(prev => ({
                ...prev,
                name: "Beautiful Plant",
                species: "succulent",
                species_details: "Echeveria elegans",
                description: "A healthy-looking succulent with thick, fleshy leaves arranged in a rosette pattern.",
                light_requirements: "bright indirect",
                humidity_preference: "low",
                temperature_range: "65-75°F",
                watering_frequency_days: "7"
            }));

            // Clean up temporary plant
            // Note: We'll need to implement delete endpoint later
            console.log("Analysis completed, temp plant ID:", tempPlantId);
            
        } catch (error) {
            console.error("AI analysis failed:", error);
            toaster.create({
                description: "AI analysis failed. Please try again.",
                type: "error",
            });
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleSubmit = async () => {
        if (!formData.name.trim() || !formData.species) {
            toaster.create({
                description: "Please fill in at least the plant name and species.",
                type: "error",
            });
            return;
        }

        setIsSubmitting(true);
        try {
            // Create plant
            const plantData = {
                name: formData.name,
                species: formData.species,
                species_details: formData.species_details || undefined,
                description: formData.description || undefined,
                location: formData.location || undefined,
                watering_frequency_days: formData.watering_frequency_days ? parseInt(formData.watering_frequency_days) : undefined,
                light_requirements: formData.light_requirements || undefined,
                humidity_preference: formData.humidity_preference || undefined,
                temperature_range: formData.temperature_range || undefined,
            };

            const plantResponse = await fetch(`${BASE_URL}/api/plant/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(plantData),
            });

            if (!plantResponse.ok) {
                throw new Error("Failed to create plant");
            }

            const plantResult = await plantResponse.json();
            
            // Upload image if provided
            if (selectedImage && plantResult.id) {
                const formData = new FormData();
                formData.append("file", selectedImage);
                formData.append("title", "Initial plant photo");
                formData.append("description", "First photo of the plant");

                const photoResponse = await fetch(`${BASE_URL}/api/plant/${plantResult.id}/photo`, {
                    method: "POST",
                    body: formData,
                });

                if (!photoResponse.ok) {
                    console.warn("Plant created but photo upload failed");
                }
            }

            toaster.create({
                description: "Plant added successfully!",
                type: "success",
            });
            
            // Reset form and close dialog
            handleReset();
            onClose();
            if (onPlantAdded) onPlantAdded();
            
        } catch (error) {
            console.error("Failed to create plant:", error);
            toaster.create({
                description: "Failed to create plant. Please try again.",
                type: "error",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleReset = () => {
        setFormData({
            name: "",
            species: "",
            species_details: "",
            description: "",
            location: "",
            watering_frequency_days: "",
            light_requirements: "",
            humidity_preference: "",
            temperature_range: "",
        });
        setSelectedImage(null);
        setImagePreview(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    const handleClose = () => {
        handleReset();
        onClose();
    };

    return (
        <Dialog.Root
            open={isOpen}
            onOpenChange={(e) => {
                if (!e.open) handleClose();
            }}
            size="xl"
            placement="center"
        >
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content maxW="2xl">
                        <Dialog.Header>
                            <Dialog.Title>Add New Plant</Dialog.Title>
                        </Dialog.Header>

                        <Dialog.Body>
                            <VStack gap={4} align="stretch">
                                {/* Image Upload Section */}
                                <Box>
                                    <Text fontSize="sm" fontWeight="medium" mb={2}>Plant Photo</Text>
                                    <VStack gap={3}>
                                        {imagePreview ? (
                                            <Box position="relative">
                                                <Image
                                                    src={imagePreview}
                                                    alt="Plant preview"
                                                    maxH="200px"
                                                    objectFit="cover"
                                                    borderRadius="md"
                                                />
                                                <Button
                                                    size="sm"
                                                    position="absolute"
                                                    top={2}
                                                    right={2}
                                                    onClick={() => {
                                                        setSelectedImage(null);
                                                        setImagePreview(null);
                                                        if (fileInputRef.current) {
                                                            fileInputRef.current.value = "";
                                                        }
                                                    }}
                                                >
                                                    Remove
                                                </Button>
                                            </Box>
                                        ) : (
                                            <Box
                                                border="2px dashed"
                                                borderColor="gray.300"
                                                borderRadius="md"
                                                p={8}
                                                textAlign="center"
                                                cursor="pointer"
                                                onClick={() => fileInputRef.current?.click()}
                                                _hover={{ borderColor: "green.400" }}
                                            >
                                                <VStack gap={2}>
                                                    <FaUpload size={24} />
                                                    <Text>Click to upload plant photo</Text>
                                                    <Text fontSize="sm" color="gray.500">
                                                        JPG, PNG up to 10MB
                                                    </Text>
                                                </VStack>
                                            </Box>
                                        )}
                                        
                                        <input
                                            ref={fileInputRef}
                                            type="file"
                                            accept="image/*"
                                            onChange={handleImageUpload}
                                            style={{ display: "none" }}
                                        />
                                        
                                        {selectedImage && (
                                                                                    <Button
                                            colorScheme="purple"
                                            onClick={handleAIAnalysis}
                                            loading={isAnalyzing}
                                        >
                                            <FaMagic /> AI Auto-Fill from Photo
                                        </Button>
                                        )}
                                    </VStack>
                                </Box>

                                {/* Basic Information */}
                                <HStack gap={4}>
                                    <Box flex={1}>
                                        <Text fontSize="sm" fontWeight="medium" mb={2}>Plant Name *</Text>
                                        <Input
                                            value={formData.name}
                                            onChange={(e) => handleInputChange("name", e.target.value)}
                                            placeholder="e.g., My Fiddle Leaf Fig"
                                        />
                                    </Box>
                                    <Box flex={1}>
                                        <Text fontSize="sm" fontWeight="medium" mb={2}>Species *</Text>
                                        <Select.Root
                                            value={formData.species ? [formData.species] : []}
                                            onValueChange={(e) => handleInputChange("species", e.value[0] || "")}
                                            collection={createListCollection({
                                                items: PLANT_SPECIES,
                                            })}
                                        >
                                            <Select.Trigger>
                                                <Select.ValueText placeholder="Select species" />
                                            </Select.Trigger>
                                            <Select.Content>
                                                {PLANT_SPECIES.map((species) => (
                                                    <Select.Item key={species.value} item={species.value}>
                                                        {species.label}
                                                    </Select.Item>
                                                ))}
                                            </Select.Content>
                                        </Select.Root>
                                    </Box>
                                </HStack>

                                <Box>
                                    <Text fontSize="sm" fontWeight="medium" mb={2}>Species Details</Text>
                                    <Input
                                        value={formData.species_details}
                                        onChange={(e) => handleInputChange("species_details", e.target.value)}
                                        placeholder="e.g., Ficus lyrata, Monstera deliciosa"
                                    />
                                </Box>

                                <Box>
                                    <Text fontSize="sm" fontWeight="medium" mb={2}>Description</Text>
                                    <Textarea
                                        value={formData.description}
                                        onChange={(e) => handleInputChange("description", e.target.value)}
                                        placeholder="Describe your plant..."
                                        rows={3}
                                    />
                                </Box>

                                <Box>
                                    <Text fontSize="sm" fontWeight="medium" mb={2}>Location</Text>
                                    <Input
                                        value={formData.location}
                                        onChange={(e) => handleInputChange("location", e.target.value)}
                                        placeholder="e.g., Living room window, Bedroom, Balcony"
                                    />
                                </Box>

                                {/* Care Information */}
                                <HStack gap={4}>
                                    <Box flex={1}>
                                        <Text fontSize="sm" fontWeight="medium" mb={2}>Watering Frequency (days)</Text>
                                        <Input
                                            type="number"
                                            value={formData.watering_frequency_days}
                                            onChange={(e) => handleInputChange("watering_frequency_days", e.target.value)}
                                            placeholder="7"
                                        />
                                    </Box>
                                    <Box flex={1}>
                                        <Text fontSize="sm" fontWeight="medium" mb={2}>Light Requirements</Text>
                                        <Select.Root
                                            value={formData.light_requirements ? [formData.light_requirements] : []}
                                            onValueChange={(e) => handleInputChange("light_requirements", e.value[0] || "")}
                                            collection={createListCollection({
                                                items: [
                                                    { value: "low", label: "Low Light" },
                                                    { value: "medium", label: "Medium Light" },
                                                    { value: "high", label: "High Light" },
                                                    { value: "bright indirect", label: "Bright Indirect" },
                                                ],
                                            })}
                                        >
                                            <Select.Trigger>
                                                <Select.ValueText placeholder="Select light needs" />
                                            </Select.Trigger>
                                            <Select.Content>
                                                <Select.Item item="low">Low Light</Select.Item>
                                                <Select.Item item="medium">Medium Light</Select.Item>
                                                <Select.Item item="high">High Light</Select.Item>
                                                <Select.Item item="bright indirect">Bright Indirect</Select.Item>
                                            </Select.Content>
                                        </Select.Root>
                                    </Box>
                                </HStack>

                                <HStack gap={4}>
                                    <Box flex={1}>
                                        <Text fontSize="sm" fontWeight="medium" mb={2}>Humidity Preference</Text>
                                        <Select.Root
                                            value={formData.humidity_preference ? [formData.humidity_preference] : []}
                                            onValueChange={(e) => handleInputChange("humidity_preference", e.value[0] || "")}
                                            collection={createListCollection({
                                                items: [
                                                    { value: "low", label: "Low" },
                                                    { value: "medium", label: "Medium" },
                                                    { value: "high", label: "High" },
                                                ],
                                            })}
                                        >
                                            <Select.Trigger>
                                                <Select.ValueText placeholder="Select humidity" />
                                            </Select.Trigger>
                                            <Select.Content>
                                                <Select.Item item="low">Low</Select.Item>
                                                <Select.Item item="medium">Medium</Select.Item>
                                                <Select.Item item="high">High</Select.Item>
                                            </Select.Content>
                                        </Select.Root>
                                    </Box>
                                    <Box flex={1}>
                                        <Text fontSize="sm" fontWeight="medium" mb={2}>Temperature Range</Text>
                                        <Input
                                            value={formData.temperature_range}
                                            onChange={(e) => handleInputChange("temperature_range", e.target.value)}
                                            placeholder="e.g., 65-75°F"
                                        />
                                    </Box>
                                </HStack>
                            </VStack>
                        </Dialog.Body>

                        <Dialog.Footer>
                            <Button variant="outline" onClick={handleClose}>
                                Cancel
                            </Button>
                            <Button
                                colorScheme="green"
                                onClick={handleSubmit}
                                loading={isSubmitting}
                            >
                                <FaPlus /> Add Plant
                            </Button>
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

export default AddPlantDialog;
