export interface MultimodalContentItem {
    type: 'text' | 'image';
    text?: string;
    source_type?: string;
    mime_type?: string;
    data?: string;
}

export interface ChatMessageInfo {
    content: string | MultimodalContentItem[];
    role: string;
    file?: File;
    filePreview?: string | null;
}