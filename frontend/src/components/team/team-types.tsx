import type { ReactNode } from "react";
import { FaBars } from "react-icons/fa6";

/** View modes for the team page content area */
export type TeamViewMode = "incomplete_tasks";

export interface TeamViewModeOption {
    id: TeamViewMode;
    label: string;
}

export const TEAM_VIEW_MODES: TeamViewModeOption[] = [
    { id: "incomplete_tasks", label: "Incomplete Tasks" },
];

export const TEAM_VIEW_MODE_ICONS: Record<TeamViewMode, ReactNode> = {
    incomplete_tasks: <FaBars />,
};

export interface TeamTask {
    title: string;
    identifier: string;
    doc_sub_type?: string;
    status: string;
    time_spent_mn: number;
    time_left_mn: number;
    cortex_share_link?: string;
    estimated_completion_date?: string | null;
    [key: string]: unknown;
}

export interface MemberWorkload {
    name: string;
    task_count: number;
    time_spent_mn: number;
    time_left_mn: number;
    tasks: TeamTask[];
}

export const MEMBER_COLORS = [
    "teal.400",
    "blue.400",
    "purple.400",
    "orange.400",
    "cyan.400",
    "pink.400",
    "yellow.400",
    "red.400",
    "green.400",
    "gray.400",
];
