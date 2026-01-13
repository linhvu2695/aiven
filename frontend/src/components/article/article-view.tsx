import {
    Box,
    VStack,
    Text,
    Flex,
    Textarea,
    Heading,
    Link,
    Code,
} from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useArticle } from "@/context/article-ctx";
import { ArticleViewHeader } from "./article-view-header";

interface ArticleViewProps {
    onSave: () => void;
    onCancel: () => void;
}

export const ArticleView = ({
    onSave,
    onCancel,
}: ArticleViewProps) => {
    const { selectedArticle: article, articleDraft, mode, updateArticleDraft } = useArticle();

    if (!article) {
        return (
            <Flex h="full" align="center" justify="center">
                <VStack gap={4} textAlign="center">
                    <Text fontSize="lg" color="gray.500">
                        Select an article from the tree to view its content
                    </Text>
                    <Text fontSize="sm" color="gray.400">
                        Or create a new article using the + button
                    </Text>
                </VStack>
            </Flex>
        );
    }

    return (
        <VStack h="full" gap={0} align="stretch">
            <ArticleViewHeader onSave={onSave} onCancel={onCancel} />

            {/* Article Content */}
            <Box flex={1} p={6} overflow="auto">
                {mode === "edit" ? (
                    <Textarea
                        placeholder="Write your article content here... (Markdown supported)"
                        value={articleDraft?.content || ""}
                        onChange={(e) => updateArticleDraft("content", e.target.value)}
                        h="full"
                        minH="300px"
                        resize="none"
                        fontSize="sm"
                        lineHeight="1.6"
                        fontFamily="mono"
                        borderColor="gray.300"
                        _dark={{ borderColor: "gray.600", bg: "gray.800" }}
                        _focus={{ borderColor: "blue.400", boxShadow: "0 0 0 1px var(--chakra-colors-blue-400)" }}
                    />
                ) : (
                    <Box
                        className="markdown-content"
                        fontSize="md"
                        lineHeight="1.8"
                        color="gray.800"
                        _dark={{ color: "gray.200" }}
                        css={{
                            "& > *:first-child": { marginTop: 0 },
                            "& > *:last-child": { marginBottom: 0 },
                        }}
                    >
                        {article.content ? (
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                    h1: ({ children }) => (
                                        <Heading as="h1" size="2xl" mt={6} mb={4} borderBottom="1px solid" borderColor="gray.200" pb={2} _dark={{ borderColor: "gray.700" }}>
                                            {children}
                                        </Heading>
                                    ),
                                    h2: ({ children }) => (
                                        <Heading as="h2" size="xl" mt={5} mb={3} borderBottom="1px solid" borderColor="gray.200" pb={2} _dark={{ borderColor: "gray.700" }}>
                                            {children}
                                        </Heading>
                                    ),
                                    h3: ({ children }) => (
                                        <Heading as="h3" size="lg" mt={4} mb={2}>
                                            {children}
                                        </Heading>
                                    ),
                                    h4: ({ children }) => (
                                        <Heading as="h4" size="md" mt={3} mb={2}>
                                            {children}
                                        </Heading>
                                    ),
                                    p: ({ children }) => (
                                        <Text mb={4} lineHeight="1.8">
                                            {children}
                                        </Text>
                                    ),
                                    a: ({ href, children }) => (
                                        <Link href={href} color="blue.500" _hover={{ textDecoration: "underline" }} target="_blank" rel="noopener noreferrer">
                                            {children}
                                        </Link>
                                    ),
                                    ul: ({ children }) => (
                                        <Box as="ul" pl={6} mb={4} listStyleType="disc">
                                            {children}
                                        </Box>
                                    ),
                                    ol: ({ children }) => (
                                        <Box as="ol" pl={6} mb={4} listStyleType="decimal">
                                            {children}
                                        </Box>
                                    ),
                                    li: ({ children }) => (
                                        <Box as="li" mb={1}>
                                            {children}
                                        </Box>
                                    ),
                                    blockquote: ({ children }) => (
                                        <Box
                                            as="blockquote"
                                            pl={4}
                                            borderLeft="4px solid"
                                            borderColor="blue.400"
                                            color="gray.600"
                                            _dark={{ color: "gray.400" }}
                                            fontStyle="italic"
                                            my={4}
                                        >
                                            {children}
                                        </Box>
                                    ),
                                    code: ({ children, className }) => {
                                        const isInline = !className;
                                        if (isInline) {
                                            return (
                                                <Code
                                                    px={1.5}
                                                    py={0.5}
                                                    bg="gray.100"
                                                    _dark={{ bg: "gray.700" }}
                                                    borderRadius="md"
                                                    fontSize="sm"
                                                >
                                                    {children}
                                                </Code>
                                            );
                                        }
                                        return (
                                            <Box
                                                as="pre"
                                                p={4}
                                                bg="gray.900"
                                                color="gray.100"
                                                borderRadius="md"
                                                overflowX="auto"
                                                my={4}
                                                fontSize="sm"
                                                fontFamily="mono"
                                            >
                                                <code>{children}</code>
                                            </Box>
                                        );
                                    },
                                    hr: () => (
                                        <Box as="hr" my={6} borderColor="gray.300" _dark={{ borderColor: "gray.600" }} />
                                    ),
                                    table: ({ children }) => (
                                        <Box my={4} overflowX="auto" w="full">
                                            <Box
                                                as="table"
                                                w="full"
                                                borderCollapse="collapse"
                                                border="1px solid"
                                                borderColor="gray.300"
                                                _dark={{ borderColor: "gray.600" }}
                                                borderRadius="md"
                                                overflow="hidden"
                                                minW="full"
                                            >
                                                {children}
                                            </Box>
                                        </Box>
                                    ),
                                    thead: ({ children }) => (
                                        <Box as="thead" bg="gray.100" _dark={{ bg: "gray.700" }}>
                                            {children}
                                        </Box>
                                    ),
                                    tbody: ({ children }) => (
                                        <Box as="tbody">
                                            {children}
                                        </Box>
                                    ),
                                    tr: ({ children }) => (
                                        <Box
                                            as="tr"
                                            borderBottom="1px solid"
                                            borderColor="gray.300"
                                            _dark={{ borderColor: "gray.600" }}
                                            _last={{ borderBottom: "none" }}
                                        >
                                            {children}
                                        </Box>
                                    ),
                                    th: ({ children }) => (
                                        <Box
                                            as="th"
                                            px={4}
                                            py={2}
                                            textAlign="left"
                                            fontWeight="semibold"
                                            borderRight="1px solid"
                                            borderColor="gray.300"
                                            _dark={{ borderColor: "gray.600" }}
                                            _last={{ borderRight: "none" }}
                                        >
                                            {children}
                                        </Box>
                                    ),
                                    td: ({ children }) => (
                                        <Box
                                            as="td"
                                            px={4}
                                            py={2}
                                            borderRight="1px solid"
                                            borderColor="gray.300"
                                            _dark={{ borderColor: "gray.600" }}
                                            _last={{ borderRight: "none" }}
                                        >
                                            {children}
                                        </Box>
                                    ),
                                }}
                            >
                                {article.content}
                            </ReactMarkdown>
                        ) : (
                            <Text color="gray.500">No content available.</Text>
                        )}
                    </Box>
                )}
            </Box>
        </VStack>
    );
}; 