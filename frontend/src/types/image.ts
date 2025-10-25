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
