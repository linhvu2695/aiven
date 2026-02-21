export interface TaskDetail {
    title: string;
    identifier: string;
    doc_sub_type: string;
    status: string;
    time_spent_mn: number;
    time_left_mn: number;
    assigned_to: string;
    main_dev_team: string[];
    estimated_completion_date: string | null;
    cortex_share_link: string;
    importance_for_next_release: string;
    dependencies: string[];
    estimated_start_date: string | null;
    estimated_end_date: string | null;
    completion_date: string | null;
    parent_folder_identifier: string;
    monitor: boolean;
    module: string;
}
