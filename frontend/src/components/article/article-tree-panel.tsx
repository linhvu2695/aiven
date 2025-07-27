import { Box, VStack, Text } from "@chakra-ui/react";
import { useEffect } from "react";
import { ArticleTreeItem } from "./article-tree-item";
import type { ArticleItemInfo } from "./article-item-info";
import { useArticle, type Article } from "../../context/article-ctx";

interface ArticleTreePanelProps {
    articles: ArticleItemInfo[];
    selectedId?: string;
    onSelect: (article: ArticleItemInfo) => void;
    searchQuery: string;
}

const ArticleTree = ({ selectedId, onSelect }: {
    selectedId?: string;
    onSelect: (article: ArticleItemInfo) => void;
}) => {
    const { articles } = useArticle();
    
    // Derive root articles from the articles array
    const rootArticles = articles.filter(article => article.parent === "0");

    return (
        <Box h="full" overflowY="auto">
            <VStack gap={1} align="stretch" p={2}>
                {rootArticles.map(article => {
                    return (
                        <ArticleTreeItem
                            key={article.id}
                            article={article}
                            selectedId={selectedId}
                            onSelect={onSelect}
                            level={0}
                        />
                    );
                })}
            </VStack>
        </Box>
    );
};

export const ArticleTreePanel = ({
    articles,
    selectedId,
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
                        <ArticleTree
                            selectedId={selectedId}
                            onSelect={onSelect}
                        />
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
