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
import { useImageView, ViewMode, ViewRatio } from "@/context/image-view-ctx";
import { useColorMode } from "@/components/ui/color-mode";

const PAGE_SIZE_OPTIONS = [5, 10, 20, 30, 50] as const;

interface ViewOptionButtonProps<T> {
    value: T;
    currentValue: T;
    label: string;
    onClick: () => void;
}

const ViewOptionButton = <T,>({ value, currentValue, label, onClick }: ViewOptionButtonProps<T>) => {
    const isSelected = currentValue === value;
    
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
    const { colorMode } = useColorMode();
    const { 
        pageSize, 
        setPageSize, 
        viewMode, 
        setViewMode,
        viewRatio,
        setViewRatio,
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
                    <Dialog.Content
                        bg={colorMode === "dark" ? "rgba(0, 0, 0, 0.80)" : "rgba(255, 255, 255, 0.80)"}
                        backdropFilter="blur(8px)"
                    >
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
                                            <ViewOptionButton
                                                value={ViewMode.SIMPLE}
                                                currentValue={viewMode}
                                                label="Simple"
                                                onClick={() => setViewMode(ViewMode.SIMPLE)}
                                            />
                                            <ViewOptionButton
                                                value={ViewMode.DETAIL}
                                                currentValue={viewMode}
                                                label="Detail"
                                                onClick={() => setViewMode(ViewMode.DETAIL)}
                                            />
                                        </HStack>
                                    </Fieldset.Content>
                                </Fieldset.Root>

                                {/* View Ratio Settings */}
                                <Fieldset.Root>
                                    <Fieldset.Legend>
                                        Grid Size
                                    </Fieldset.Legend>
                                    <Fieldset.Content>
                                        <HStack gap={4}>
                                            <ViewOptionButton
                                                value={ViewRatio.PORTRAIT}
                                                currentValue={viewRatio}
                                                label="Portrait"
                                                onClick={() => setViewRatio(ViewRatio.PORTRAIT)}
                                            />
                                            <ViewOptionButton
                                                value={ViewRatio.SQUARE}
                                                currentValue={viewRatio}
                                                label="Square"
                                                onClick={() => setViewRatio(ViewRatio.SQUARE)}
                                            />
                                            <ViewOptionButton
                                                value={ViewRatio.LANDSCAPE}
                                                currentValue={viewRatio}
                                                label="Landscape"
                                                onClick={() => setViewRatio(ViewRatio.LANDSCAPE)}
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

