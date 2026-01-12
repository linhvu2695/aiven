export interface ArticleItemInfo {
    id: string;
    title: string;
    summary: string;
    content: string;
    tags: string[];
    parent: string;  // Parent article ID, "0" for root level
    created_at?: Date;
    updated_at?: Date;
    added_to_graph?: boolean;
} 