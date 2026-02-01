import { useEffect, useState, useId } from "react";
import { Box, Spinner, Text } from "@chakra-ui/react";
import mermaid from "mermaid";

// Initialize mermaid with dark theme support
mermaid.initialize({
    startOnLoad: false,
    theme: "dark",
    securityLevel: "loose",
    fontFamily: "inherit",
    flowchart: {
        htmlLabels: true,
        useMaxWidth: true,
    },
});

interface MermaidRendererProps {
    chart: string;
}

export const MermaidRenderer = ({ chart }: MermaidRendererProps) => {
    const [svg, setSvg] = useState<string>("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const id = useId().replace(/:/g, "");

    useEffect(() => {
        if (!chart) {
            setLoading(false);
            setError("No chart content provided");
            return;
        }

        let isMounted = true;
        let isCompleted = false;
        const timeoutId = setTimeout(() => {
            if (isMounted && !isCompleted) {
                setError("Diagram rendering timed out");
                setLoading(false);
            }
        }, 10000); // 10 second timeout

        const renderChart = async () => {
            try {
                // Clean up the chart content - remove HTML entities that might cause issues
                const cleanedChart = chart
                    .replace(/&lt;/g, "<")
                    .replace(/&gt;/g, ">")
                    .replace(/&amp;/g, "&");

                const uniqueId = `mermaid-${id}-${Math.random().toString(36).substr(2, 9)}`;
                const { svg: renderedSvg } = await mermaid.render(uniqueId, cleanedChart);
                
                isCompleted = true;
                if (isMounted) {
                    setSvg(renderedSvg);
                    setLoading(false);
                }
            } catch (err) {
                console.error("Mermaid rendering error:", err);
                isCompleted = true;
                if (isMounted) {
                    setError(err instanceof Error ? err.message : "Failed to render diagram");
                    setLoading(false);
                }
            }
        };

        renderChart();

        return () => {
            isMounted = false;
            clearTimeout(timeoutId);
        };
    }, [chart, id]);

    if (loading) {
        return (
            <Box
                p={4}
                bg="gray.800"
                borderRadius="md"
                my={4}
                display="flex"
                alignItems="center"
                justifyContent="center"
                minH="100px"
            >
                <Spinner size="md" color="blue.400" />
            </Box>
        );
    }

    if (error) {
        return (
            <Box
                p={4}
                bg="red.900"
                borderRadius="md"
                my={4}
                border="1px solid"
                borderColor="red.600"
            >
                <Text color="red.300" fontSize="sm" fontFamily="mono">
                    Mermaid Error: {error}
                </Text>
                <Box
                    as="pre"
                    mt={2}
                    p={2}
                    bg="gray.900"
                    borderRadius="md"
                    fontSize="xs"
                    overflowX="auto"
                    color="gray.400"
                    whiteSpace="pre-wrap"
                    wordBreak="break-word"
                >
                    {chart}
                </Box>
            </Box>
        );
    }

    return (
        <Box
            my={4}
            p={4}
            bg="gray.800"
            borderRadius="md"
            overflowX="auto"
            css={{
                "& svg": {
                    maxWidth: "100%",
                    height: "auto",
                },
            }}
            dangerouslySetInnerHTML={{ __html: svg }}
        />
    );
};
