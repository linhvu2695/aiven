import type { ArticleItemInfo } from "../components/article/article-item-info";

/**
 * Helper function to check if an article is a descendant of another article in the tree structure
 * @param ancestorId - The ID of the potential ancestor article
 * @param descendantId - The ID of the potential descendant article
 * @param articles - Array of all articles to search through
 * @returns true if descendantId is a descendant of ancestorId, false otherwise
 */
export const isDescendant = (
    ancestorId: string,
    descendantId: string,
    articles: ArticleItemInfo[]
): boolean => {
    if (ancestorId === "" || descendantId === "") {
        return false;
    }
    
    const article = articles.find((a) => a.id === descendantId);
    if (!article || article.parent === "0") {
        return false;
    }
    if (article.parent === ancestorId) {
        return true;
    }
    return isDescendant(ancestorId, article.parent, articles);
}; 