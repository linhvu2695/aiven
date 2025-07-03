import { createContext, useContext, useState, type ReactNode } from "react";

export type Agent = {
  id: string;
  name: string;
  description: string;
  avatar: string;
  model: string;
  persona: string;
  tone: string;
};

type AgentContextType = {
  agent: Agent | null;
  setAgent: (agent: Agent) => void;
  agentDraft: Agent | null;
  setAgentDraft: (agent: Agent | null) => void;
  updateAgentDraft: <K extends keyof Agent>(field: K, value: Agent[K]) => void;
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
  const [agentDraft, setAgentDraft] = useState<Agent | null>(null);

  const updateAgentDraft = <K extends keyof Agent>(field: K, value: Agent[K]) => {
    setAgentDraft((prev) =>
      prev ? { ...prev, [field]: value } : null
    );
  };

  return (
    <AgentContext.Provider value={{ agent, setAgent, agentDraft, setAgentDraft, updateAgentDraft }}>
      {children}
    </AgentContext.Provider>
  );
};