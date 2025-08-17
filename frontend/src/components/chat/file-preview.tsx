import React from "react";

export interface FilePreviewProps {
    // Frontend file handling
    file?: File | null;
    filePreview?: string | null;
    
    // Backend file handling
    imageData?: string | null;
    mimeType?: string | null;
}

// Handles file preview for backend messages with base64 data and MIME types
const BackendFilePreview = ({ 
    imageData, 
    mimeType 
}: { 
    imageData: string; 
    mimeType: string; 
}) => {
    const dataUrl = imageData.startsWith('data:') 
        ? imageData 
        : `data:${mimeType};base64,${imageData}`;
    
    if (mimeType.startsWith("image/")) {
        return (
            <img
                src={dataUrl}
                alt="Uploaded image"
                style={{ maxWidth: "200px", borderRadius: 8 }}
                onError={(e) => {
                    console.error("Backend image failed to load:", dataUrl);
                    e.currentTarget.style.display = "none";
                }}
            />
        );
    }
    
    if (mimeType.startsWith("audio/")) {
        return (
            <audio 
                controls 
                src={dataUrl} 
                style={{ maxWidth: "200px" }} 
            />
        );
    }
    
    if (mimeType === "application/pdf") {
        return (
            <a
                href={dataUrl}
                target="_blank"
                rel="noopener noreferrer"
            >
                📄 Document
            </a>
        );
    }
    
    return <span>📎 File ({mimeType})</span>;
};

// Handles file preview for frontend messages with File objects
const FrontendFilePreview = ({ 
    file, 
    filePreview 
}: { 
    file: File; 
    filePreview?: string | null; 
}) => {
    const previewUrl = filePreview || 
        (file.type.startsWith("image/") ? URL.createObjectURL(file) : null);

    if (file.type.startsWith("image/")) {
        return previewUrl ? (
            <img
                src={previewUrl}
                alt={file.name}
                style={{ maxWidth: "200px", borderRadius: 8 }}
                onError={(e) => {
                    console.error("Frontend image failed to load:", previewUrl);
                    e.currentTarget.style.display = "none";
                }}
            />
        ) : (
            <span>🖼️ {file.name}</span>
        );
    }

    if (file.type.startsWith("audio/")) {
        return previewUrl ? (
            <audio 
                controls 
                src={previewUrl} 
                style={{ maxWidth: "200px" }} 
            />
        ) : (
            <span>🎵 {file.name}</span>
        );
    }

    if (file.type === "application/pdf") {
        return (
            <a
                href={previewUrl || "#"}
                target="_blank"
                rel="noopener noreferrer"
            >
                📄 {file.name}
            </a>
        );
    }

    return <span>📎 {file.name}</span>;
};

// Main FilePreview component that handles both frontend and backend file formats
export const FilePreview: React.FC<FilePreviewProps> = ({
    file,
    filePreview,
    imageData,
    mimeType,
}) => {
    // Backend message handling - has priority if both are present
    if (imageData && mimeType) {
        return (
            <BackendFilePreview 
                imageData={imageData} 
                mimeType={mimeType} 
            />
        );
    }

    // Frontend message handling
    if (file) {
        return (
            <FrontendFilePreview 
                file={file} 
                filePreview={filePreview} 
            />
        );
    }

    // No file content
    return <span>📎 No file</span>;
};
