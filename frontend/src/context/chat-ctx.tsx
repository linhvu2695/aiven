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
    const [messages, setMessages] = useState<ChatMessageInfo[]>([]);

    const resetMessages = () => {
        setMessages([]);
    };

    return (
        <ChatContext.Provider value={{ messages, setMessages, resetMessages }}>
            {children}
        </ChatContext.Provider>
    );
};
