import { 
    Text, 
    Card,
    Grid,
    GridItem
} from "@chakra-ui/react";

interface StatCardProps {
    value: number;
    label: string;
    color: string;
}

const StatCard = ({ value, label, color }: StatCardProps) => (
    <GridItem>
        <Card.Root>
            <Card.Body textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color={color}>
                    {value}
                </Text>
                <Text fontSize="sm" color="fg.muted">
                    {label}
                </Text>
            </Card.Body>
        </Card.Root>
    </GridItem>
);

export const PlantStats = () => {
    const stats = [
        { value: 0, label: "Total Plants", color: "green.500" },
        { value: 0, label: "Need Watering", color: "blue.500" },
        { value: 0, label: "Need Attention", color: "yellow.500" }
    ];

    return (
        <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
            {stats.map((stat) => (
                <StatCard 
                    key={stat.label}
                    value={stat.value}
                    label={stat.label}
                    color={stat.color}
                />
            ))}
        </Grid>
    );
};

export default PlantStats;
