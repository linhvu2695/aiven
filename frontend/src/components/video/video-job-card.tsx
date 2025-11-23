import {
    Box,
    Card,
    HStack,
    VStack,
    Text,
    Badge,
} from "@chakra-ui/react";
import { 
    FaCheck, 
    FaSpinner, 
    FaExclamationTriangle,
    FaClock,
    FaRedo,
    FaBan,
    FaHourglassHalf
} from "react-icons/fa";
import type { JobInfo, JobType } from "@/types/job";
import { FaEllipsis } from "react-icons/fa6";

interface VideoJobCardProps {
    job: JobInfo;
}

export const VideoJobCard = ({ job }: VideoJobCardProps) => {
    const getStatusColor = (status: string) => {
        switch (status) {
            case "pending":
                return "gray";
            case "started":
            case "progress":
                return "blue";
            case "success":
                return "green";
            case "failure":
                return "red";
            case "cancelled":
                return "orange";
            case "retry":
                return "yellow";
            default:
                return "gray";
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "pending":
                return <FaClock />;
            case "started":
                return <FaEllipsis />;
            case "progress":
                return <FaSpinner />;
            case "retry":
                return <FaRedo />;
            case "success":
                return <FaCheck />;
            case "failure":
                return <FaExclamationTriangle />;
            case "cancelled":
                return <FaBan />;
            case "expired":
                return <FaHourglassHalf />;
            default:
                return null;
        }
    };

    const getProgressPercentage = () => {
        if (!job.progress || job.progress.total === 0) return 0;
        return Math.round((job.progress.current / job.progress.total) * 100);
    };

    const getProgressMessage = () => {
        if (job.progress?.message) return job.progress.message;
        if (job.progress && job.progress.total > 0) {
            return `${job.progress.current} / ${job.progress.total}`;
        }
        return job.status;
    };

    const formatTime = (dateString?: string) => {
        if (!dateString) return "";
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);

        if (diffSecs < 60) return `${diffSecs}s ago`;
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return date.toLocaleDateString();
    };

    const formatJobType = (jobType: JobType) => {
        return jobType
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    };

    return (
        <Card.Root size="sm" variant="outline" w="280px">
            <Card.Body p={3}>
                <VStack align="stretch" gap={2}>
                    {/* Header */}
                    <HStack gap={2}>
                        <Box color={`${getStatusColor(job.status)}.500`}>
                            {getStatusIcon(job.status)}
                        </Box>
                        <Badge colorPalette={getStatusColor(job.status)} size="sm">
                            {job.status}
                        </Badge>
                    </HStack>

                    {/* Job Name */}
                    <Text fontSize="sm" fontWeight="medium" lineClamp={2}>
                        {formatJobType(job.job_type)}
                    </Text>

                    {/* Progress */}
                    {(job.status === "progress" || job.status === "started") && (
                        <Box>
                            <Box
                                w="100%"
                                h="6px"
                                bg="gray.200"
                                borderRadius="full"
                                overflow="hidden"
                                _dark={{ bg: "gray.700" }}
                            >
                                <Box
                                    h="100%"
                                    w={`${getProgressPercentage()}%`}
                                    bg="blue.500"
                                    transition="width 0.3s ease"
                                />
                            </Box>
                            <Text fontSize="xs" color="gray.500" mt={1}>
                                {getProgressMessage()}
                            </Text>
                        </Box>
                    )}

                    {/* Metadata */}
                    {job.metadata?.prompt && (
                        <Text fontSize="xs" color="gray.600" lineClamp={2}>
                            {job.metadata.prompt}
                        </Text>
                    )}

                    {/* Result Message for completed jobs */}
                    {job.result?.message && (
                        <Text 
                            fontSize="xs" 
                            color={job.result.success ? "green.600" : "red.600"}
                            lineClamp={2}
                        >
                            {job.result.message}
                        </Text>
                    )}

                    {/* Time */}
                    <Text fontSize="xs" color="gray.500">
                        {formatTime(job.started_at || job.created_at)}
                    </Text>
                </VStack>
            </Card.Body>
        </Card.Root>
    );
};

