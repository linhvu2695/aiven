import {
    Box,
    VStack,
    HStack,
    Text,
    IconButton,
    useDisclosure,
    Collapsible,
    Dialog,
    Portal,
    Button,
} from "@chakra-ui/react";
import { FaChevronRight, FaChevronDown, FaPlus, FaTrash } from "react-icons/fa";
import { useDraggable, useDroppable } from "@dnd-kit/core";
import { useState } from "react";
import type { ArticleItemInfo } from "./article-item-info";
import { useArticle, type Article } from "../../context/article-ctx";
import { BASE_URL } from "@/App";
import { toaster } from "../ui/toaster";
import { isDescendant } from "../../utils/article-utils";

interface ArticleTreeItemProps {
    article: ArticleItemInfo;
    onSelect: (article: ArticleItemInfo) => void;
    level?: number;
}

export const ArticleTreeItem = ({
    article,
    onSelect,
    level = 0,
}: ArticleTreeItemProps) => {
    const { open, onToggle } = useDisclosure({ defaultOpen: true });
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [articleToDelete, setArticleToDelete] = useState<ArticleItemInfo | null>(null);
    const {
        articles,
        setArticles,
        setArticle,
        setArticleDraft,
        selectedArticle,
        setSelectedArticle,
        setMode,
        searchQuery,
    } = useArticle();

    // Draggable hook
    const {
        attributes,
        listeners,
        setNodeRef: setDragRef,
        transform,
        isDragging,
    } = useDraggable({
        id: article.id,
    });

    // Droppable hook
    const { isOver, setNodeRef: setDropRef } = useDroppable({
        id: article.id,
    });

    const children = articles.filter((a) => a.parent === article.id);
    const hasChildren = children.length > 0;
    const isSelected = selectedArticle?.id === article.id;

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
        const response = await fetch(
            BASE_URL + `/api/article/${articleId}`,
            {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                },
            }
        );

        if (response.ok) {
            // Update the articles state to remove the deleted article
            setArticles((prev) => prev.filter((a) => a.id !== articleId));

            // If the deleted article was selected, clear the selection
            if (
                selectedArticle?.id === articleId ||
                isDescendant(articleId, selectedArticle?.id ?? "", articles)
            ) {
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

    const handleDeleteClick = (article: ArticleItemInfo, event: React.MouseEvent) => {
        event.stopPropagation(); // Prevent triggering article selection
        setArticleToDelete(article);
        setDeleteDialogOpen(true);
    };

    const handleDeleteConfirm = async () => {
        if (!articleToDelete) return;
        
        await handleDeleteArticle(articleToDelete.id);
        
        // Close dialog and reset state
        setDeleteDialogOpen(false);
        setArticleToDelete(null);
    };

    const handleDeleteCancel = () => {
        setDeleteDialogOpen(false);
        setArticleToDelete(null);
    };

    const style = transform
        ? {
              transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
              opacity: isDragging ? 0.5 : 1,
          }
        : undefined;

    return (
        <Box ref={setDropRef} style={style}>
            <HStack
                ref={setDragRef}
                {...attributes}
                {...listeners}
                onClick={() => onSelect(article)}
                cursor={isDragging ? "grabbing" : "pointer"}
                p={2}
                pl={level * 8 + 4}
                bg={
                    isSelected
                        ? "teal.800"
                        : isOver
                        ? "blue.800"
                        : "transparent"
                }
                color={isSelected ? "white" : "inherit"}
                _hover={{
                    bg: isSelected
                        ? "teal.800"
                        : isOver
                        ? "blue.800"
                        : "gray.100",
                    _dark: {
                        bg: isSelected
                            ? "teal.800"
                            : isOver
                            ? "blue.800"
                            : "gray.900",
                    },
                    "& .add-button, & .delete-button": {
                        opacity: 1,
                    },
                }}
                borderRadius="md"
                gap={2}
                border={isOver ? "2px dashed" : "none"}
                borderColor={isOver ? "blue.400" : "transparent"}
            >
                <Text
                    fontSize="sm"
                    fontWeight={isSelected ? "semibold" : "normal"}
                    flex={1}
                >
                    {article.title}
                </Text>

                {/* Fold button */}
                {hasChildren && searchQuery === "" && (
                    <IconButton
                        aria-label="Toggle children"
                        variant="ghost"
                        opacity={0.2}
                        bg={"transparent"}
                        size="xs"
                        ml="auto"
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
                    onClick={(e) => handleDeleteClick(article, e)}
                >
                    <FaTrash />
                </IconButton>
            </HStack>

            {hasChildren && searchQuery === "" && (
                <Collapsible.Root open={open}>
                    <Collapsible.Content>
                        <VStack gap={0} align="stretch">
                            {children.map((child) => (
                                <ArticleTreeItem
                                    key={child.id}
                                    article={child}
                                    onSelect={onSelect}
                                    level={level + 1}
                                />
                            ))}
                        </VStack>
                    </Collapsible.Content>
                </Collapsible.Root>
            )}

            {/* Delete confirmation dialog */}
            <Dialog.Root
                open={deleteDialogOpen}
                onOpenChange={(e) => {
                    if (!e.open) handleDeleteCancel();
                }}
                size="sm"
                placement="center"
            >
                <Portal>
                    <Dialog.Backdrop />
                    <Dialog.Positioner>
                        <Dialog.Content>
                            <Dialog.Header>
                                <Dialog.Title>Delete Article</Dialog.Title>
                            </Dialog.Header>
                            <Dialog.Body>
                                Are you sure you want to delete the article <b>"{articleToDelete?.title || "Untitled"}"</b>? 
                                <br />
                                <br />
                                This action cannot be undone and will also delete all child articles.
                            </Dialog.Body>
                            <Dialog.Footer>
                                <Dialog.ActionTrigger asChild>
                                    <Button variant="solid" onClick={handleDeleteCancel}>Cancel</Button>
                                </Dialog.ActionTrigger>
                                <Button
                                    variant="outline"
                                    colorScheme="red"
                                    onClick={handleDeleteConfirm}
                                >
                                    Delete
                                </Button>
                            </Dialog.Footer>
                            <Dialog.CloseTrigger />
                        </Dialog.Content>
                    </Dialog.Positioner>
                </Portal>
            </Dialog.Root>
        </Box>
    );
};
