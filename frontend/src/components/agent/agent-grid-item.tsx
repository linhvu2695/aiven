import {
    Portal,
    Box,
    Text,
    VStack,
    IconButton,
    Dialog,
    useDisclosure,
    Button,
    CloseButton,
} from "@chakra-ui/react";
import { toaster } from "@/components/ui/toaster";
import { FaTrash } from "react-icons/fa";
import { BASE_URL } from "@/App";
import type { AgentItemInfo } from "./agent-item-info";

export interface AgentGridItemProps {
    agentInfo: AgentItemInfo
    onClick?: () => void;
    onDelete?: () => void;
}

export const AgentGridItem = ({
    agentInfo,
    onClick,
    onDelete
}: AgentGridItemProps) => {
    const { open, onOpen, onClose } = useDisclosure();

    const handleDelete = async (id: string) => {
        try {
            const res = await fetch(BASE_URL + `/api/agent/delete?id=${id}`, {
                method: "POST",
            });
            if (res.ok) {
                toaster.create({
                    description: "Agent deleted successfully",
                    type: "success",
                });
                // Optionally, trigger a refresh or callback here
            } else {
                console.log(res);
                toaster.create({
                    description: "Failed to delete agent",
                    type: "error",
                });
            }
        } catch (err) {
            console.log(err);
            toaster.create({
                description: "Error deleting agent",
                type: "error",
            });
        }
        
        onClose();
        if (onDelete) onDelete();
    };

    return (
        <>
            <Box
                borderRadius="lg"
                overflow="hidden"
                position="relative"
                cursor={"pointer"}
                bgImage={`url(${agentInfo.avatar})`}
                bgSize="cover"
                bgPos="center"
                h="300px"
                _hover={{
                    transform: "scale(1.05)",
                    transition: "transform 0.2s ease-in-out",
                }}
                onClick={onClick}
            >
                {/* Delete button */}
                <IconButton
                    aria-label="Delete agent"
                    cursor={"pointer"}
                    size="sm"
                    bg={"transparent"}
                    colorScheme="red"
                    position="absolute"
                    top={2}
                    right={2}
                    zIndex={2}
                    onClick={(e) => {
                        e.stopPropagation();
                        onOpen();
                    }}
                    _hover={{
                        transform: "scale(1.3)",
                        bg: "red.500",
                        color: "white",
                        boxShadow: "0 0 0 4px rgba(229,62,62,0.2)",
                        transition: "all 0.15s cubic-bezier(.4,0,.2,1)",
                    }}
                >
                    <FaTrash />
                </IconButton>

                {/* Grid item */}
                <VStack
                    position="absolute"
                    bottom="0"
                    left="0"
                    right="0"
                    bg="linear-gradient(to top, rgba(0,0,0,0.8), transparent)"
                    p={4}
                    align="start"
                    spaceY={1}
                >
                    <Text fontWeight="bold" fontSize="xl" color="white">
                        {agentInfo.name}
                    </Text>
                    <Text fontSize="sm" color="gray.200" lineClamp={2}>
                        {agentInfo.description}
                    </Text>
                </VStack>
            </Box>

            {/* Delete confirmation popup */}
            <Dialog.Root
                open={open}
                onOpenChange={(e) => {
                    if (!e.open) onClose();
                }}
                size="sm"
                placement="center"
            >
                <Portal>
                    <Dialog.Backdrop />
                    <Dialog.Positioner>
                        <Dialog.Content>
                            <Dialog.Header>
                                <Dialog.Title>Delete Agent</Dialog.Title>
                            </Dialog.Header>
                            <Dialog.Body>
                                Do you want to delete Agent <b>{agentInfo.name}</b>?
                            </Dialog.Body>
                            <Dialog.Footer>
                                <Dialog.ActionTrigger asChild>
                                    <Button variant="solid">Cancel</Button>
                                </Dialog.ActionTrigger>
                                <Button
                                    variant={"outline"}
                                    onClick={() => handleDelete(agentInfo.id)}
                                >
                                    Delete
                                </Button>
                            </Dialog.Footer>
                            <Dialog.CloseTrigger asChild>
                                <CloseButton size="sm" />
                            </Dialog.CloseTrigger>
                        </Dialog.Content>
                    </Dialog.Positioner>
                </Portal>
            </Dialog.Root>
        </>
    );
};
