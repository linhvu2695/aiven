import { createContext, useContext, useState, type ReactNode } from "react";

type ChatModelContextType = {
  chatModel: string | null;
  setChatModel: (model: string) => void;
};

const ChatModelContext = createContext<ChatModelContextType | undefined>(undefined);

export const useChatModel = () => {
  const context = useContext(ChatModelContext);
  if (!context) {
    throw new Error("useModel must be used within a ModelProvider");
  }
  return context;
};

export const ChatModelProvider = ({ children }: { children: ReactNode }) => {
  const [chatModel, setChatModel] = useState<string | null>(null);

  return (
    <ChatModelContext.Provider value={{ chatModel, setChatModel }}>
      {children}
    </ChatModelContext.Provider>
  );
};