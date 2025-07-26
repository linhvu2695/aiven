import { createContext, useContext, useState, type ReactNode } from "react";
import type { ChatMessageInfo } from "@/components/chat/chat-message-info";

type ChatContextType = {
    messages: ChatMessageInfo[];
    setMessages: React.Dispatch<React.SetStateAction<ChatMessageInfo[]>>;
    resetMessages: () => void;
};

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChat = () => {
    const context = useContext(ChatContext);
    if (!context) {
        throw new Error("useChat must be used within a ChatProvider");
    }
    return context;
};

export const ChatProvider = ({ children }: { children: ReactNode }) => {
    const baseMessage = { role: "assistant", content: "Hello. What can I do for you?" };
    const [messages, setMessages] = useState<ChatMessageInfo[]>([
        baseMessage,
    ]);

    const resetMessages = () => {
        setMessages([
            baseMessage,
        ]);
    };

    return (
        <ChatContext.Provider value={{ messages, setMessages, resetMessages }}>
            {children}
        </ChatContext.Provider>
    );
};
