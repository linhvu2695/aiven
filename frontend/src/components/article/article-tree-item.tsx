import {
    Box,
    VStack,
    HStack,
    Text,
    IconButton,
    useDisclosure,
    Collapsible,
} from "@chakra-ui/react";
import { FaChevronRight, FaChevronDown, FaPlus, FaTrash } from "react-icons/fa";
import type { ArticleItemInfo } from "./article-item-info";
import { useArticle, type Article } from "../../context/article-ctx";
import { BASE_URL } from "@/App";
import { toaster } from "../ui/toaster";

interface ArticleTreeItemProps {
    article: ArticleItemInfo;
    selectedId?: string;
    onSelect: (article: ArticleItemInfo) => void;
    level?: number;
}

export const ArticleTreeItem = ({
    article,
    selectedId,
    onSelect,
    level = 0,
}: ArticleTreeItemProps) => {
    const { open, onToggle } = useDisclosure({ defaultOpen: level < 2 });
    const {
        articles,
        setArticles,
        setArticle,
        setArticleDraft,
        selectedArticle,
        setSelectedArticle,
        setMode,
    } = useArticle();

    const children = articles.filter((a) => a.parent === article.id);
    const hasChildren = children.length > 0;
    const isSelected = selectedId === article.id;

    const handleAddArticle = (parentId: string) => {
        const newArticle: Article = {
            id: "",
            title: "",
            content: "",
            summary: "",
            tags: [],
            parent: parentId,
        };
        setSelectedArticle(newArticle);
        setArticle(newArticle);
        setArticleDraft(newArticle);
        setMode("edit");
    };

    const handleDeleteArticle = async (articleId: string) => {
        const response = await fetch(BASE_URL + `/api/article/delete?id=${articleId}`, {
            method: "POST",
        });

        if (response.ok) {
            // Update the articles state to remove the deleted article
            setArticles(prev => prev.filter(a => a.id !== articleId));
            
            // If the deleted article was selected, clear the selection
            if (selectedArticle?.id === articleId) {
                setSelectedArticle(null);
                setArticle(null);
                setArticleDraft(null);
            }
            
            toaster.create({
                description: "Article deleted successfully",
                type: "success",
            });
        } else {
            console.log(response);
            toaster.create({
                description: "Failed to delete article",
                type: "error",
            });
        }
    };

    return (
        <Box>
            <HStack
                p={2}
                pl={level * 4 + 4}
                cursor="pointer"
                bg={isSelected ? "teal.800" : "transparent"}
                color={isSelected ? "white" : "inherit"}
                _hover={{
                    bg: isSelected ? "teal.800" : "gray.100",
                    _dark: {
                        bg: isSelected ? "teal.800" : "gray.900",
                    },
                    "& .add-button, & .delete-button": {
                        opacity: 1,
                    },
                }}
                borderRadius="md"
                onClick={() => onSelect(article)}
                gap={2}
            >
                <Text
                    fontSize="sm"
                    fontWeight={isSelected ? "semibold" : "normal"}
                >
                    {article.title}
                </Text>

                {/* Fold button */}
                {hasChildren && (
                    <IconButton
                        aria-label="Toggle children"
                        variant="ghost"
                        bg={"transparent"}
                        size="xs"
                        onClick={(e) => {
                            e.stopPropagation();
                            onToggle();
                        }}
                    >
                        {open ? <FaChevronDown /> : <FaChevronRight />}
                    </IconButton>
                )}

                {/* Add button */}
                <IconButton
                    className="add-button"
                    aria-label="Add article"
                    variant="ghost"
                    bg={"transparent"}
                    size="xs"
                    ml="auto"
                    opacity={0}
                    transition="opacity 0.2s"
                    onClick={(e) => {
                        e.stopPropagation();
                        handleAddArticle(article.id);
                    }}
                >
                    <FaPlus />
                </IconButton>

                {/* Delete button */}
                <IconButton
                    className="delete-button"
                    aria-label="Delete article"
                    variant="ghost"
                    bg={"transparent"}
                    size="xs"
                    opacity={0}
                    transition="opacity 0.2s"
                    onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteArticle(article.id);
                    }}
                >
                    <FaTrash />
                </IconButton>
            </HStack>

            {hasChildren && (
                <Collapsible.Root open={open}>
                    <Collapsible.Content>
                        <VStack gap={0} align="stretch">
                            {children.map((child) => (
                                <ArticleTreeItem
                                    key={child.id}
                                    article={child}
                                    selectedId={selectedId}
                                    onSelect={onSelect}
                                    level={level + 1}
                                />
                            ))}
                        </VStack>
                    </Collapsible.Content>
                </Collapsible.Root>
            )}
        </Box>
    );
};
