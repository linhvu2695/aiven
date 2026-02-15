import { Box, HStack, Text } from "@chakra-ui/react";
import { useColorModeValue } from "../ui/color-mode";
import { formatMinutes, ACCENT_COLOR } from "./work-utils";

/** Max width (px) that a progress bar can occupy */
const BAR_MAX_W = 400;

interface WorkTaskProgressBarProps {
    spent: number;
    left: number;
    maxTime: number;
}

export const WorkTaskProgressBar = ({
    spent,
    left,
    maxTime,
}: WorkTaskProgressBarProps) => {
    const color = useColorModeValue(ACCENT_COLOR.light, ACCENT_COLOR.dark);
    const total = spent + left;
    if (total === 0) return null;

    const barW = Math.min(Math.max((total / maxTime) * BAR_MAX_W, 2), BAR_MAX_W);
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
