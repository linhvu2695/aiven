import { Box, HStack, Input, Button, Flex, IconButton } from "@chakra-ui/react";
import { FaPlus, FaEdit, FaEye } from "react-icons/fa";
import { useState, useEffect, useMemo } from "react";
import { BASE_URL } from "@/App";

import { Tooltip } from "@/components/ui/tooltip";
import { useArticle } from "@/context/article-ctx";
import { ArticleTreePanel } from "@/components/article/article-tree-panel";
import { ArticleView } from "@/components/article/article-view";
import type { ArticleItemInfo } from "@/components/article/article-item-info";
import type { Article } from "@/context/article-ctx";

export const KnowledgePage = () => {
    const {
        setArticle,
        articleDraft,
        setArticleDraft,
        articles,
        setArticles,
        selectedArticle,
        setSelectedArticle,
        mode,
        setMode,
    } = useArticle();
    const [searchQuery, setSearchQuery] = useState("");

    const fetchArticle = async (id: string) => {
        try {
            const response = await fetch(BASE_URL + `/api/article/id=${id}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) throw new Error("Failed to fetch article info");
            const data = await response.json();
            setSelectedArticle(data);
            setArticle(data);
            setArticleDraft(data);
            setMode("view");
        } catch (error) {
            console.error("Error fetching article info:", error);
        }
    };

    const fetchArticles = async () => {
        try {
            const response = await fetch(BASE_URL + "/api/article/search", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) throw new Error("Failed to fetch articles");
            const data = await response.json();
            // Ensure parent field exists, defaulting if not
            const processedArticles = (data.articles || []).map(
                (article: any) => ({
                    ...article,
                    parent: article.parent || "0",
                })
            );
            setArticles(processedArticles);
        } catch (error) {
            console.error("Error fetching articles:", error);
        }
    };

    const saveArticle = async () => {
        if (!articleDraft) return;

        try {
            const response = await fetch(BASE_URL + "/api/article/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    id: articleDraft.id || undefined,
                    title: articleDraft.title,
                    content: articleDraft.content,
                    summary: articleDraft.summary,
                    tags: articleDraft.tags,
                    parent: articleDraft.parent || "0",
                }),
            });

            if (!response.ok) throw new Error("Failed to save article");

            await fetchArticles();
            if (articleDraft.id) {
                await fetchArticle(articleDraft.id);
            }
            setMode("view");
        } catch (error) {
            console.error("Error saving article:", error);
        }
    };

    useEffect(() => {
        fetchArticles();
    }, []);

    const filteredArticles = useMemo(() => {
        if (!searchQuery) return articles;
        return articles.filter(
            (article) =>
                article.title
                    .toLowerCase()
                    .includes(searchQuery.toLowerCase()) ||
                article.summary
                    .toLowerCase()
                    .includes(searchQuery.toLowerCase()) ||
                article.tags.some((tag) =>
                    tag.toLowerCase().includes(searchQuery.toLowerCase())
                )
        );
    }, [searchQuery, articles]);

    const handleNewArticle = () => {
        const newArticle: Article = {
            id: "",
            title: "",
            content: "",
            summary: "",
            tags: [],
            parent: "0",
        };
        setSelectedArticle(newArticle);
        setArticle(newArticle);
        setArticleDraft(newArticle);
        setMode("edit");
    };

    const handleCancel = () => {
        if (selectedArticle && selectedArticle.id !== "") {
            setArticleDraft(selectedArticle);
        } else {
            setArticle(null);
            setArticleDraft(null);
            setSelectedArticle(null);
        }
        setMode("view");
    };

    return (
        <Box h="100vh" overflow="hidden">
            {/* Top Bar */}
            <HStack p={4}>
                {/* Mode Toggle */}
                <HStack gap={2}>
                    <Button
                        size="sm"
                        variant={mode === "view" ? "solid" : "outline"}
                        onClick={() => setMode("view")}
                        disabled={!selectedArticle || selectedArticle.id === ""}
                    >
                        <FaEye /> View
                    </Button>
                    <Button
                        size="sm"
                        variant={mode === "edit" ? "solid" : "outline"}
                        onClick={() => setMode("edit")}
                        disabled={!selectedArticle}
                    >
                        <FaEdit /> Edit
                    </Button>
                </HStack>

                <Box flex={1} />

                {/* Search */}
                <HStack gap={2}>
                    <Input
                        placeholder="Search articles..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        maxW="300px"
                        size="sm"
                    />
                    <Tooltip content="Create new article">
                        <IconButton
                            aria-label="Create new article"
                            size="sm"
                            onClick={handleNewArticle}
                        >
                            <FaPlus />
                        </IconButton>
                    </Tooltip>
                </HStack>
            </HStack>

            {/* Main Content */}
            <Flex h="calc(100vh - 80px)">
                {/* Article Tree */}
                <ArticleTreePanel
                    articles={filteredArticles}
                    selectedId={selectedArticle?.id}
                    onSelect={(article: ArticleItemInfo) =>
                        fetchArticle(article.id)
                    }
                    searchQuery={searchQuery}
                />

                {/* Article View */}
                <Box flex={1} overflow="hidden">
                    <ArticleView
                        article={selectedArticle}
                        articleDraft={articleDraft}
                        mode={mode}
                        onSave={saveArticle}
                        onCancel={handleCancel}
                        onUpdateDraft={setArticleDraft}
                    />
                </Box>
            </Flex>
        </Box>
    );
};

export default KnowledgePage;
