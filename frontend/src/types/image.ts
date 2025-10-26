export interface ImageUrlInfo {
    image_id: string;
    url?: string;
    expires_at?: string;
    success: boolean;
    message: string;
}

export interface ImageUrlsResponse {
    success: boolean;
    results: ImageUrlInfo[];
    message: string;
}

export interface ImageInfo {
    id: string;
    uploaded_at: string;
    updated_at: string;
    description?: string;
    title?: string;
    filename?: string;
    original_filename?: string;
}

export interface ImageListResponse {
    images: ImageInfo[];
    total: number;
    page: number;
    page_size: number;
}

export interface AspectRatioOption {
    label: string;
    value: string;
}

export const ASPECT_RATIO_OPTIONS: AspectRatioOption[] = [
    { label: "Square (1:1)", value: "1:1" },
    { label: "Portrait (2:3)", value: "2:3" },
    { label: "Landscape (3:2)", value: "3:2" },
    { label: "Mobile (3:4)", value: "3:4" },
    { label: "Twitter (4:3)", value: "4:3" },
    { label: "Instagram (4:5)", value: "4:5" },
    { label: "Camera (5:4)", value: "5:4" },
    { label: "Tiktok (9:16)", value: "9:16" },
    { label: "Widescreen (16:9)", value: "16:9" },
    { label: "Ultra-wide (21:9)", value: "21:9" },
];

export interface ProviderOption {
    label: string;
    value: string;
}

export const PROVIDER_OPTIONS: ProviderOption[] = [
    { label: "Gemini", value: "gemini" },
    { label: "OpenAI", value: "openai" },
];
