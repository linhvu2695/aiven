import {
    Box,
    VStack,
    HStack,
    Text,
    Input,
    Button,
} from "@chakra-ui/react";
import { FaSave, FaTimes } from "react-icons/fa";
import { useArticle } from "@/context/article-ctx";

interface ArticleViewHeaderProps {
    onSave: () => void;
    onCancel: () => void;
}

export const ArticleViewHeader = ({ onSave, onCancel }: ArticleViewHeaderProps) => {
    const { selectedArticle: article, articleDraft, mode, updateArticleDraft } = useArticle();

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
    );
};
