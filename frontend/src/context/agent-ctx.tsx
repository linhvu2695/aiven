import { createContext, useContext, useState, type ReactNode } from "react";

export type Agent = {
  id: string;
  name: string;
  description: string;
  model: string;
  persona: string;
  tone: string;
};

type AgentContextType = {
  agent: Agent | null;
  setAgent: (agent: Agent) => void;
};

const AgentContext = createContext<AgentContextType | undefined>(undefined);

export const useAgent = () => {
  const context = useContext(AgentContext);
  if (!context) {
    throw new Error("useAgent must be used within an AgentProvider");
  }
  return context;
};

export const AgentProvider = ({ children }: { children: ReactNode }) => {
  const [agent, setAgent] = useState<Agent | null>(null);

  return (
    <AgentContext.Provider value={{ agent, setAgent }}>
      {children}
    </AgentContext.Provider>
  );
};