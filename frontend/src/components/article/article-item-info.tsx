export interface ArticleItemInfo {
    id: string;
    title: string;
    summary: string;
    tags: string[];
    parent: string;  // Parent article ID, "0" for root level
    created_at?: Date;
    updated_at?: Date;
} 