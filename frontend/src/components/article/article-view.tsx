import {
    Box,
    VStack,
    HStack,
    Text,
    Input,
    Button,
    Flex,
} from "@chakra-ui/react";
import { FaSave, FaTimes } from "react-icons/fa";
import { useColorMode } from "@/components/ui/color-mode";
import type { Article, ViewMode } from "@/context/article-ctx";

interface ArticleViewProps {
    article: Article | null;
    articleDraft: Article | null;
    mode: ViewMode;
    onSave: () => void;
    onCancel: () => void;
    onUpdateDraft: (updater: (prev: Article | null) => Article | null) => void;
}

export const ArticleView = ({
    article,
    articleDraft,
    mode,
    onSave,
    onCancel,
    onUpdateDraft,
}: ArticleViewProps) => {
    const { colorMode } = useColorMode();

    if (!article) {
        return (
            <Flex h="full" align="center" justify="center">
                <VStack gap={4} textAlign="center">
                    <Text fontSize="lg" color="gray.500">
                        Select an article from the tree to view its content
                    </Text>
                    <Text fontSize="sm" color="gray.400">
                        Or create a new article using the + button
                    </Text>
                </VStack>
            </Flex>
        );
    }

    return (
        <VStack h="full" gap={0} align="stretch">
            {/* Article Header */}
            <Box p={6} borderBottom="1px solid" borderColor="gray.200" _dark={{ borderColor: "gray.700" }}>
                {mode === "edit" ? (
                    <VStack gap={4} align="stretch">
                        <Input
                            placeholder="Article title..."
                            value={articleDraft?.title || ""}
                            onChange={(e) => onUpdateDraft(prev => prev ? { ...prev, title: e.target.value } : null)}
                            fontSize="2xl"
                            fontWeight="bold"
                            variant="flushed"
                        />
                        <Input
                            placeholder="Summary (optional)..."
                            value={articleDraft?.summary || ""}
                            onChange={(e) => onUpdateDraft(prev => prev ? { ...prev, summary: e.target.value } : null)}
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
                        <Text fontSize="2xl" fontWeight="bold">
                            {article.title || "Untitled"}
                        </Text>
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

            {/* Article Content */}
            <Box flex={1} p={6} overflow="auto">
                {mode === "edit" ? (
                    <textarea
                        placeholder="Write your article content here..."
                        value={articleDraft?.content || ""}
                        onChange={(e) => onUpdateDraft(prev => prev ? { ...prev, content: e.target.value } : null)}
                        style={{
                            width: "100%",
                            height: "100%",
                            border: "1px solid #e2e8f0",
                            borderRadius: "6px",
                            padding: "12px",
                            fontSize: "14px",
                            lineHeight: "1.5",
                            resize: "none",
                            outline: "none",
                            backgroundColor: colorMode === "dark" ? "#2d3748" : "#ffffff",
                            color: colorMode === "dark" ? "#ffffff" : "#000000",
                        }}
                    />
                ) : (
                    <Box
                        fontSize="md"
                        lineHeight="1.6"
                        whiteSpace="pre-wrap"
                        color="gray.800"
                        _dark={{ color: "gray.200" }}
                    >
                        {article.content || "No content available."}
                    </Box>
                )}
            </Box>
        </VStack>
    );
}; 