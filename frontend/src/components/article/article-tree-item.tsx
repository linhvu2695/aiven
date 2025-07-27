import {
    Box,
    VStack,
    HStack,
    Text,
    IconButton,
    useDisclosure,
} from "@chakra-ui/react";
import { Collapsible } from "@chakra-ui/react";
import { FaChevronRight, FaChevronDown } from "react-icons/fa";
import { useMemo } from "react";
import type { ArticleItemInfo } from "./article-item-info";

interface ArticleTreeItemProps {
    article: ArticleItemInfo;
    articles: ArticleItemInfo[];
    selectedId?: string;
    onSelect: (article: ArticleItemInfo) => void;
    level?: number;
}

export const ArticleTreeItem = ({
    article,
    articles,
    selectedId,
    onSelect,
    level = 0,
}: ArticleTreeItemProps) => {
    const { open, onToggle } = useDisclosure({ defaultOpen: level < 2 });

    // Find children of this article
    const children = useMemo(() => {
        return articles.filter((a) => a.parent === article.id);
    }, [articles, article.id]);

    const hasChildren = children.length > 0;
    const isSelected = selectedId === article.id;

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
                        bg: isSelected ? "teal.800" : "gray.700",
                    },
                }}
                borderRadius="md"
                onClick={() => onSelect(article)}
                gap={2}
            >
                <Text
                    fontSize="sm"
                    fontWeight={isSelected ? "semibold" : "normal"}
                    truncate
                    flex={1}
                >
                    {article.title}
                </Text>

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
            </HStack>

            {hasChildren && (
                <Collapsible.Root open={open}>
                    <VStack gap={0} align="stretch">
                        {children.map((child) => (
                            <ArticleTreeItem
                                key={child.id}
                                article={child}
                                articles={articles}
                                selectedId={selectedId}
                                onSelect={onSelect}
                                level={level + 1}
                            />
                        ))}
                    </VStack>
                </Collapsible.Root>
            )}
        </Box>
    );
};
