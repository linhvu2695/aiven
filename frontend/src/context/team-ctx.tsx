import { createContext, useContext, useState, type ReactNode } from "react";

export type MemberBarChartMode = "single" | "dual";

interface TeamContextValue {
    selectedMember: string | null;
    setSelectedMember: (name: string | null) => void;
    chartMode: MemberBarChartMode;
    setChartMode: (mode: MemberBarChartMode) => void;
}

const TeamContext = createContext<TeamContextValue | null>(null);

export const useTeamContext = (): TeamContextValue => {
    const ctx = useContext(TeamContext);
    if (!ctx) {
        throw new Error("useTeamContext must be used within a TeamProvider");
    }
    return ctx;
};

export const TeamProvider = ({ children }: { children: ReactNode }) => {
    const [selectedMember, setSelectedMember] = useState<string | null>(null);
    const [chartMode, setChartMode] = useState<MemberBarChartMode>("dual");

    return (
        <TeamContext.Provider value={{ selectedMember, setSelectedMember, chartMode, setChartMode }}>
            {children}
        </TeamContext.Provider>
    );
};
