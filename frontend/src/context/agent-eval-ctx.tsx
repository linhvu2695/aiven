import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import type { ChatMessageInfo } from "@/components/chat/chat-message-info";
import type { Agent } from "./agent-ctx";
import type { MCPFunction } from "@/components/agent/agent-eval/agent-eval-trajectory-match";

export type TrajectoryMatch = "strict" | "unordered" | "superset" | "subset";
export type ToolArgsMatch = "ignore" | "exact" | "superset" | "subset";

export interface ExpectedFunctionCall {
    id: string;
    function: MCPFunction;
    expectedInput: Record<string, any>;
    expectedOutput: Record<string, any>;
}

type AgentEvalContextType = {
    messages: ChatMessageInfo[];
    setMessages: (messages: ChatMessageInfo[]) => void;
    addMessage: (content: string, role: "user" | "assistant") => void;
    resetMessages: () => void;
    selectedRole: "user" | "assistant";
    setSelectedRole: (role: "user" | "assistant") => void;
    judgeAgent: Agent | null;
    setJudgeAgent: (agent: Agent | null) => void;
    trajectoryMatch: TrajectoryMatch;
    setTrajectoryMatch: (match: TrajectoryMatch) => void;
    toolArgsMatch: ToolArgsMatch;
    setToolArgsMatch: (match: ToolArgsMatch) => void;
    expectedFunctionCalls: ExpectedFunctionCall[];
    setExpectedFunctionCalls: (calls: ExpectedFunctionCall[]) => void;
};

const AgentEvalContext = createContext<AgentEvalContextType | undefined>(undefined);

export const useAgentEval = () => {
    const context = useContext(AgentEvalContext);
    if (!context) {
        throw new Error("useAgentEval must be used within an AgentEvalProvider");
    }
    return context;
};

export const AgentEvalProvider = ({ children }: { children: ReactNode }) => {
    const [messages, setMessages] = useState<ChatMessageInfo[]>([
        {
            content: "Hello, how are you?",
            role: "user",
        },
        {
            content: "I'm good, thank you! How can I help you today?",
            role: "assistant",
        },
    ]);
    const [selectedRole, setSelectedRole] = useState<"user" | "assistant">("user");
    const [judgeAgent, setJudgeAgent] = useState<Agent | null>(null);
    const [trajectoryMatch, setTrajectoryMatch] = useState<TrajectoryMatch>("strict");
    const [toolArgsMatch, setToolArgsMatch] = useState<ToolArgsMatch>("ignore");
    const [expectedFunctionCalls, setExpectedFunctionCalls] = useState<ExpectedFunctionCall[]>([]);

    // Update selectedRole when messages updated (default behavior)
    useEffect(() => {
        const lastRole = messages.length > 0 ? messages[messages.length - 1].role : "assistant";
        const nextDefaultRole = lastRole === "user" ? "assistant" : "user";
        setSelectedRole(nextDefaultRole);
    }, [messages.length]);

    const addMessage = (content: string, role: "user" | "assistant") => {
        const newMessage: ChatMessageInfo = {
            content: content.trim(),
            role,
        };
        setMessages((prev) => [...prev, newMessage]);
    };

    const resetMessages = () => {
        setMessages([
            {
                content: "Hello, how are you?",
                role: "user",
            },
            {
                content: "I'm good, thank you! How can I help you today?",
                role: "assistant",
            },
        ]);
        setExpectedFunctionCalls([]);
    };

    return (
        <AgentEvalContext.Provider
            value={{
                messages,
                setMessages,
                addMessage,
                resetMessages,
                selectedRole,
                setSelectedRole,
                judgeAgent,
                setJudgeAgent,
                trajectoryMatch,
                setTrajectoryMatch,
                toolArgsMatch,
                setToolArgsMatch,
                expectedFunctionCalls,
                setExpectedFunctionCalls,
            }}
        >
            {children}
        </AgentEvalContext.Provider>
    );
};

