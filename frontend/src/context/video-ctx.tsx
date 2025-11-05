import { createContext, useContext, useState, type ReactNode } from "react";
import type { VideoWithUrl } from "@/types/video";

type VideoContextType = {
    selectedVideo: VideoWithUrl | null;
    setSelectedVideo: (video: VideoWithUrl | null) => void;
    isDialogOpen: boolean;
    openVideoDialog: (video: VideoWithUrl) => void;
    closeVideoDialog: () => void;
};

const VideoContext = createContext<VideoContextType | undefined>(undefined);

export const useVideo = () => {
    const context = useContext(VideoContext);
    if (!context) {
        throw new Error("useVideo must be used within a VideoProvider");
    }
    return context;
};

export const VideoProvider = ({ children }: { children: ReactNode }) => {
    const [selectedVideo, setSelectedVideo] = useState<VideoWithUrl | null>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    const openVideoDialog = (video: VideoWithUrl) => {
        setSelectedVideo(video);
        setIsDialogOpen(true);
    };

    const closeVideoDialog = () => {
        setIsDialogOpen(false);
        setSelectedVideo(null);
    };

    return (
        <VideoContext.Provider value={{ 
            selectedVideo, 
            setSelectedVideo,
            isDialogOpen,
            openVideoDialog,
            closeVideoDialog
        }}>
            {children}
        </VideoContext.Provider>
    );
};

