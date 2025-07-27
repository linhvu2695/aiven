import { createContext, useContext, useState, type ReactNode, type Dispatch, type SetStateAction } from "react";

export type Article = {
    id: string;
    title: string;
    content: string;
    summary: string;
    tags: string[];
    parent: string;  // Parent article ID, "0" for root level
    children: string[];  // List of child article IDs
    created_at?: string;
    updated_at?: string;
};

type ArticleContextType = {
    article: Article | null;
    setArticle: Dispatch<SetStateAction<Article | null>>;
    articleDraft: Article | null;
    setArticleDraft: Dispatch<SetStateAction<Article | null>>;
    updateArticleDraft: <K extends keyof Article>(
        field: K,
        value: Article[K]
    ) => void;
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
            }}
        >
            {children}
        </ArticleContext.Provider>
    );
};
