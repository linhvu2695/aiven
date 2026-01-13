import { createContext, useContext, useState, useCallback, useRef, type ReactNode } from "react";
import type { ImageWithUrl } from "@/types/image";

type ImageContextType = {
    selectedImage: ImageWithUrl | null;
    setSelectedImage: (image: ImageWithUrl | null) => void;
    isDialogOpen: boolean;
    openImageDialog: (image: ImageWithUrl) => void;
    closeImageDialog: () => void;
    isGenDialogOpen: boolean;
    setIsGenDialogOpen: (isOpen: boolean) => void;
    registerRefreshCallback: (callback: () => void) => void;
    refreshImages: () => void;
};

const ImageContext = createContext<ImageContextType | undefined>(undefined);

export const useImage = () => {
    const context = useContext(ImageContext);
    if (!context) {
        throw new Error("useImage must be used within an ImageProvider");
    }
    return context;
};

export const ImageProvider = ({ children }: { children: ReactNode }) => {
    const [selectedImage, setSelectedImage] = useState<ImageWithUrl | null>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isGenDialogOpen, setIsGenDialogOpen] = useState(false);
    const refreshCallbackRef = useRef<(() => void) | null>(null);

    const openImageDialog = (image: ImageWithUrl) => {
        setSelectedImage(image);
        setIsDialogOpen(true);
    };

    const closeImageDialog = () => {
        setIsDialogOpen(false);
        setSelectedImage(null);
    };

    const registerRefreshCallback = useCallback((callback: () => void) => {
        refreshCallbackRef.current = callback;
    }, []);

    const refreshImages = useCallback(() => {
        if (refreshCallbackRef.current) {
            refreshCallbackRef.current();
        }
    }, []);

    return (
        <ImageContext.Provider value={{ 
            selectedImage, 
            setSelectedImage,
            isDialogOpen,
            openImageDialog,
            closeImageDialog,
            isGenDialogOpen,
            setIsGenDialogOpen,
            registerRefreshCallback,
            refreshImages
        }}>
            {children}
        </ImageContext.Provider>
    );
};

