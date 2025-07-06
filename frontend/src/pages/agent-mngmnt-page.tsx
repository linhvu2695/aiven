import {
    Box,
    SimpleGrid,
    Input,
    VStack,
    HStack,
    Text,
    IconButton,
    useDisclosure,
    Dialog,
    Portal,
    CloseButton,
} from "@chakra-ui/react";
import { FaArrowLeft, FaArrowRight, FaUserSlash, FaPlus } from "react-icons/fa";
import { AgentGridItem } from "@/components/agent/agent-grid-item";
import { useState, useMemo, useEffect } from "react";
import { BASE_URL } from "@/App";
import { useColorMode } from "@/components/ui/color-mode";
import { Tooltip } from "@/components/ui/tooltip";
import { AgentProvider, useAgent } from "@/context/agent-ctx";
import { AgentCard } from "@/components/agent/agent-card";

interface AgentGridItemInfo {
    id: string;
    name: string;
    description: string;
    avatar: string;
}

const AGENTS_PER_PAGE = 5;

export const AgentManagementPage = () => {
    const { colorMode } = useColorMode();
    const { agent, setAgent, setAgentDraft } = useAgent();
    const [searchQuery, setSearchQuery] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [agents, setAgents] = useState<AgentGridItemInfo[]>([]);
    const { open, onOpen, onClose } = useDisclosure();

    const fetchAgents = async () => {
        try {
            const response = await fetch(BASE_URL + "/api/agent/search", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) throw new Error("Failed to fetch agent info");
            const data = await response.json();
            setAgents(data.agents);
        } catch (error) {
            console.error("Error fetching agent info:", error);
        }
    };

    useEffect(() => {
        fetchAgents();
    }, []);

    const filteredAgents = useMemo(() => {
        return agents.filter((agent) =>
            agent.name.toLowerCase().includes(searchQuery.toLowerCase())
        );
    }, [searchQuery, agents]);

    const paginatedAgents = useMemo(() => {
        const startIndex = (currentPage - 1) * AGENTS_PER_PAGE;
        const endIndex = startIndex + AGENTS_PER_PAGE;
        return filteredAgents.slice(startIndex, endIndex);
    }, [filteredAgents, currentPage]);

    const totalPages = Math.ceil(filteredAgents.length / AGENTS_PER_PAGE);

    const handleDialogClose = () => {
        setAgent(null as any);
        setAgentDraft(null);
        onClose();
    };

    return (
        <>
            <Box p={5}>
                <VStack gap={4} align="stretch">
                    {/* Search */}
                    <HStack gap={4}>
                        <Input
                            borderRadius={18}
                            width={"40vh"}
                            placeholder="Search agents by name..."
                            value={searchQuery}
                            onChange={(e) => {
                                setSearchQuery(e.target.value);
                                setCurrentPage(1); // Reset to first page on search
                            }}
                        />
                    </HStack>

                    {/* Grid */}
                    {paginatedAgents.length === 0 ? (
                        <VStack
                            align="center"
                            justify="center"
                            minH="30vh"
                            w="full"
                            gap={3}
                        >
                            <FaUserSlash size={48} color="#888" />
                            <Text fontSize="lg" color="gray.500">
                                No agents found
                            </Text>
                        </VStack>
                    ) : (
                        <SimpleGrid columns={{ sm: 2, md: 3, lg: 5 }} gap={6}>
                            {/* Add Agent Button as first cell */}
                            <Tooltip content="Create new agent">
                                <Box
                                    borderRadius="lg"
                                    overflow="hidden"
                                    position="relative"
                                    h="300px"
                                    display="flex"
                                    alignItems="center"
                                    justifyContent="center"
                                    cursor="pointer"
                                    _hover={{
                                        bg:
                                            colorMode === "dark"
                                                ? "gray.900"
                                                : "gray.200",
                                        transform: "scale(1.05)",
                                        transition: "transform 0.2s",
                                    }}
                                    onClick={onOpen}
                                >
                                    <FaPlus size={48} color="gray.900" />
                                </Box>
                            </Tooltip>

                            {paginatedAgents.map((agent) => (
                                <AgentGridItem
                                    key={agent.id}
                                    name={agent.name}
                                    description={agent.description}
                                    avatar={agent.avatar}
                                    onClick={() => {
                                        const fetchAgent = async () => {
                                            try {
                                                const response = await fetch(
                                                    BASE_URL +
                                                        `/api/agent/id=${agent.id}`,
                                                    {
                                                        method: "GET",
                                                        headers: {
                                                            "Content-Type":
                                                                "application/json",
                                                        },
                                                    }
                                                );

                                                if (!response.ok)
                                                    throw new Error(
                                                        "Failed to fetch agent info"
                                                    );
                                                const data =
                                                    await response.json();
                                                setAgent(data);
                                                setAgentDraft(data);
                                            } catch (error) {
                                                console.error(
                                                    "Error fetching agent info:",
                                                    error
                                                );
                                            }
                                        };
                                        fetchAgent();
                                        onOpen();
                                    }}
                                />
                            ))}
                        </SimpleGrid>
                    )}

                    {/* Paging */}
                    {totalPages > 0 && (
                        <HStack justify="center" gap={4} mt={4}>
                            <IconButton
                                variant={"ghost"}
                                aria-label="Previous page"
                                onClick={() =>
                                    setCurrentPage((prev) =>
                                        Math.max(prev - 1, 1)
                                    )
                                }
                                disabled={currentPage === 1}
                            >
                                <FaArrowLeft />
                            </IconButton>
                            <Text>
                                Page {currentPage} of {totalPages}
                            </Text>
                            <IconButton
                                variant={"ghost"}
                                aria-label="Next page"
                                onClick={() =>
                                    setCurrentPage((prev) =>
                                        Math.min(prev + 1, totalPages)
                                    )
                                }
                                disabled={currentPage === totalPages}
                            >
                                <FaArrowRight />
                            </IconButton>
                        </HStack>
                    )}
                </VStack>
            </Box>

            {/* Add Agent Dialog */}
            <Dialog.Root
                open={open}
                onOpenChange={(e) => {
                    if (!e.open) handleDialogClose();
                }}
                size="lg"
                placement="center"
            >
                <Portal>
                    <Dialog.Backdrop />
                    <Dialog.Positioner>
                        <Dialog.Content maxW="700px" maxH={"1200px"}>
                            {/* Create agent dialog */}
                            {!agent?.id && (
                                <>
                                    <Dialog.Header>
                                        <Dialog.Title>
                                            Create New Agent
                                        </Dialog.Title>
                                    </Dialog.Header>
                                    <Dialog.Body>
                                        <AgentProvider>
                                            <AgentCard
                                                mode="create"
                                                onSave={() => {
                                                    fetchAgents();
                                                    handleDialogClose();
                                                }}
                                                onCancel={handleDialogClose}
                                                inDialog={true}
                                            />
                                        </AgentProvider>
                                    </Dialog.Body>
                                </>
                            )}

                            {/* Update agent dialog */}
                            {agent?.id && (
                                <>
                                    <Dialog.Header>
                                        <Dialog.Title>
                                            Update Agent
                                        </Dialog.Title>
                                    </Dialog.Header>
                                    <Dialog.Body>
                                        <AgentCard
                                            mode="edit"
                                            onSave={() => {
                                                fetchAgents();
                                                handleDialogClose();
                                            }}
                                            onCancel={handleDialogClose}
                                            inDialog={true}
                                        />
                                    </Dialog.Body>
                                </>
                            )}

                            <Dialog.CloseTrigger asChild>
                                <CloseButton
                                    size="sm"
                                    position="absolute"
                                    top={2}
                                    right={2}
                                />
                            </Dialog.CloseTrigger>
                        </Dialog.Content>
                    </Dialog.Positioner>
                </Portal>
            </Dialog.Root>
        </>
    );
};
