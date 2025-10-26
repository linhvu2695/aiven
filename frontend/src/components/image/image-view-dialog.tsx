import {
    Box,
    VStack,
    Text,
    Dialog,
    Portal,
    CloseButton,
    HStack,
    Fieldset,
} from "@chakra-ui/react";
import { useImageView, ViewMode } from "@/context/image-view-ctx";

const PAGE_SIZE_OPTIONS = [5, 10, 20, 30, 50] as const;

interface ViewModeButtonProps {
    mode: ViewMode;
    currentMode: ViewMode;
    label: string;
    onClick: () => void;
}

const ViewModeButton = ({ mode, currentMode, label, onClick }: ViewModeButtonProps) => {
    const isSelected = currentMode === mode;
    
    return (
        <Box
            as="button"
            px={6}
            py={3}
            cursor="pointer"
            borderRadius="md"
            borderWidth="1px"
            bg={isSelected ? "teal" : "transparent"}
            _hover={{bg: "teal"}}
            transition="all 0.2s"
            onClick={onClick}
            flex={1}
        >
            <VStack gap={1}>
                <Text>{label}</Text>
            </VStack>
        </Box>
    );
};

export const ImageViewDialog = () => {
    const { 
        pageSize, 
        setPageSize, 
        viewMode, 
        setViewMode,
        isViewDialogOpen,
        closeViewDialog
    } = useImageView();

    return (
        <Dialog.Root 
            open={isViewDialogOpen} 
            onOpenChange={(e) => {
                if (!e.open) {
                    closeViewDialog();
                }
            }}
            size="md"
            placement="center"
        >
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content>
                        <Dialog.Header>
                            <Dialog.Title>
                                View Settings
                            </Dialog.Title>
                        </Dialog.Header>

                        <Dialog.Body>
                            <VStack align="stretch" gap={6}>
                                {/* Page Size Settings */}
                                <Fieldset.Root>
                                    <Fieldset.Legend>
                                        Page Size
                                    </Fieldset.Legend>
                                    <Fieldset.Content>
                                        <HStack gap={4} wrap="wrap">
                                            {PAGE_SIZE_OPTIONS.map((size) => (
                                                <Box
                                                    key={size}
                                                    p={2}
                                                    borderRadius="md"
                                                    cursor="pointer"
                                                    bg={pageSize === size ? "teal" : "transparent"}
                                                    fontWeight={pageSize === size ? "semibold" : "normal"}
                                                    _hover={{bg: "teal"}}
                                                    transition="all 0.2s"
                                                    onClick={() => setPageSize(size)}
                                                >
                                                    {size}
                                                </Box>
                                            ))}
                                        </HStack>
                                    </Fieldset.Content>
                                </Fieldset.Root>

                                {/* View Mode Settings */}
                                <Fieldset.Root>
                                    <Fieldset.Legend>
                                        View Mode
                                    </Fieldset.Legend>
                                    <Fieldset.Content>
                                        <HStack gap={4}>
                                            <ViewModeButton
                                                mode={ViewMode.SIMPLE}
                                                currentMode={viewMode}
                                                label="Simple"
                                                onClick={() => setViewMode(ViewMode.SIMPLE)}
                                            />
                                            <ViewModeButton
                                                mode={ViewMode.DETAIL}
                                                currentMode={viewMode}
                                                label="Detail"
                                                onClick={() => setViewMode(ViewMode.DETAIL)}
                                            />
                                        </HStack>
                                    </Fieldset.Content>
                                </Fieldset.Root>

                            </VStack>
                        </Dialog.Body>

                        <Dialog.CloseTrigger asChild>
                            <CloseButton size="sm" />
                        </Dialog.CloseTrigger>
                    </Dialog.Content>
                </Dialog.Positioner>
            </Portal>
        </Dialog.Root>
    );
};

export default ImageViewDialog;

