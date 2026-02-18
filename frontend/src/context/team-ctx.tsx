import { createContext, useContext, useState, type ReactNode } from "react";

interface TeamContextValue {
    selectedMember: string | null;
    setSelectedMember: (name: string | null) => void;
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

    return (
        <TeamContext.Provider value={{ selectedMember, setSelectedMember }}>
            {children}
        </TeamContext.Provider>
    );
};
