import {
    FaQuestionCircle,
    FaCode,
    FaFileAlt,
    FaFlask,
    FaSearchPlus,
    FaBug,
    FaVial,
    FaCalendar,
    FaPaintBrush,
    FaCheckSquare,
    FaQuestion,
    FaClipboardList,
} from "react-icons/fa";
import { FaPeopleGroup } from "react-icons/fa6";

/** Accent color pair used across the work page (light / dark mode) */
export const ACCENT_COLOR = { light: "green.600", dark: "green.400" };

/** View modes for the right panel */
export type WorkViewMode = "hierarchy" | "participants" | "kanban";

export interface WorkViewModeOption {
    id: WorkViewMode;
    label: string;
}

export const WORK_VIEW_MODES: WorkViewModeOption[] = [
    { id: "hierarchy", label: "Hierarchy" },
    { id: "participants", label: "Participants" },
    { id: "kanban", label: "Kanban Board" },
];

/** Status groups used by the Kanban board */
export interface KanbanColumn {
    id: string;
    label: string;
    colorPalette: string;
    match: (statusLower: string) => boolean;
}

export const KANBAN_COLUMNS: KanbanColumn[] = [
    {
        id: "todo",
        label: "To Do",
        colorPalette: "blue",
        match: (s) => 
            s.includes("to be vetted") || 
            s.includes("to dispatch") || 
            s.includes("gathering requirements"),
    },
    {
        id: "in_progress",
        label: "In Progress",
        colorPalette: "orange",
        match: (s) => 
            s.includes("in progress") || 
            s.includes("needs peer review"),
    },
    {
        id: "blocked",
        label: "Blocked",
        colorPalette: "red",
        match: (s) => s.includes("blocked"),
    },
    {
        id: "done",
        label: "Done",
        colorPalette: "green",
        match: (s) =>
            s.includes("done") ||
            s.includes("completed") ||
            s.includes("implemented") ||
            s.includes("closed"),
    },
    {
        id: "obsolete",
        label: "Obsolete",
        colorPalette: "gray",
        match: (s) => s.includes("obsolete"),
    },
];

export const formatMinutes = (minutes: number): string => {
    if (minutes === 0) return "0m";
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours === 0) return `${mins}m`;
    if (mins === 0) return `${hours}h`;
    return `${hours}h ${mins}m`;
};

export const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return "—";
    try {
        return new Date(dateStr).toLocaleDateString(undefined, {
            year: "numeric",
            month: "short",
            day: "numeric",
        });
    } catch {
        return "—";
    }
};

export const statusColor = (status: string): string => {
    const s = status.toLowerCase();
    if (
        s.includes("done") ||
        s.includes("completed") ||
        s.includes("implemented") ||
        s.includes("obsolete") ||
        s.includes("closed")
    )
        return "green";
    if (s.includes("progress") || s.includes("dev")) return "orange";
    if (s.includes("blocked")) return "red";
    if (s.includes("todo") || s.includes("open") || s.includes("new")) return "blue";
    return "gray";
};

/** All known doc sub types for filtering */
export const DOC_SUB_TYPES = [
    "Question",
    "Development",
    "Technical Document",
    "Research Analysis",
    "Code Review",
    "Defect - Application",
    "Enhancement",
    "QA",
    "Test Case Review",
    "Meeting",
    "Technical Vetting",
    "Product Discovery",
    "Task Management",
    "Dev Planning",
    "Final Dev Review",
    "Product Review",
    "UX Review",
    "Final Review",
] as const;

export const DEFAULT_DOC_SUB_TYPE_FILTER = new Set(["Development", "QA"]);

export const docSubTypeIcon = (docSubType: string): { icon: React.ReactNode; color: string } => {
    const s = docSubType.toLowerCase();
    if (s.includes("question")) return { icon: <FaQuestion size={12} />, color: "cyan.400" };
    if (s.includes("development")) return { icon: <FaCode size={12} />, color: "yellow.400" };
    if (s.includes("document")) return { icon: <FaFileAlt size={12} />, color: "purple.400" };
    if (s.includes("research") || s.includes("analysis")) return { icon: <FaFlask size={12} />, color: "cyan.400" };
    if (s.includes("code review")) return { icon: <FaSearchPlus size={12} />, color: "orange.400" };
    if (s.includes("defect")) return { icon: <FaBug size={12} />, color: "red.400" };
    if (s.includes("enhancement")) return { icon: <FaPaintBrush size={12} />, color: "blue.400" };
    if (s.includes("qa")) return { icon: <FaVial size={12} />, color: "cyan.400" };
    if (s.includes("test case review")) return { icon: <FaVial size={12} />, color: "cyan.400" };
    if (s.includes("meeting")) return { icon: <FaCalendar size={12} />, color: "green.400" };
    if (s.includes("technical vetting")) return { icon: <FaCheckSquare size={12} />, color: "yellow.400" };
    if (s.includes("product discovery")) return { icon: <FaQuestionCircle size={12} />, color: "green.400" };
    if (s.includes("task management")) return { icon: <FaClipboardList size={12} />, color: "blue.400" };
    if (s.includes("dev planning")) return { icon: <FaPeopleGroup size={12} />, color: "yellow.400" };
    if (s.includes("final dev review")) return { icon: <FaCheckSquare size={12} />, color: "green.400" };
    if (s.includes("product review")) return { icon: <FaCheckSquare size={12} />, color: "green.400" };
    if (s.includes("ux review")) return { icon: <FaCheckSquare size={12} />, color: "green.400" };
    if (s.includes("final review")) return { icon: <FaCheckSquare size={12} />, color: "green.400" };
    return { icon: null, color: "gray.400" };
};
