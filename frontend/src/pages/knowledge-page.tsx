import { Box, HStack, Input, Button, Flex, IconButton } from "@chakra-ui/react";
import { FaPlus, FaEdit, FaEye, FaFilePdf } from "react-icons/fa";
import { useEffect, useRef, useState } from "react";
import { BASE_URL } from "@/App";

import { Tooltip } from "@/components/ui/tooltip";
import { useArticle } from "@/context/article-ctx";
import { ArticleTreePanel, ArticleView, type ArticleItemInfo } from "@/components/article";
import type { Article } from "@/context/article-ctx";
import { toaster } from "@/components/ui/toaster";

export const KnowledgePage = () => {
    const {
        setArticle,
        articleDraft,
        setArticleDraft,
        setArticles,
        selectedArticle,
        setSelectedArticle,
        mode,
        setMode,
        searchQuery,
        setSearchQuery,
    } = useArticle();
    const pdfInputRef = useRef<HTMLInputElement>(null);
    const [isUploadingPdf, setIsUploadingPdf] = useState(false);

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

            var result = await response.json();
            console.log(result);
            if (!result.success) {
                toaster.create({
                    description: result.message,
                    type: "error",
                });
                return;
            } else {
                toaster.create({
                    description: "Article saved successfully",
                    type: "success",
                });
                articleDraft.id = result.id;
                setArticle(articleDraft);
                setSelectedArticle(articleDraft);
                setMode("view");
            }

            await fetchArticles();
        } catch (error) {
            console.error("Error saving article:", error);
        }
    };

    useEffect(() => {
        fetchArticles();
    }, []);

    const handleNewArticle = () => {
        const newArticle: Article = {
            id: "",
            title: "",
            content: "",
            summary: "",
            tags: [],
            parent: selectedArticle?.id || "0",
        };
        setSelectedArticle(newArticle);
        setArticle(newArticle);
        setArticleDraft(newArticle);
        setMode("edit");
    };    

    const handlePdfUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setIsUploadingPdf(true);
        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("parent", selectedArticle?.id || "0");

            const response = await fetch(BASE_URL + "/api/article/from-pdf", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "Failed to parse PDF");
            }

            const result = await response.json();
            if (result.success) {
                toaster.create({
                    description: "PDF parsed and article created successfully",
                    type: "success",
                });
                await fetchArticles();
                // Select the newly created article
                if (result.article_id) {
                    await fetchArticle(result.article_id);
                }
            } else {
                throw new Error(result.message || "Failed to create article from PDF");
            }
        } catch (error) {
            console.error("Error uploading PDF:", error);
            toaster.create({
                description: error instanceof Error ? error.message : "Failed to upload PDF",
                type: "error",
            });
        } finally {
            setIsUploadingPdf(false);
            // Reset the input so the same file can be uploaded again
            if (pdfInputRef.current) {
                pdfInputRef.current.value = "";
            }
        }
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
                    <Tooltip content="Upload PDF as article">
                        <IconButton
                            aria-label="Upload PDF"
                            size="sm"
                            onClick={() => pdfInputRef.current?.click()}
                            loading={isUploadingPdf}
                        >
                            <FaFilePdf />
                        </IconButton>
                    </Tooltip>
                    <input
                        ref={pdfInputRef}
                        type="file"
                        accept=".pdf"
                        style={{ display: "none" }}
                        onChange={handlePdfUpload}
                    />
                </HStack>
            </HStack>

            {/* Main Content */}
            <Flex h="calc(100vh - 80px)">
                {/* Article Tree */}
                <ArticleTreePanel
                    onSelect={(article: ArticleItemInfo) =>
                        fetchArticle(article.id)
                    }
                />

                {/* Article View */}
                <Box flex={1} overflow="hidden">
                    <ArticleView
                        onSave={saveArticle}
                        onCancel={handleCancel}
                    />
                </Box>
            </Flex>
        </Box>
    );
};

export default KnowledgePage;
