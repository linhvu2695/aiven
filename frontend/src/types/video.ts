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

// Video aspect ratio options for video generation
export const VIDEO_ASPECT_RATIO_OPTIONS = [
    { value: "16:9", label: "16:9 (Landscape)" },
    { value: "9:16", label: "9:16 (Portrait)" },
    { value: "1:1", label: "1:1 (Square)" },
    { value: "4:3", label: "4:3 (Classic)" },
    { value: "3:4", label: "3:4 (Portrait Classic)" },
];

// Video duration options for video generation
export const VIDEO_DURATION_OPTIONS = [
    { value: "4", label: "4 seconds" },
    { value: "8", label: "8 seconds" },
    { value: "12", label: "12 seconds" },
];

