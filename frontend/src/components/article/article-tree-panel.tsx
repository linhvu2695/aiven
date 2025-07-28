import { Box, VStack, Text } from "@chakra-ui/react";
import { useEffect } from "react";
import {
    DndContext,
    type DragEndEvent,
    useSensor,
    useSensors,
    PointerSensor,
    useDroppable,
} from "@dnd-kit/core";
import { ArticleTreeItem } from "./article-tree-item";
import type { ArticleItemInfo } from "./article-item-info";
import { useArticle } from "../../context/article-ctx";
import { BASE_URL } from "@/App";
import { toaster } from "../ui/toaster";

interface ArticleTreePanelProps {
    articles: ArticleItemInfo[];
    onSelect: (article: ArticleItemInfo) => void;
    searchQuery: string;
}

const RootDropZone = () => {
    const { isOver, setNodeRef } = useDroppable({
        id: "0", // Root level ID
    });

    return (
        <Box
            ref={setNodeRef}
            p={4}
            mx={2}
            borderRadius="lg"
            border={isOver ? "2px dashed" : "none"}
            borderColor={isOver ? "blue.400" : "transparent"}
            bg={isOver ? "blue.800" : "gray.700"}
            transition="all 0.1s ease"
            textAlign="center"
            h="20px"
            display="flex"
            alignItems="center"
            justifyContent="center"
            _hover={{
                bg: "blue.800",
            }}
        >
            <Text
                color={isOver ? "white" : "gray.300"}
                fontSize="sm"
                fontWeight="medium"
                transition="color 0.2s ease"
            >
                Root
            </Text>
        </Box>
    );
};

const ArticleTree = ({
    onSelect,
}: {
    onSelect: (article: ArticleItemInfo) => void;
}) => {
    const { articles, setArticles } = useArticle();

    // Derive root articles from the articles array
    const rootArticles = articles.filter((article) => article.parent === "0");

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 8,
            },
        })
    );

    const handleDragEnd = async (event: DragEndEvent) => {
        const { active, over } = event;

        console.log(active, over);

        if (!over || active.id === over.id) {
            return;
        }

        const draggedArticleId = active.id as string;
        const targetParentId = over.id as string;

        // Find the dragged article
        const draggedArticle = articles.find((a) => a.id === draggedArticleId);
        if (!draggedArticle) {
            return;
        }

        // Prevent dropping on self or descendants or direct parent
        if (
            draggedArticleId === targetParentId ||
            draggedArticle.parent === targetParentId ||
            isDescendant(draggedArticleId, targetParentId, articles)
        ) {
            toaster.create({
                description: "Cannot move article to itself or its descendants",
                type: "error",
            });
            return;
        }

        try {
            // Update the backend
            const response = await fetch(BASE_URL + "/api/article/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    id: draggedArticleId,
                    title: draggedArticle.title,
                    content: draggedArticle.content || "",
                    summary: draggedArticle.summary || "",
                    tags: draggedArticle.tags || [],
                    parent: targetParentId,
                }),
            });

            if (response.ok) {
                // Update the local state
                setArticles((prev) =>
                    prev.map((article) =>
                        article.id === draggedArticleId
                            ? { ...article, parent: targetParentId }
                            : article
                    )
                );

                toaster.create({
                    description: "Article moved successfully",
                    type: "success",
                });
            } else {
                console.error("Failed to move article:", response);
                toaster.create({
                    description: "Failed to move article",
                    type: "error",
                });
            }
        } catch (error) {
            console.error("Error moving article:", error);
            toaster.create({
                description: "Failed to move article",
                type: "error",
            });
        }
    };

    return (
        <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
            <Box h="full" overflowY="auto">
                <VStack gap={2} align="stretch" h="full" p={2}>
                    {/* Dedicated root drop area */}
                    <RootDropZone />

                    {/* Article tree */}
                    <Box flex={1} p={2}>
                        <VStack gap={1} align="stretch">
                            {rootArticles.map((article) => {
                                return (
                                    <ArticleTreeItem
                                        key={article.id}
                                        article={article}
                                        onSelect={onSelect}
                                        level={0}
                                    />
                                );
                            })}
                            {rootArticles.length === 0 && (
                                <Box p={4} textAlign="center">
                                    <Text color="gray.500" fontSize="sm">
                                        No articles yet
                                    </Text>
                                </Box>
                            )}
                        </VStack>
                    </Box>
                </VStack>
            </Box>
        </DndContext>
    );
};

// Helper function to check if an article is a descendant of another
const isDescendant = (
    ancestorId: string,
    descendantId: string,
    articles: ArticleItemInfo[]
): boolean => {
    const article = articles.find((a) => a.id === descendantId);
    if (!article || article.parent === "0") {
        return false;
    }
    if (article.parent === ancestorId) {
        return true;
    }
    return isDescendant(ancestorId, article.parent, articles);
};

export const ArticleTreePanel = ({
    articles,
    onSelect,
    searchQuery,
}: ArticleTreePanelProps) => {
    const { setArticles } = useArticle();

    // Update the context when articles prop changes
    // This allows the component to still receive articles as props while storing them in context
    useEffect(() => {
        setArticles(articles);
    }, [articles, setArticles]);

    return (
        <Box w="400px">
            <VStack h="full" gap={0} align="stretch">
                <Box p={3}>
                    <Text fontWeight="semibold" fontSize="xl">
                        Articles
                    </Text>
                </Box>
                <Box flex={1} overflow="hidden">
                    {articles.length > 0 ? (
                        <ArticleTree onSelect={onSelect} />
                    ) : (
                        <Box p={4} textAlign="center">
                            <Text color="gray.500" fontSize="sm">
                                {searchQuery
                                    ? "No articles found"
                                    : "No articles yet"}
                            </Text>
                        </Box>
                    )}
                </Box>
            </VStack>
        </Box>
    );
};
