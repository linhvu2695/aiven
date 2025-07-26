export interface ChatMessageInfo {
    content: string;
    role: string;
    file?: File;
    filePreview?: string | null;
}