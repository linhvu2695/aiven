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
