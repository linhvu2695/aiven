import {
    FaQuestionCircle,
    FaCode,
    FaFileAlt,
    FaFlask,
    FaSearchPlus,
    FaBug,
} from "react-icons/fa";

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

export const docSubTypeIcon = (docSubType: string): { icon: React.ReactNode; color: string } => {
    const s = docSubType.toLowerCase();
    if (s.includes("question")) return { icon: <FaQuestionCircle size={12} />, color: "cyan.400" };
    if (s.includes("development")) return { icon: <FaCode size={12} />, color: "yellow.400" };
    if (s.includes("technical document")) return { icon: <FaFileAlt size={12} />, color: "purple.400" };
    if (s.includes("research") || s.includes("analysis")) return { icon: <FaFlask size={12} />, color: "cyan.400" };
    if (s.includes("code review")) return { icon: <FaSearchPlus size={12} />, color: "orange.400" };
    if (s.includes("defect")) return { icon: <FaBug size={12} />, color: "red.400" };
    return { icon: null, color: "gray.400" };
};
