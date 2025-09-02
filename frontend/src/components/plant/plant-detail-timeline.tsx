import {
    VStack,
    Text,
    Card,
} from "@chakra-ui/react";
import {
    FaCamera,
} from "react-icons/fa";
import type { PlantInfo } from "@/types/plant";

interface PlantDetailTimelineProps {
    plant: PlantInfo;
}

export const PlantDetailTimeline = ({ plant }: PlantDetailTimelineProps) => {
    return (
        <VStack gap={6} align="stretch" h="100%" overflow="auto">

            {/* Placeholder Message */}
            <Card.Root variant="outline" borderStyle="dashed">
                <Card.Body>
                    <VStack gap={3} color="fg.muted" textAlign="center" py={8}>
                        <FaCamera size={32} />
                        <VStack gap={1}>
                            <Text fontWeight="medium">
                                Timeline Coming Soon!
                            </Text>
                            <Text fontSize="sm">
                                This section will display all your plant's photos and care events in chronological order.
                            </Text>
                        </VStack>
                    </VStack>
                </Card.Body>
            </Card.Root>
        </VStack>
    );
};

export default PlantDetailTimeline;
