import { IconButton } from "@chakra-ui/react";
import { FaArrowUpRightFromSquare } from "react-icons/fa6";

export interface DetailItemButtonProps {
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

export const DetailItemButton = ({
    "aria-label": ariaLabel,
    onClick,
    position = { bottom: 2, right: 2 },
    size = "sm",
    zIndex = 2,
}: DetailItemButtonProps) => {
    return (
        <IconButton
            aria-label={ariaLabel}
            cursor="pointer"
            size={size}
            bg="transparent"
            color="rgba(0,0,0,0.25)"
            variant="solid"
            position="absolute"
            top={position.top}
            right={position.right}
            bottom={position.bottom}
            left={position.left}
            zIndex={zIndex}
            onClick={onClick}
            opacity={0.9}
            _hover={{
                opacity: 1,
                transform: "scale(1.3)",
                bg: "rgba(0,0,0,0.25)",
                color: "white",
                transition: "all 0.2s ease-in-out",
            }}
        >
            <FaArrowUpRightFromSquare />
        </IconButton>
    );
};

export default DetailItemButton;

