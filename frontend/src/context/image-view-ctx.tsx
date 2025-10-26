import { createContext, useContext, useState, type ReactNode } from "react";

export enum ViewMode {
    SIMPLE = "simple",
    DETAIL = "detail"
}

type ImageViewContextType = {
    pageSize: number;
    setPageSize: (size: number) => void;
    viewMode: ViewMode;
    setViewMode: (mode: ViewMode) => void;
    isViewDialogOpen: boolean;
    openViewDialog: () => void;
    closeViewDialog: () => void;
};

const ImageViewContext = createContext<ImageViewContextType | undefined>(undefined);

export const useImageView = () => {
    const context = useContext(ImageViewContext);
    if (!context) {
        throw new Error("useImageView must be used within an ImageViewProvider");
    }
    return context;
};

export const ImageViewProvider = ({ children }: { children: ReactNode }) => {
    const [pageSize, setPageSize] = useState(10);
    const [viewMode, setViewMode] = useState<ViewMode>(ViewMode.SIMPLE);
    const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);

    const openViewDialog = () => {
        setIsViewDialogOpen(true);
    };

    const closeViewDialog = () => {
        setIsViewDialogOpen(false);
    };

    return (
        <ImageViewContext.Provider value={{ 
            pageSize,
            setPageSize,
            viewMode,
            setViewMode,
            isViewDialogOpen,
            openViewDialog,
            closeViewDialog
        }}>
            {children}
        </ImageViewContext.Provider>
    );
};

