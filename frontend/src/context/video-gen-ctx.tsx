import { createContext, useContext, useState, type ReactNode } from "react";

interface VideoGenContextType {
    prompt: string;
    setPrompt: (prompt: string) => void;
    imageId: string | null;
    setImageId: (id: string | null) => void;
    aspectRatio: string;
    setAspectRatio: (ratio: string) => void;
    duration: number;
    setDuration: (duration: number) => void;
    provider: string;
    setProvider: (provider: string) => void;
    model: string;
    setModel: (model: string) => void;
    isGenerating: boolean;
    setIsGenerating: (generating: boolean) => void;
    resetState: () => void;
}

const VideoGenContext = createContext<VideoGenContextType | undefined>(undefined);

export const useVideoGen = () => {
    const context = useContext(VideoGenContext);
    if (!context) {
        throw new Error("useVideoGen must be used within VideoGenProvider");
    }
    return context;
};

interface VideoGenProviderProps {
    children: ReactNode;
}

const VIDEO_ASPECT_RATIO_DEFAULT = "9:16";
const VIDEO_DURATION_DEFAULT = 4;

export const VideoGenProvider = ({ children }: VideoGenProviderProps) => {
    const [prompt, setPrompt] = useState("");
    const [imageId, setImageId] = useState<string | null>(null);
    const [aspectRatio, setAspectRatio] = useState(VIDEO_ASPECT_RATIO_DEFAULT);
    const [duration, setDuration] = useState(VIDEO_DURATION_DEFAULT);
    const [provider, setProvider] = useState("openai");
    const [model, setModel] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);

    const resetState = () => {
        setPrompt("");
        setImageId(null);
        setAspectRatio(VIDEO_ASPECT_RATIO_DEFAULT);
        setDuration(VIDEO_DURATION_DEFAULT);
        setProvider("openai");
        setModel("");
        setIsGenerating(false);
    };

    return (
        <VideoGenContext.Provider
            value={{
                prompt,
                setPrompt,
                imageId,
                setImageId,
                aspectRatio,
                setAspectRatio,
                duration,
                setDuration,
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
        </VideoGenContext.Provider>
    );
};

