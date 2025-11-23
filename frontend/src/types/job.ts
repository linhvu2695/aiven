export type JobStatus = 
    | "pending" 
    | "started" 
    | "retry" 
    | "progress" 
    | "success" 
    | "failure" 
    | "cancelled" 
    | "expired";

// Runtime constants for job status checks
export const ACTIVE_JOB_STATUSES: JobStatus[] = ["pending", "started", "progress", "retry"];
export const COMPLETED_JOB_STATUSES: JobStatus[] = ["success", "failure", "cancelled", "expired"];

export type JobPriority = 3 | 5 | 7 | 9;

export type JobType = 
    | "video_generation"
    | "video_processing"
    | "image_processing"
    | "data_export"
    | "data_import"
    | "email_notification"
    | "batch_update"
    | "scheduled_task"
    | "cleanup"
    | "general";

export interface JobProgress {
    current: number;
    total: number;
    message?: string;
}

export interface JobResult {
    success: boolean;
    data?: Record<string, any>;
    message?: string;
}

export interface JobInfo {
    id: string;
    job_type: JobType;
    job_name: string;
    status: JobStatus;
    progress?: JobProgress;
    priority: JobPriority;
    metadata: Record<string, any>;
    entity_id?: string;
    entity_type?: string;
    created_at: string;
    started_at?: string;
    completed_at?: string;
    expires_at?: string;
    retries: number;
    max_retries: number;
    retry_delay?: number;
    result?: JobResult;
}

export interface JobListRequest {
    page?: number;
    page_size?: number;
    job_type?: JobType;
    status?: JobStatus;
    entity_id?: string;
    entity_type?: string;
    priority?: JobPriority;
}

export interface JobListResponse {
    jobs: JobInfo[];
    total: number;
    page: number;
    page_size: number;
}

