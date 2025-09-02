import {
    Dialog,
    HStack,
    Box,
    CloseButton,
    VStack,
    Heading,
} from "@chakra-ui/react";
import PlantDetailInfo from "./plant-detail-info";
import PlantDetailTimeline from "./plant-detail-timeline";
import { type PlantInfo, type PlantInfoWithImage } from "@/types/plant";

interface PlantDetailDialogProps {
    plant: PlantInfoWithImage | null;
    isOpen: boolean;
    onClose: () => void;
    onPlantUpdate?: (updatedPlant: PlantInfo) => void;
}

export const PlantDetailDialog = ({ 
    plant, 
    isOpen, 
    onClose,
    onPlantUpdate 
}: PlantDetailDialogProps) => {
    if (!plant) return null;

    return (
        <Dialog.Root open={isOpen} onOpenChange={(e) => e.open || onClose()}>
            <Dialog.Backdrop />
            <Dialog.Positioner>
                <Dialog.Content maxW="8xl" h="90vh">
                    <VStack gap={4} align="stretch" h="100%">                        
                        {/* Content */}
                        <Box overflow="hidden" flex={1}>
                            <HStack h="100%" align="stretch" gap={0} p={6}>
                                {/* Left Side - Plant Information (40% width) */}
                                <Box flex="0 0 40%" minW="0">
                                    <PlantDetailInfo 
                                        plant={plant}
                                        onPlantUpdate={onPlantUpdate}
                                        onClose={onClose}
                                    />
                                </Box>
                                
                                {/* Right Side - Timeline (60% width) */}
                                <Box flex="0 0 60%" minW="0">
                                    <PlantDetailTimeline 
                                        plant={plant}
                                    />
                                </Box>
                            </HStack>
                        </Box>
                    </VStack>
                </Dialog.Content>
            </Dialog.Positioner>
        </Dialog.Root>
    );
};

export default PlantDetailDialog;
