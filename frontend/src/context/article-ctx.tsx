import { createContext, useContext, useState, type ReactNode, type Dispatch, type SetStateAction } from "react";
import type { ArticleItemInfo } from "../components/article/article-item-info";

export type Article = {
    id: string;
    title: string;
    content: string;
    summary: string;
    tags: string[];
    parent: string;  // Parent article ID, "0" for root level
    created_at?: string;
    updated_at?: string;
};

export type ViewMode = "view" | "edit";

type ArticleContextType = {
    // Selected article
    article: Article | null;
    setArticle: Dispatch<SetStateAction<Article | null>>;
    articleDraft: Article | null;
    setArticleDraft: Dispatch<SetStateAction<Article | null>>;
    updateArticleDraft: <K extends keyof Article>(
        field: K,
        value: Article[K]
    ) => void;

    // UI state
    selectedArticle: Article | null;
    setSelectedArticle: Dispatch<SetStateAction<Article | null>>;
    mode: ViewMode;
    setMode: Dispatch<SetStateAction<ViewMode>>;

    // Search functionality
    searchQuery: string;
    setSearchQuery: Dispatch<SetStateAction<string>>;

    // Article tree data
    articles: ArticleItemInfo[];
    setArticles: Dispatch<SetStateAction<ArticleItemInfo[]>>;
};

const ArticleContext = createContext<ArticleContextType | undefined>(undefined);

export const useArticle = () => {
    const context = useContext(ArticleContext);
    if (!context) {
        throw new Error("useArticle must be used within an ArticleProvider");
    }
    return context;
};

export const ArticleProvider = ({ children }: { children: ReactNode }) => {
    const [article, setArticle] = useState<Article | null>(null);
    const [articleDraft, setArticleDraft] = useState<Article | null>(null);
    const [articles, setArticles] = useState<ArticleItemInfo[]>([]);
    const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
    const [mode, setMode] = useState<ViewMode>("view");
    const [searchQuery, setSearchQuery] = useState<string>("");

    const updateArticleDraft = <K extends keyof Article>(
        field: K,
        value: Article[K]
    ) => {
        setArticleDraft((prev) => (prev ? { ...prev, [field]: value } : null));
    };

    return (
        <ArticleContext.Provider
            value={{
                article,
                setArticle,
                articleDraft,
                setArticleDraft,
                updateArticleDraft,
                selectedArticle,
                setSelectedArticle,
                mode,
                setMode,
                searchQuery,
                setSearchQuery,
                articles,
                setArticles,
            }}
        >
            {children}
        </ArticleContext.Provider>
    );
};
