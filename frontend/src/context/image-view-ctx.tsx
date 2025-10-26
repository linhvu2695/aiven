import { createContext, useContext, useState, type ReactNode } from "react";

export enum ViewMode {
    SIMPLE = "simple",
    DETAIL = "detail"
}

export enum ViewRatio {
    PORTRAIT = "portrait",
    SQUARE = "square",
    LANDSCAPE = "landscape"
}

const VIEW_RATIO_SIZES: Record<ViewRatio, number> = {
    [ViewRatio.PORTRAIT]: 200,
    [ViewRatio.SQUARE]: 300,
    [ViewRatio.LANDSCAPE]: 400
};

type ImageViewContextType = {
    pageSize: number;
    setPageSize: (size: number) => void;
    viewMode: ViewMode;
    setViewMode: (mode: ViewMode) => void;
    viewRatio: ViewRatio;
    setViewRatio: (ratio: ViewRatio) => void;
    getViewRatioSize: () => number;
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
    const [viewRatio, setViewRatio] = useState<ViewRatio>(ViewRatio.SQUARE);
    const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);

    const openViewDialog = () => {
        setIsViewDialogOpen(true);
    };

    const closeViewDialog = () => {
        setIsViewDialogOpen(false);
    };

    const getViewRatioSize = () => {
        return VIEW_RATIO_SIZES[viewRatio];
    };

    return (
        <ImageViewContext.Provider value={{ 
            pageSize,
            setPageSize,
            viewMode,
            setViewMode,
            viewRatio,
            setViewRatio,
            getViewRatioSize,
            isViewDialogOpen,
            openViewDialog,
            closeViewDialog
        }}>
            {children}
        </ImageViewContext.Provider>
    );
};

