import { createContext, useContext, useState, type ReactNode } from "react";
import { ASPECT_RATIO_OPTIONS } from "@/types/image";

interface ImageGenContextType {
    prompt: string;
    setPrompt: (prompt: string) => void;
    aspectRatio: string;
    setAspectRatio: (ratio: string) => void;
    provider: string;
    setProvider: (provider: string) => void;
    model: string;
    setModel: (model: string) => void;
    isGenerating: boolean;
    setIsGenerating: (generating: boolean) => void;
    resetState: () => void;
}

const ImageGenContext = createContext<ImageGenContextType | undefined>(undefined);

export const useImageGen = () => {
    const context = useContext(ImageGenContext);
    if (!context) {
        throw new Error("useImageGen must be used within ImageGenProvider");
    }
    return context;
};

interface ImageGenProviderProps {
    children: ReactNode;
}

export const ImageGenProvider = ({ children }: ImageGenProviderProps) => {
    const [prompt, setPrompt] = useState("");
    const [aspectRatio, setAspectRatio] = useState(ASPECT_RATIO_OPTIONS[0].value);
    const [provider, setProvider] = useState("google_genai");
    const [model, setModel] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);

    const resetState = () => {
        setPrompt("");
        setAspectRatio(ASPECT_RATIO_OPTIONS[0].value);
        setProvider("google_genai");
        setModel("");
        setIsGenerating(false);
    };

    return (
        <ImageGenContext.Provider
            value={{
                prompt,
                setPrompt,
                aspectRatio,
                setAspectRatio,
                provider,
                setProvider,
                model,
                setModel,
                isGenerating,
                setIsGenerating,
                resetState,
            }}
        >
            {children}
        </ImageGenContext.Provider>
    );
};

