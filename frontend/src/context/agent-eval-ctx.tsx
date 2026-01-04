import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import type { ChatMessageInfo } from "@/components/chat/chat-message-info";

export interface MCPFunction {
    name: string;
    description: string | null;
    inputSchema: Record<string, any> | null;
    outputSchema: Record<string, any> | null;
}

export type TrajectoryMatch = "strict" | "unordered" | "superset" | "subset";
export type ToolArgsMatch = "ignore" | "exact" | "superset" | "subset";

export interface ExpectedFunctionCall {
    id: string;
    function: MCPFunction;
    expectedInput: Record<string, any>;
    expectedOutput: Record<string, any>;
}

export interface EvalResult {
    success: boolean;
    score: boolean; // True if trajectory matches, False otherwise
    key: string; // Evaluation key (e.g., "trajectory_strict_match")
    comment?: string; // Optional comment from evaluator
    actual_trajectory: Array<{
        role: string;
        content: string;
        tool_calls?: Array<{
            function: {
                name: string;
                arguments: string;
            };
        }>;
    }>;
    message: string;
}

type AgentEvalContextType = {
    messages: ChatMessageInfo[];
    setMessages: (messages: ChatMessageInfo[]) => void;
    addMessage: (content: string, role: "user" | "assistant") => void;
    resetMessages: () => void;
    selectedRole: "user" | "assistant";
    setSelectedRole: (role: "user" | "assistant") => void;
    llmAsJudge: boolean;
    setLlmAsJudge: (llmAsJudge: boolean) => void;
    trajectoryMatch: TrajectoryMatch;
    setTrajectoryMatch: (match: TrajectoryMatch) => void;
    toolArgsMatch: ToolArgsMatch;
    setToolArgsMatch: (match: ToolArgsMatch) => void;
    expectedFunctionCalls: ExpectedFunctionCall[];
    setExpectedFunctionCalls: (calls: ExpectedFunctionCall[]) => void;
    evalResult: EvalResult | null;
    setEvalResult: (result: EvalResult | null) => void;
};

const AgentEvalContext = createContext<AgentEvalContextType | undefined>(undefined);

const DEFAULT_MESSAGES = [
    {
        content: "Hello, how are you?",
        role: "user",
    }
];

export const useAgentEval = () => {
    const context = useContext(AgentEvalContext);
    if (!context) {
        throw new Error("useAgentEval must be used within an AgentEvalProvider");
    }
    return context;
};

export const AgentEvalProvider = ({ children }: { children: ReactNode }) => {
    const [messages, setMessages] = useState<ChatMessageInfo[]>(DEFAULT_MESSAGES);
    const [selectedRole, setSelectedRole] = useState<"user" | "assistant">("user");
    const [llmAsJudge, setLlmAsJudge] = useState<boolean>(false);
    const [trajectoryMatch, setTrajectoryMatch] = useState<TrajectoryMatch>("strict");
    const [toolArgsMatch, setToolArgsMatch] = useState<ToolArgsMatch>("ignore");
    const [expectedFunctionCalls, setExpectedFunctionCalls] = useState<ExpectedFunctionCall[]>([]);
    const [evalResult, setEvalResult] = useState<EvalResult | null>(null);

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
        setMessages(DEFAULT_MESSAGES);
        setExpectedFunctionCalls([]);
        setEvalResult(null);
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
                llmAsJudge,
                setLlmAsJudge,
                trajectoryMatch,
                setTrajectoryMatch,
                toolArgsMatch,
                setToolArgsMatch,
                expectedFunctionCalls,
                setExpectedFunctionCalls,
                evalResult,
                setEvalResult,
            }}
        >
            {children}
        </AgentEvalContext.Provider>
    );
};

