import { BASE_URL } from "@/App";
import {
    Box,
    HStack,
    Text,
    IconButton,
    Flex,
    Spinner,
    Center,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { FaChevronDown, FaChevronUp, FaSync, FaArrowLeft, FaArrowRight } from "react-icons/fa";
import type { JobInfo, JobListResponse } from "@/types/job";
import { ACTIVE_JOB_STATUSES, COMPLETED_JOB_STATUSES } from "@/types/job";
import { VideoJobCard } from "./video-job-card";
import { toaster } from "@/components/ui/toaster";
import { Tooltip, useColorMode } from "@/components/ui";

const RECENT_JOB_THRESHOLD_MINUTES = 30*24*60; // 24 hours
const PAGE_SIZE = 7;

export const VideoJobsPanel = () => {
    const [jobs, setJobs] = useState<JobInfo[]>([]);
    const { colorMode } = useColorMode();
    const [loading, setLoading] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalJobs, setTotalJobs] = useState(0);

    const fetchJobs = async (page: number = currentPage) => {
        try {
            setLoading(true);
            const response = await fetch(`${BASE_URL}/api/job/list`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    job_type: "video_generation",
                    page: page,
                    page_size: PAGE_SIZE,
                }),
            });

            if (!response.ok) throw new Error("Failed to fetch jobs");

            const data: JobListResponse = await response.json();
            
            // Filter to show only active or recently completed jobs
            const activeJobs = data.jobs.filter(job => 
                ACTIVE_JOB_STATUSES.includes(job.status) ||
                (COMPLETED_JOB_STATUSES.includes(job.status) && 
                 isRecentlyCompleted(job))
            );

            setJobs(activeJobs);
            setTotalJobs(data.total);
            setCurrentPage(data.page);
        } catch (error) {
            console.error("Error fetching jobs:", error);
            toaster.create({
                description: "Failed to load jobs",
                type: "error",
            });
        } finally {
            setLoading(false);
        }
    };

    const isRecentlyCompleted = (job: JobInfo): boolean => {
        if (!job.completed_at) return false;
        const completedDate = new Date(job.completed_at);
        const now = new Date();
        const diffMinutes = (now.getTime() - completedDate.getTime()) / 1000 / 60;
        return diffMinutes < RECENT_JOB_THRESHOLD_MINUTES;
    };

    useEffect(() => {
        fetchJobs(currentPage);
    }, [currentPage]);

    // Auto-refresh every 5 seconds when there are active jobs
    useEffect(() => {
        const hasActiveJobs = jobs.some(job => 
            ACTIVE_JOB_STATUSES.includes(job.status)
        );

        if (hasActiveJobs) {
            const interval = setInterval(() => {
                fetchJobs(currentPage);
            }, 5000);

            return () => clearInterval(interval);
        }
    }, [jobs, currentPage]);

    const activeJobsCount = jobs.filter(job => 
        ACTIVE_JOB_STATUSES.includes(job.status)
    ).length;

    const totalPages = Math.ceil(totalJobs / PAGE_SIZE);

    const handlePreviousPage = () => {
        if (currentPage > 1) {
            setCurrentPage(currentPage - 1);
        }
    };

    const handleNextPage = () => {
        if (currentPage < totalPages) {
            setCurrentPage(currentPage + 1);
        }
    };

    if (jobs.length === 0 && !loading) return null;

    return (
        <Box
            position="fixed"
            bottom={0}
            left={0}
            right={0}
            bg={colorMode === "dark" ? "gray.800" : "white"}
            borderTop="1px solid"
            borderColor={colorMode === "dark" ? "gray.700" : "gray.200"}
            shadow="lg"
            zIndex={10}
        >
            {/* Header */}
            <HStack
                p={3}
                justify="space-between"
                cursor="pointer"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <HStack gap={2}>
                    <IconButton
                        aria-label={isExpanded ? "Collapse" : "Expand"}
                        size="sm"
                        variant="ghost"
                        onClick={(e) => {
                            e.stopPropagation();
                            setIsExpanded(!isExpanded);
                        }}
                    >
                        {isExpanded ? <FaChevronDown /> : <FaChevronUp />}
                    </IconButton>
                    <Text fontSize="sm" fontWeight="semibold">
                        Video Generation Jobs
                    </Text>
                    {activeJobsCount > 0 && (
                        <Box
                            bg="blue.500"
                            color="white"
                            borderRadius="full"
                            px={2}
                            py={0.5}
                            fontSize="xs"
                            fontWeight="bold"
                        >
                            {activeJobsCount}
                        </Box>
                    )}
                </HStack>

                <HStack gap={2} onClick={(e) => e.stopPropagation()}>
                    {/* Pagination Controls */}
                    {!loading && totalJobs > 0 && (
                        <HStack gap={1}>
                            <IconButton
                                onClick={handlePreviousPage}
                                disabled={currentPage === 1}
                                variant="ghost"
                                size="sm"
                                aria-label="Previous page"
                            >
                                <FaArrowLeft />
                            </IconButton>
                            <HStack gap={1}>
                                <Text fontSize="xs" fontWeight="medium">
                                    Page {currentPage} of {totalPages}
                                </Text>
                                <Text fontSize="xs" color="gray.500">
                                    ({totalJobs})
                                </Text>
                            </HStack>
                            <IconButton
                                onClick={handleNextPage}
                                disabled={currentPage >= totalPages}
                                variant="ghost"
                                size="sm"
                                aria-label="Next page"
                            >
                                <FaArrowRight />
                            </IconButton>
                        </HStack>
                    )}
                    <Tooltip content="Refresh">
                        <IconButton
                            aria-label="Refresh jobs"
                            size="sm"
                            variant="ghost"
                            onClick={(e) => {
                                e.stopPropagation();
                                fetchJobs(currentPage);
                            }}
                            disabled={loading}
                        >
                            <FaSync className={loading ? "animate-spin" : ""} />
                        </IconButton>
                    </Tooltip>
                </HStack>
            </HStack>

            {/* Content */}
            {isExpanded && (
                <Box
                    maxH="300px"
                    overflowY="auto"
                    overflowX="auto"
                    p={3}
                    pt={0}
                >
                    {loading && jobs.length === 0 ? (
                        <Center py={8}>
                            <Spinner size="md" color="primary.500" />
                        </Center>
                    ) : (
                        <Flex gap={3} wrap="nowrap">
                            {jobs.map((job) => (
                                <VideoJobCard
                                    key={job.id}
                                    job={job}
                                />
                            ))}
                        </Flex>
                    )}
                </Box>
            )}
        </Box>
    );
};

