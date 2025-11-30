import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import type { ChatMessageInfo } from "@/components/chat/chat-message-info";

type AgentEvalContextType = {
    messages: ChatMessageInfo[];
    addMessage: (content: string, role: "user" | "assistant") => void;
    resetMessages: () => void;
    selectedRole: "user" | "assistant";
    setSelectedRole: (role: "user" | "assistant") => void;
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
    };

    return (
        <AgentEvalContext.Provider
            value={{
                messages,
                addMessage,
                resetMessages,
                selectedRole,
                setSelectedRole,
            }}
        >
            {children}
        </AgentEvalContext.Provider>
    );
};

