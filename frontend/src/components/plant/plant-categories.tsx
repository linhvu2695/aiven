import { 
    Box, 
    Heading, 
    Text, 
    Card,
    VStack
} from "@chakra-ui/react";

interface CategoryCardProps {
    title: string;
    count: number;
}

const CategoryCard = ({ title, count }: CategoryCardProps) => (
    <Card.Root size="sm">
        <Card.Body>
            <VStack align="start" gap={1}>
                <Text fontWeight="semibold">{title}</Text>
                <Text fontSize="sm" color="fg.muted">{count} plants</Text>
            </VStack>
        </Card.Body>
    </Card.Root>
);

export const PlantCategories = () => {
    const categories = [
        { title: "Indoor Plants", count: 0 },
        { title: "Outdoor Plants", count: 0 },
        { title: "Succulents", count: 0 },
        { title: "Herbs", count: 0 }
    ];

    return (
        <Box 
            as="aside" 
            w="300px" 
            minW="300px"
            h="100%"
            borderRadius="md"
            border="1px"
            borderColor="border.default"
            bg="bg.subtle"
        >
            <VStack p={4} align="stretch" gap={3}>
                <Heading size="md" color="fg.default">Categories</Heading>
                
                {categories.map((category) => (
                    <CategoryCard 
                        key={category.title}
                        title={category.title}
                        count={category.count}
                    />
                ))}
            </VStack>
        </Box>
    );
};

export default PlantCategories;
