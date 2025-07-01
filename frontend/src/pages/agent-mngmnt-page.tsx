import {
    Box,
    SimpleGrid,
    Input,
    VStack,
    HStack,
    Text,
    IconButton,
} from "@chakra-ui/react";
import { FaArrowLeft, FaArrowRight, FaUserSlash } from "react-icons/fa";
import { AgentGridItem } from "@/components/agent/agent-grid-item";
import { useState, useMemo, useEffect } from "react";
import { BASE_URL } from "@/App";

interface AgentGridItemInfo {
    id: string;
    name: string;
    description: string;
    imageUrl: string;
}

const AGENTS_PER_PAGE = 5;

export const AgentManagementPage = () => {
    const [searchQuery, setSearchQuery] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [agents, setAgents] = useState<AgentGridItemInfo[]>([]);

    useEffect(() => {
        const fetchAgent = async () => {
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
        fetchAgent();
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

    return (
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
                        {paginatedAgents.map((agent) => (
                            <AgentGridItem
                                key={agent.id}
                                name={agent.name}
                                description={agent.description}
                                imageUrl={agent.imageUrl}
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
                                setCurrentPage((prev) => Math.max(prev - 1, 1))
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
    );
};
