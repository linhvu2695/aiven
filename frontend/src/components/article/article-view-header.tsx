import {
    Box,
    VStack,
    HStack,
    Text,
    Input,
    Button,
    Icon,
} from "@chakra-ui/react";
import { useState } from "react";
import { FaSave, FaTimes, FaCheck, FaCircle, FaProjectDiagram } from "react-icons/fa";
import { useArticle } from "@/context/article-ctx";
import { Tooltip } from "@/components/ui/tooltip";
import { toaster } from "@/components/ui/toaster";
import { BASE_URL } from "@/App";

interface ArticleViewHeaderProps {
    onSave: () => void;
    onCancel: () => void;
}

export const ArticleViewHeader = ({ onSave, onCancel }: ArticleViewHeaderProps) => {
    const { selectedArticle: article, setSelectedArticle, articleDraft, mode, updateArticleDraft } = useArticle();
    const [isAddingToGraph, setIsAddingToGraph] = useState(false);

    const handleAddToGraph = async () => {
        if (!article) return;

        setIsAddingToGraph(true);
        try {
            const response = await fetch(BASE_URL + "/api/article/addgraph", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    article_id: article.id,
                    force_readd: false,
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "Failed to add article to graph");
            }

            // Update the article state to reflect the change
            setSelectedArticle({ ...article, added_to_graph: true });

            toaster.create({
                title: "Article added to knowledge graph",
                type: "success",
            });
        } catch (error) {
            toaster.create({
                title: "Failed to add article to graph",
                description: error instanceof Error ? error.message : "Unknown error",
                type: "error",
            });
        } finally {
            setIsAddingToGraph(false);
        }
    };

    if (!article) return null;

    return (
        <Box p={6} borderBottom="1px solid" borderColor="gray.200" _dark={{ borderColor: "gray.700" }}>
            {mode === "edit" ? (
                <VStack gap={4} align="stretch">
                    <Input
                        placeholder="Article title..."
                        value={articleDraft?.title || ""}
                        onChange={(e) => updateArticleDraft("title", e.target.value)}
                        fontSize="2xl"
                        fontWeight="bold"
                        variant="flushed"
                    />
                    <Input
                        placeholder="Summary (optional)..."
                        value={articleDraft?.summary || ""}
                        onChange={(e) => updateArticleDraft("summary", e.target.value)}
                        fontSize="md"
                        color="gray.600"
                        variant="flushed"
                    />
                    {/* Action buttons for edit mode */}
                    <HStack gap={2} justify="flex-end">
                        <Button
                            size="sm"
                            colorScheme="green"
                            onClick={onSave}
                        >
                            <FaSave /> Save
                        </Button>
                        <Button
                            size="sm"
                            variant="outline"
                            onClick={onCancel}
                        >
                            <FaTimes /> Cancel
                        </Button>
                    </HStack>
                </VStack>
            ) : (
                <VStack gap={2} align="start">
                    <HStack gap={3}>
                        <Text fontSize="2xl" fontWeight="bold">
                            {article.title || "Untitled"}
                        </Text>
                        <Tooltip
                            content={article.added_to_graph ? "Added to knowledge graph" : "Not in knowledge graph"}
                        >
                            <Icon
                                color={article.added_to_graph ? "green.500" : "gray.400"}
                                boxSize={4}
                            >
                                {article.added_to_graph ? <FaCheck /> : <FaCircle />}
                            </Icon>
                        </Tooltip>
                        {!article.added_to_graph && (
                            <Button
                                size="xs"
                                variant="outline"
                                onClick={handleAddToGraph}
                                loading={isAddingToGraph}
                            >
                                <FaProjectDiagram /> Add to Graph
                            </Button>
                        )}
                    </HStack>
                    {article.summary && (
                        <Text fontSize="md" color="gray.600" _dark={{ color: "gray.400" }}>
                            {article.summary}
                        </Text>
                    )}
                    <HStack fontSize="sm" color="gray.500" gap={4}>
                        {article.created_at && (
                            <Text>
                                Created at {new Date(article.created_at).toLocaleString()}
                            </Text>
                        )}
                        {article.updated_at && (
                            <Text>
                                Updated at {new Date(article.updated_at).toLocaleString()}
                            </Text>
                        )}
                    </HStack>
                </VStack>
            )}
        </Box>
    );
};
