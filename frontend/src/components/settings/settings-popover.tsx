import { useState } from "react";
import { Box, Button, Flex, IconButton, Popover, Portal, Text, VStack } from "@chakra-ui/react";
import { FaCog, FaKey } from "react-icons/fa";
import { Tooltip } from "@/components/ui/tooltip";
import { LinkAuthTokenDialog } from "./link-auth-token-dialog";

export const SettingsPopover = () => {
    const [open, setOpen] = useState(false);
    const [authTokenDialogOpen, setAuthTokenDialogOpen] = useState(false);

    return (
        <>
            <Popover.Root
                open={open}
                onOpenChange={(e) => setOpen(e.open)}
                positioning={{ placement: "bottom-start", flip: false }}
            >
                <Popover.Trigger asChild>
                    <Box as="span" display="inline-block">
                        <Tooltip content="Settings" showArrow>
                            <IconButton
                                aria-label="Settings"
                                variant="ghost"
                                size="xl"
                                onClick={() => setOpen(true)}
                            >
                                <FaCog />
                            </IconButton>
                        </Tooltip>
                    </Box>
                </Popover.Trigger>
                <Portal>
                    <Popover.Positioner>
                        <Popover.Content w="200px" p={2}>
                            <Popover.Arrow>
                                <Popover.ArrowTip />
                            </Popover.Arrow>
                            <VStack align="stretch" gap={0}>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    justifyContent="flex-start"
                                    onClick={() => {
                                        setOpen(false);
                                        setAuthTokenDialogOpen(true);
                                    }}
                                >
                                    <Flex align="center" gap={2}>
                                        <FaKey />
                                        <Text fontSize="sm">Set Link Auth Token</Text>
                                    </Flex>
                                </Button>
                            </VStack>
                        </Popover.Content>
                    </Popover.Positioner>
                </Portal>
            </Popover.Root>
            <LinkAuthTokenDialog
                isOpen={authTokenDialogOpen}
                onClose={() => setAuthTokenDialogOpen(false)}
            />
        </>
    );
};
