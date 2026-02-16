import { Box, VStack, Text } from "@chakra-ui/react";
import { Chart, useChart } from "@chakra-ui/charts";
import { PieChart, Pie, Cell, Tooltip as ReTooltip } from "recharts";

export interface DonutChartEntry {
    name: string;
    value: number;
    label: string;
    color: string;
}

export interface DonutChartProps {
    data: DonutChartEntry[];
    chartHook: ReturnType<typeof useChart<{ name: string; value: number; label: string; color: `${string}.${string}` }>>;
    total: number;
    centerLabel: string;
    centerSublabel: string;
    size?: number;
    innerRadius?: number;
    outerRadius?: number;
}

export const DonutChart = ({
    data,
    chartHook,
    total,
    centerLabel,
    centerSublabel,
    size = 280,
    innerRadius = 70,
    outerRadius = 110,
}: DonutChartProps) => (
    <Box position="relative" flexShrink={0} w={`${size}px`} h={`${size}px`}>
        <Chart.Root chart={chartHook} maxW={`${size}px`} position="relative" zIndex={1}>
            <PieChart width={size} height={size}>
                <Pie
                    data={data}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={innerRadius}
                    outerRadius={outerRadius}
                    strokeWidth={1.5}
                    isAnimationActive
                >
                    {data.map((entry) => (
                        <Cell key={entry.name} fill={chartHook.color(entry.color)} />
                    ))}
                </Pie>
                <ReTooltip
                    content={({ payload }) => {
                        if (!payload?.length) return null;
                        const item = payload[0].payload as DonutChartEntry;
                        const pct = Math.round((item.value / total) * 100);
                        return (
                            <Box
                                bg="bg.panel"
                                borderWidth="1px"
                                borderColor="border.default"
                                borderRadius="md"
                                px={3}
                                py={2}
                                shadow="md"
                            >
                                <Text fontSize="xs" fontWeight="bold">{item.name}</Text>
                                <Text fontSize="xs" color="fg.muted">
                                    {item.label} ({pct}%)
                                </Text>
                            </Box>
                        );
                    }}
                />
            </PieChart>
        </Chart.Root>
        <VStack
            position="absolute"
            top="40%"
            left="50%"
            transform="translate(-50%, -50%)"
            gap={0}
            pointerEvents="none"
            textAlign="center"
            zIndex={0}
        >
            <Text fontSize="lg" fontWeight="bold" lineHeight="1.2">{centerLabel}</Text>
            <Text fontSize="2xs" color="fg.muted">{centerSublabel}</Text>
        </VStack>
    </Box>
);
