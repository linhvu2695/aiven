import { Box, VStack, Text } from "@chakra-ui/react";
import { useMemo } from "react";
import { ArticleTreeItem } from "./article-tree-item";
import type { ArticleItemInfo } from "./article-item-info";

interface ArticleTreePanelProps {
    articles: ArticleItemInfo[];
    selectedId?: string;
    onSelect: (article: ArticleItemInfo) => void;
    searchQuery: string;
}

const ArticleTree = ({ articles, selectedId, onSelect }: {
    articles: ArticleItemInfo[];
    selectedId?: string;
    onSelect: (article: ArticleItemInfo) => void;
}) => {
    // Find root articles (parent = "0")
    const rootArticles = useMemo(() => {
        return articles.filter(article => article.parent === "0");
    }, [articles]);

    return (
        <Box h="full" overflowY="auto">
            <VStack gap={1} align="stretch" p={2}>
                {rootArticles.map(article => (
                    <ArticleTreeItem
                        key={article.id}
                        article={article}
                        articles={articles}
                        selectedId={selectedId}
                        onSelect={onSelect}
                        level={0}
                    />
                ))}
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
                            articles={articles}
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
