export interface VideoUrlInfo {
    video_id: string;
    url?: string;
    expires_at?: string;
    thumbnail_url?: string;
    thumbnail_expires_at?: string;
    success: boolean;
    message: string;
}

export interface VideoUrlsResponse {
    success: boolean;
    results: VideoUrlInfo[];
    message: string;
}

export interface VideoInfo {
    id: string;
    uploaded_at: string;
    updated_at: string;
    description?: string;
    title?: string;
    filename?: string;
    original_filename?: string;
    metadata?: {
        width?: number;
        height?: number;
        duration?: number;
        file_size?: number;
    };
}

export interface VideoWithUrl extends VideoInfo {
    url?: string;
    thumbnail_url?: string;
}

export interface VideoListResponse {
    videos: VideoInfo[];
    total: number;
    page: number;
    page_size: number;
}

