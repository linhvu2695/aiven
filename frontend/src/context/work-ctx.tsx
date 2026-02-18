import { createContext, useContext, useState, useCallback, useEffect, useMemo, type ReactNode } from "react";
import { BASE_URL } from "@/App";
import { toaster } from "@/components/ui/toaster";
import type { TaskDetail } from "@/components/work/work-types";
import { DEFAULT_DOC_SUB_TYPE_FILTER } from "@/components/work/work-utils";

interface WorkContextValue {
    monitoredTasks: TaskDetail[];
    selectedRootTask: TaskDetail | null;
    selectedDescendants: TaskDetail[];
    isAdding: boolean;
    isLoadingTree: boolean;
    selectTask: (taskId: string) => Promise<void>;
    addTask: (taskId: string, forceRefresh: boolean) => Promise<void>;
    removeTask: (taskId: string) => Promise<void>;
    updateTask: (updatedTask: TaskDetail) => void;
    refreshTaskTree: (taskId: string) => Promise<void>;

    activeTypeFilters: Set<string>;
    setActiveTypeFilters: (filters: Set<string>) => void;
    activeAssigneeFilters: Set<string> | null;
    setActiveAssigneeFilters: (filters: Set<string> | null) => void;
    assignees: string[];
    filteredTasks: TaskDetail[];
}

const WorkContext = createContext<WorkContextValue | null>(null);

export const useWorkContext = (): WorkContextValue => {
    const ctx = useContext(WorkContext);
    if (!ctx) {
        throw new Error("useWorkContext must be used within a WorkProvider");
    }
    return ctx;
};

export const WorkProvider = ({ children }: { children: ReactNode }) => {
    const [monitoredTasks, setMonitoredTasks] = useState<TaskDetail[]>([]);
    const [selectedRootTask, setSelectedRootTask] = useState<TaskDetail | null>(null);
    const [selectedDescendants, setSelectedDescendants] = useState<TaskDetail[]>([]);
    const [isAdding, setIsAdding] = useState(false);
    const [isLoadingTree, setIsLoadingTree] = useState(false);

    const [activeTypeFilters, setActiveTypeFilters] = useState<Set<string>>(
        () => new Set(DEFAULT_DOC_SUB_TYPE_FILTER)
    );
    const [activeAssigneeFilters, setActiveAssigneeFilters] = useState<Set<string> | null>(null);

    const allTasks = useMemo(() => {
        if (!selectedRootTask) return selectedDescendants;
        return [selectedRootTask, ...selectedDescendants];
    }, [selectedRootTask, selectedDescendants]);

    const assignees = useMemo(() => {
        const names = new Set<string>();
        for (const t of allTasks) {
            if (t.assigned_to) names.add(t.assigned_to);
        }
        return [...names].sort((a, b) => a.localeCompare(b));
    }, [allTasks]);

    const filteredTasks = useMemo(() => {
        const matchingIds = new Set<string>();
        for (const t of allTasks) {
            const typeMatch =
                activeTypeFilters.size === 0 ||
                [...activeTypeFilters].some((f) => t.doc_sub_type.toLowerCase().includes(f.toLowerCase()));
            const assigneeMatch =
                activeAssigneeFilters === null || activeAssigneeFilters.has(t.assigned_to);
            if (typeMatch && assigneeMatch) {
                matchingIds.add(t.identifier);
            }
        }

        const includedIds = new Set(matchingIds);
        const taskMap = new Map(allTasks.map((t) => [t.identifier, t]));
        for (const id of matchingIds) {
            let current = taskMap.get(id);
            while (current && current.parent_folder_identifier) {
                if (includedIds.has(current.parent_folder_identifier)) break;
                includedIds.add(current.parent_folder_identifier);
                current = taskMap.get(current.parent_folder_identifier);
            }
        }

        return allTasks.filter((t) => includedIds.has(t.identifier));
    }, [allTasks, activeTypeFilters, activeAssigneeFilters]);

    useEffect(() => {
        const loadMonitored = async () => {
            try {
                const res = await fetch(`${BASE_URL}/api/work/monitored`);
                if (!res.ok) return;
                const data: TaskDetail[] = await res.json();
                setMonitoredTasks(data);
            } catch (error) {
                console.error("Error loading monitored tasks:", error);
            }
        };
        loadMonitored();
    }, []);

    const selectTask = useCallback(async (taskId: string) => {
        setIsLoadingTree(true);
        try {
            const [rootRes, descRes] = await Promise.all([
                fetch(`${BASE_URL}/api/work/task/${taskId}`),
                fetch(`${BASE_URL}/api/work/task/${taskId}/descendants`),
            ]);

            if (!rootRes.ok) throw new Error("Failed to fetch root task");
            if (!descRes.ok) throw new Error("Failed to fetch descendants");

            setSelectedRootTask(await rootRes.json());
            setSelectedDescendants(await descRes.json());
        } catch (error) {
            console.error("Error fetching task tree:", error);
            toaster.create({ description: "Failed to load task hierarchy", type: "error" });
        } finally {
            setIsLoadingTree(false);
        }
    }, []);

    const addTask = useCallback(async (taskId: string, forceRefresh: boolean) => {
        if (monitoredTasks.some((t) => t.identifier === taskId)) {
            selectTask(taskId);
            return;
        }

        setIsAdding(true);
        try {
            const rootRes = await fetch(`${BASE_URL}/api/work/task/${taskId}?force_refresh=${forceRefresh}`);
            if (!rootRes.ok) throw new Error("Failed to fetch task");
            const rootTask: TaskDetail = await rootRes.json();

            await fetch(`${BASE_URL}/api/work/task/${rootTask.identifier}/monitor`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ monitor: true }),
            });

            setMonitoredTasks((prev) => [...prev, rootTask]);
            selectTask(rootTask.identifier);
        } catch (error) {
            toaster.create({
                description: `Failed to add task ${taskId} to monitor list`,
                type: "error",
            });
        } finally {
            setIsAdding(false);
        }
    }, [monitoredTasks, selectTask]);

    const updateTask = useCallback((updatedTask: TaskDetail) => {
        setMonitoredTasks((prev) =>
            prev.map((t) => (t.identifier === updatedTask.identifier ? updatedTask : t))
        );
        setSelectedRootTask((prev) =>
            prev?.identifier === updatedTask.identifier ? updatedTask : prev
        );
        setSelectedDescendants((prev) =>
            prev.map((t) => (t.identifier === updatedTask.identifier ? updatedTask : t))
        );
    }, []);

    const refreshTaskTree = useCallback(async (taskId: string) => {
        setIsLoadingTree(true);
        try {
            const [rootRes, descRes] = await Promise.all([
                fetch(`${BASE_URL}/api/work/task/${taskId}?force_refresh=true`),
                fetch(`${BASE_URL}/api/work/task/${taskId}/descendants?force_refresh=true`),
            ]);

            if (!rootRes.ok) throw new Error("Failed to refresh root task");
            if (!descRes.ok) throw new Error("Failed to refresh descendants");

            const updatedRoot: TaskDetail = await rootRes.json();
            const updatedDescendants: TaskDetail[] = await descRes.json();

            setMonitoredTasks((prev) =>
                prev.map((t) => (t.identifier === updatedRoot.identifier ? updatedRoot : t))
            );
            setSelectedRootTask((prev) =>
                prev?.identifier === updatedRoot.identifier ? updatedRoot : prev
            );
            setSelectedDescendants(updatedDescendants);

            toaster.create({ description: `Refreshed ${taskId} and all descendants`, type: "success" });
        } catch (error) {
            console.error("Error refreshing task tree:", error);
            toaster.create({ description: `Failed to refresh ${taskId} tree`, type: "error" });
        } finally {
            setIsLoadingTree(false);
        }
    }, []);

    const removeTask = useCallback(async (taskId: string) => {
        try {
            await fetch(`${BASE_URL}/api/work/task/${taskId}/monitor`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ monitor: false }),
            });
        } catch (error) {
            toaster.create({ description: "Failed to remove task from monitor list", type: "error" });
            return;
        }

        setMonitoredTasks((prev) => prev.filter((t) => t.identifier !== taskId));
        if (selectedRootTask?.identifier === taskId) {
            setSelectedRootTask(null);
            setSelectedDescendants([]);
        }
    }, [selectedRootTask]);

    return (
        <WorkContext.Provider
            value={{
                monitoredTasks,
                selectedRootTask,
                selectedDescendants,
                isAdding,
                isLoadingTree,
                selectTask,
                addTask,
                removeTask,
                updateTask,
                refreshTaskTree,
                activeTypeFilters,
                setActiveTypeFilters,
                activeAssigneeFilters,
                setActiveAssigneeFilters,
                assignees,
                filteredTasks,
            }}
        >
            {children}
        </WorkContext.Provider>
    );
};
