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
} from "@chakra-ui/react";
import { useState, useRef } from "react";
import { FaUpload, FaMagic, FaPlus } from "react-icons/fa";
import { BASE_URL } from "@/App";
import { toaster } from "../ui/toaster";
import { Dropdown, FormField, DeleteItemButton } from "../ui";

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
        species: "other",
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
            // Upload the image to the AutoFillPlantInfo API endpoint
            const formData = new FormData();
            formData.append("file", selectedImage);

            const response = await fetch(`${BASE_URL}/api/plant/autofill`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                toaster.create({
                    description: "AI analysis failed. Please try again.",
                    type: "error",
                });
                return;
            }

            const autofillData = await response.json();
            if (!autofillData.success || !autofillData.plant_info) {
                toaster.create({
                    description: "AI analysis failed. Please try again.",
                    type: "error",
                });
                return;
            }

            const plantInfo = autofillData.plant_info;

            // Update form data with AI-generated plant information
            setFormData(prev => ({
                ...prev,
                name: plantInfo.name || prev.name,
                species: plantInfo.species || prev.species,
                species_details: plantInfo.species_details || prev.species_details,
                description: plantInfo.description || prev.description,
                location: plantInfo.location || prev.location,
                light_requirements: plantInfo.light_requirements || prev.light_requirements,
                humidity_preference: plantInfo.humidity_preference || prev.humidity_preference,
                temperature_range: plantInfo.temperature_range || prev.temperature_range,
                watering_frequency_days: plantInfo.watering_frequency_days ? plantInfo.watering_frequency_days.toString() : prev.watering_frequency_days
            }));

            toaster.create({
                description: "AI plant info autofill completed",
                type: "success",
            });
            
        } catch (error) {
            console.error("AI plant info autofill failed:", error);
            toaster.create({
                description: "AI plant info autofill failed. Please try again.",
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
                toaster.create({
                    description: "Failed to create plant. Please try again.",
                    type: "error",
                });
                return;
            }

            const plantResult = await plantResponse.json();
            
            // Upload image if provided
            if (selectedImage && plantResult.id) {
                const formData = new FormData();
                formData.append("file", selectedImage);
                formData.append("title", `${plantResult.name} - ${new Date().toLocaleDateString()}`);

                const photoResponse = await fetch(`${BASE_URL}/api/plant/${plantResult.id}/photo`, {
                    method: "POST",
                    body: formData,
                });

                if (!photoResponse.ok) {
                    toaster.create({
                        description: "Plant created but photo upload failed. Please try again.",
                        type: "warning",
                    });
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
            species: "other",
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
            placement="center"
        >
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content maxW="1200px" w="90vw">
                        <Dialog.Header>
                            <Dialog.Title>Add New Plant</Dialog.Title>
                        </Dialog.Header>

                        <Dialog.Body>
                            <HStack gap={6} align="start" minH="500px">
                                {/* Left Column - Image Section */}
                                <Box flex={1} minW="400px" h="500px">
                                    <VStack gap={4} align="stretch" h="full">
                                        {imagePreview ? (
                                            <Box position="relative" flex={1}>
                                                <Image
                                                    src={imagePreview}
                                                    alt="Plant preview"
                                                    w="100%"
                                                    h="400px"
                                                    objectFit="cover"
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
                                                borderColor="gray.300"
                                                borderRadius="lg"
                                                p={12}
                                                textAlign="center"
                                                cursor="pointer"
                                                onClick={() => fileInputRef.current?.click()}
                                                _hover={{ bg: "teal.950" }}
                                                h="100%"
                                                display="flex"
                                                alignItems="center"
                                                justifyContent="center"
                                                flex={1}
                                            >
                                                <VStack gap={4}>
                                                    <FaUpload size={48} />
                                                    <Text fontSize="lg" fontWeight="medium">Click to upload plant photo</Text>
                                                    <Text fontSize="md" color="gray.500">
                                                        JPG, PNG up to 10MB
                                                    </Text>
                                                    <Text fontSize="sm" color="gray.400">
                                                        High quality photos help with AI analysis
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
                                                size="lg"
                                                w="full"
                                                _hover={{
                                                    transform: "scale(1.02)",
                                                    bgColor: "teal.500",
                                                }}
                                            >
                                                <FaMagic /> AI Auto-Fill from Photo
                                            </Button>
                                        )}
                                    </VStack>
                                </Box>

                                {/* Right Column - Form Inputs */}
                                <Box flex={1} minW="400px">
                                    <VStack gap={4} align="stretch">
                                        {/* Basic Information */}
                                        <HStack gap={4}>
                                            {/* Plant Name */}
                                            <FormField
                                                label="Plant Name"
                                                value={formData.name}
                                                onChange={(value) => handleInputChange("name", value)}
                                                placeholder="e.g., My Fiddle Leaf Fig"
                                                isRequired={true}
                                                flex={1}
                                            />

                                            {/* Species */}
                                            <Dropdown
                                                isRequired={true}
                                                title="Species"
                                                value={formData.species}
                                                onValueChange={(value) => handleInputChange("species", value)}
                                                options={PLANT_SPECIES}
                                                placeholder="Select species"
                                                flex={1}
                                            />
                                        </HStack>
                                        
                                        {/* Species Details */}
                                        <FormField
                                            label="Species Details"
                                            value={formData.species_details}
                                            onChange={(value) => handleInputChange("species_details", value)}
                                            placeholder="e.g., Ficus lyrata, Monstera deliciosa"
                                        />
                                        
                                        {/* Description */}
                                        <Box>
                                            <Text fontSize="sm" fontWeight="medium" mb={2}>Description</Text>
                                            <Textarea
                                                value={formData.description}
                                                onChange={(e) => handleInputChange("description", e.target.value)}
                                                placeholder="Describe your plant..."
                                                rows={3}
                                            />
                                        </Box>

                                        {/* Location */}
                                        <FormField
                                            label="Location"
                                            value={formData.location}
                                            onChange={(value) => handleInputChange("location", value)}
                                            placeholder="e.g., Living room window, Bedroom, Balcony"
                                        />
                                        
                                        <HStack gap={4}>
                                            {/* Watering Frequency */}
                                            <FormField
                                                label="💧 Watering Frequency (days)"
                                                labelColor="blue.400"
                                                type="number"
                                                value={formData.watering_frequency_days}
                                                onChange={(value) => handleInputChange("watering_frequency_days", value)}
                                                placeholder="7"
                                                flex={1}
                                            />

                                            {/* Light Requirements */}
                                            <Dropdown
                                                title="💡 Light Requirements"
                                                titleColor="yellow.400"
                                                value={formData.light_requirements}
                                                onValueChange={(value) => handleInputChange("light_requirements", value)}
                                                options={[
                                                    { value: "low", label: "Low Light" },
                                                    { value: "medium", label: "Medium Light" },
                                                    { value: "high", label: "High Light" },
                                                    { value: "bright indirect", label: "Bright Indirect" },
                                                ]}
                                                placeholder="Select light needs"
                                                flex={1}
                                            />
                                        </HStack>
                                        
                                        <HStack gap={4}>
                                            {/* Humidity Preference */}
                                            <Dropdown
                                                title="🌿 Humidity Preference"
                                                titleColor="green.400"
                                                value={formData.humidity_preference}
                                                onValueChange={(value) => handleInputChange("humidity_preference", value)}
                                                options={[
                                                    { value: "low", label: "Low" },
                                                    { value: "medium", label: "Medium" },
                                                    { value: "high", label: "High" },
                                                ]}
                                                placeholder="Select humidity"
                                                flex={1}
                                            />

                                            {/* Temperature Range */}
                                            <FormField
                                                label="🌡️ Temperature Range"
                                                labelColor="red.400"
                                                value={formData.temperature_range}
                                                onChange={(value) => handleInputChange("temperature_range", value)}
                                                placeholder="e.g., 65-75°F"
                                                flex={1}
                                            />
                                        </HStack>
                                    </VStack>
                                </Box>
                            </HStack>
                        </Dialog.Body>

                        <Dialog.Footer>
                            <Button variant="outline" onClick={handleClose}>
                                Cancel
                            </Button>
                            <Button
                                colorScheme="green"
                                onClick={handleSubmit}
                                loading={isSubmitting}
                                disabled={isSubmitting 
                                    || isAnalyzing 
                                    || !selectedImage 
                                    || !formData.name 
                                    || !formData.species
                                }
                                _hover={{
                                    transform: "scale(1.1)",
                                    bgColor: "teal.500",
                                }}
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
