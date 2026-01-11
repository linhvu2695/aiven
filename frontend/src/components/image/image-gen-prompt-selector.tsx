import { Box, IconButton, Text } from "@chakra-ui/react";
import { 
    FaTshirt,
    FaEraser,
    FaBuilding,
} from "react-icons/fa";
import type { IconType } from "react-icons";
import { Tooltip } from "@/components/ui/tooltip";

// Prompt templates for image editing
interface PromptTemplate {
    title: string;
    prompt: string;
    icon: IconType;
}

const PROMPT_TEMPLATES: PromptTemplate[] = [
    {
        title: "Fashion product corkboard",
        prompt: "Create a fashion product collage on a brown corkboard based on this outfit.",
        icon: FaTshirt,
    },
    {
        title: "Building blueprint",
        prompt: "Create an orthographic blueprint that describes this building in plan.",
        icon: FaBuilding,
    },
    {
        title: "Remove background",
        prompt: "Remove the background from this image and replace it with an empty transparent background.",
        icon: FaEraser,
    },
];

interface ImageGenPromptSelectorProps {
    onSelectPrompt: (prompt: string) => void;
    disabled?: boolean;
}

export const ImageGenPromptSelector = ({ onSelectPrompt, disabled }: ImageGenPromptSelectorProps) => {
    return (
        <Box>
            <Text fontSize="sm" fontWeight="medium" mb={2} color="gray.500">
                Prompt Templates
            </Text>
            <Box display="flex" flexDirection="row" gap={2} flexWrap="wrap">
                {PROMPT_TEMPLATES.map((template) => (
                    <Tooltip 
                        key={template.title} 
                        content={template.title}
                        showArrow
                    >
                        <IconButton
                            aria-label={template.title}
                            variant="outline"
                            size="lg"
                            onClick={() => onSelectPrompt(template.prompt)}
                            disabled={disabled}
                            transition="all 0.2s ease"
                            _hover={{
                                transform: "scale(1.1)",
                                bgColor: "teal.500",
                                color: "white",
                                borderColor: "teal.500",
                            }}
                        >
                            <template.icon />
                        </IconButton>
                    </Tooltip>
                ))}
            </Box>
        </Box>
    );
};

export default ImageGenPromptSelector;
