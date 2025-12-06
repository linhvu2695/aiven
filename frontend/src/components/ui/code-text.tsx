import { Box, type BoxProps } from "@chakra-ui/react";
import { forwardRef } from "react";

export interface CodeTextProps extends Omit<BoxProps, "as"> {
    children: React.ReactNode;
}

export const CodeText = forwardRef<HTMLDivElement, CodeTextProps>(
    ({ children, ...props }, ref) => {
        return (
            <Box
                ref={ref}
                as="code"
                px={2}
                py={1}
                bg="gray.100"
                color="gray.800"
                borderRadius="md"
                fontFamily="mono"
                fontSize="sm"
                fontWeight="semibold"
                _dark={{
                    bg: "gray.800",
                    color: "gray.100",
                }}
                {...props}
            >
                {children}
            </Box>
        );
    }
);

CodeText.displayName = "CodeText";

