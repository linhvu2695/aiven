import { IconButton } from "@chakra-ui/react";
import { FaTrash } from "react-icons/fa";

export interface DeleteItemButtonProps {
    /** Label for accessibility */
    "aria-label": string;
    /** Function to call when button is clicked */
    onClick: (e?: React.MouseEvent<HTMLButtonElement>) => void;
    /** Position of the button (absolute positioning) */
    position?: {
        top?: number;
        right?: number;
        bottom?: number;
        left?: number;
    };
    /** Size of the button */
    size?: "xs" | "sm" | "md" | "lg";
    /** z-index for layering */
    zIndex?: number;
}

export const DeleteItemButton = ({
    "aria-label": ariaLabel,
    onClick,
    position = { top: 2, right: 2 },
    size = "sm",
    zIndex = 2,
}: DeleteItemButtonProps) => {
    return (
        <IconButton
            aria-label={ariaLabel}
            cursor="pointer"
            size={size}
            bg="transparent"
            colorScheme="red"
            position="absolute"
            top={position.top}
            right={position.right}
            bottom={position.bottom}
            left={position.left}
            zIndex={zIndex}
            onClick={onClick}
            _hover={{
                transform: "scale(1.3)",
                bg: "red.500",
                color: "white",
                boxShadow: "0 0 0 4px rgba(229,62,62,0.2)",
                transition: "all 0.15s cubic-bezier(.4,0,.2,1)",
            }}
        >
            <FaTrash />
        </IconButton>
    );
};

export default DeleteItemButton;
