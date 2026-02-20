import { Box, HStack, Text, Input } from "@chakra-ui/react";
import { useCallback, useState } from "react";
import { Dropdown } from "./dropdown";

export const formatDateForInput = (d: Date) => d.toISOString().slice(0, 10);

export type DatePresetKey =
    | "today"
    | "yesterday"
    | "this_week"
    | "last_week"
    | "this_month"
    | "last_month"
    | "last_7_days"
    | "last_30_days"
    | "last_90_days";

const getPresetDateRange = (key: DatePresetKey): { start: string; end: string } => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const format = formatDateForInput;

    switch (key) {
        case "today": {
            return { start: format(today), end: format(today) };
        }
        case "yesterday": {
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);
            return { start: format(yesterday), end: format(yesterday) };
        }
        case "this_week": {
            const d = new Date(today);
            const day = d.getDay();
            const diff = day === 0 ? 6 : day - 1;
            d.setDate(d.getDate() - diff);
            return { start: format(d), end: format(today) };
        }
        case "last_week": {
            const d = new Date(today);
            const day = d.getDay();
            const diff = day === 0 ? 6 : day - 1;
            d.setDate(d.getDate() - diff - 7);
            const start = new Date(d);
            const end = new Date(d);
            end.setDate(end.getDate() + 6);
            return { start: format(start), end: format(end) };
        }
        case "this_month": {
            const start = new Date(today.getFullYear(), today.getMonth(), 1);
            return { start: format(start), end: format(today) };
        }
        case "last_month": {
            const start = new Date(today.getFullYear(), today.getMonth() - 1, 1);
            const end = new Date(today.getFullYear(), today.getMonth(), 0);
            return { start: format(start), end: format(end) };
        }
        case "last_7_days": {
            const start = new Date(today);
            start.setDate(start.getDate() - 6);
            return { start: format(start), end: format(today) };
        }
        case "last_30_days": {
            const start = new Date(today);
            start.setDate(start.getDate() - 29);
            return { start: format(start), end: format(today) };
        }
        case "last_90_days": {
            const start = new Date(today);
            start.setDate(start.getDate() - 89);
            return { start: format(start), end: format(today) };
        }
    }
};

const DATE_PRESET_OPTIONS: { value: DatePresetKey; label: string }[] = [
    { value: "today", label: "Today" },
    { value: "yesterday", label: "Yesterday" },
    { value: "this_week", label: "This week" },
    { value: "last_week", label: "Last week" },
    { value: "this_month", label: "This month" },
    { value: "last_month", label: "Last month" },
    { value: "last_7_days", label: "Most recent 7 days" },
    { value: "last_30_days", label: "Most recent 30 days" },
    { value: "last_90_days", label: "Most recent 90 days" },
];

export interface DateRangeSelectorProps {
    startDate: string;
    endDate: string;
    onStartDateChange: (date: string) => void;
    onEndDateChange: (date: string) => void;
    onPresetSelect?: (start: string, end: string) => void;
    children?: React.ReactNode;
}

export const DateRangeSelector = ({
    startDate,
    endDate,
    onStartDateChange,
    onEndDateChange,
    onPresetSelect,
    children,
}: DateRangeSelectorProps) => {
    const [datePreset, setDatePreset] = useState<string>("");
    const today = new Date();
    const maxDate = formatDateForInput(today);

    const handlePresetSelect = useCallback(
        (presetKey: string) => {
            if (!presetKey) return;
            const key = presetKey as DatePresetKey;
            const { start, end } = getPresetDateRange(key);
            onStartDateChange(start);
            onEndDateChange(end);
            setDatePreset(key);
            onPresetSelect?.(start, end);
        },
        [onStartDateChange, onEndDateChange, onPresetSelect]
    );

    const handleStartDateChange = useCallback(
        (value: string) => {
            onStartDateChange(value);
            setDatePreset("");
        },
        [onStartDateChange]
    );

    const handleEndDateChange = useCallback(
        (value: string) => {
            onEndDateChange(value);
            setDatePreset("");
        },
        [onEndDateChange]
    );

    return (
        <Box
            p={4}
            borderRadius="lg"
            borderWidth="1px"
            borderColor="border.default"
            bg="bg.subtle"
        >
            <HStack gap={4} flexWrap="wrap" align="flex-end">
                <Box minW="180px">
                    <Text fontSize="xs" color="fg.muted" mb={1}>
                        Quick select
                    </Text>
                    <Dropdown
                        value={datePreset}
                        onValueChange={handlePresetSelect}
                        options={DATE_PRESET_OPTIONS}
                        placeholder="Presets..."
                        mb={0}
                    />
                </Box>
                <Box flex={1} minW="140px">
                    <Text fontSize="xs" color="fg.muted" mb={1}>
                        From
                    </Text>
                    <Input
                        type="date"
                        value={startDate}
                        onChange={(e) => handleStartDateChange(e.target.value)}
                        size="lg"
                        max={endDate}
                    />
                </Box>
                <Box flex={1} minW="140px">
                    <Text fontSize="xs" color="fg.muted" mb={1}>
                        To
                    </Text>
                    <Input
                        type="date"
                        value={endDate}
                        onChange={(e) => handleEndDateChange(e.target.value)}
                        size="lg"
                        min={startDate}
                        max={maxDate}
                    />
                </Box>
                {children}
            </HStack>
        </Box>
    );
};
