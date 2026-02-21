import type { ReactNode } from "react";
import { FaBars, FaCalendarCheck } from "react-icons/fa6";
import type { TaskDetail } from "@/components/work/work-types";

/** View modes for the team page content area */
export type TeamViewMode = "incomplete_tasks" | "completed_tasks";

export interface TeamViewModeOption {
    id: TeamViewMode;
    label: string;
}

export const TEAM_VIEW_MODES: TeamViewModeOption[] = [
    { id: "incomplete_tasks", label: "Incomplete Tasks" },
    { id: "completed_tasks", label: "Completed Tasks" },
];

export const TEAM_VIEW_MODE_ICONS: Record<TeamViewMode, ReactNode> = {
    incomplete_tasks: <FaBars />,
    completed_tasks: <FaCalendarCheck />,
};

export const isObsoleteTask = (task: TaskDetail) =>
    (task.status || "").toLowerCase().includes("obsolete");

export interface MemberWorkload {
    name: string;
    tasks: TaskDetail[];
}

export const memberTaskCount = (m: MemberWorkload) => m.tasks.length;
export const memberTimeSpentMn = (m: MemberWorkload) =>
    m.tasks.reduce((s, t) => s + t.time_spent_mn, 0);
export const memberTimeLeftMn = (m: MemberWorkload) =>
    m.tasks.reduce((s, t) => s + (t.time_left_mn ?? 0), 0);

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

/** Colors for module pie chart slices */
export const MODULE_COLORS = [
    "teal.400",
    "blue.400",
    "purple.400",
    "orange.400",
    "cyan.400",
    "pink.400",
    "yellow.400",
    "red.400",
    "green.400",
];
