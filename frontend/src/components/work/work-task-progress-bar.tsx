import { Box, HStack, Text } from "@chakra-ui/react";
import { useColorModeValue } from "../ui/color-mode";
import { formatMinutes } from "./work-utils";

/** Max width (px) that a progress bar can occupy */
const BAR_MAX_W = 200;

interface WorkTaskProgressBarProps {
    spent: number;
    left: number;
    maxTime: number;
    scaleMode: "linear" | "log";
}

export const WorkTaskProgressBar = ({
    spent,
    left,
    maxTime,
    scaleMode,
}: WorkTaskProgressBarProps) => {
    const color = useColorModeValue("green.600", "green.400");
    const total = spent + left;
    if (total === 0) return null;

    // Scale bar width based on selected mode
    const barW = scaleMode === "log"
        ? Math.max((Math.log1p(total) / Math.log1p(maxTime)) * BAR_MAX_W, 4)
        : Math.max((total / maxTime) * BAR_MAX_W, 4);
    const spentPct = (spent / total) * 100;

    return (
        <HStack gap={2} flexShrink={0} w={`${BAR_MAX_W}px`} justify="flex-end" align="center">
            {/* Time label */}
            {left === 0 ? (
                <Text fontSize="2xs" whiteSpace="nowrap" color={color} fontWeight="bold">
                    {formatMinutes(total)}
                </Text>
            ) : (
                <Text fontSize="2xs" whiteSpace="nowrap">
                    <Text as="span" color={color}>{formatMinutes(spent)}</Text>
                    <Text as="span" color="fg.muted"> / {formatMinutes(total)}</Text>
                </Text>
            )}

            {/* Bar */}
            <Box
                w={`${barW}px`}
                h="8px"
                borderRadius="full"
                bg="gray.600"
                overflow="hidden"
                flexShrink={0}
            >
                <Box
                    h="full"
                    w={`${spentPct}%`}
                    borderRadius="full"
                    bg={color}
                    transition="width 0.3s"
                />
            </Box>
        </HStack>
    );
};
