import { 
    Text, 
    Card,
    Grid,
    GridItem
} from "@chakra-ui/react";
import type { PlantInfoWithImage } from "@/types/plant";
import { PlantHealthStatus } from "@/types/plant";

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

interface PlantStatsProps {
    plants?: PlantInfoWithImage[];
}

const calculateWateringNeeds = (plants: PlantInfoWithImage[]): number => {
    const now = new Date();
    
    return plants.filter(plant => {
        if (!plant.last_watered || !plant.watering_frequency_days) {
            return false;
        }
        
        const lastWatered = new Date(plant.last_watered);
        const daysSinceWatered = Math.floor((now.getTime() - lastWatered.getTime()) / (1000 * 60 * 60 * 24));
        
        return daysSinceWatered >= plant.watering_frequency_days;
    }).length;
};

const calculateAttentionNeeded = (plants: PlantInfoWithImage[]): number => {
    return plants.filter(plant => 
        plant.current_health_status === PlantHealthStatus.POOR || 
        plant.current_health_status === PlantHealthStatus.CRITICAL
    ).length;
};

export const PlantStats = ({ plants = [] }: PlantStatsProps) => {
    const totalPlants = plants.length;
    const needWatering = calculateWateringNeeds(plants);
    const needAttention = calculateAttentionNeeded(plants);

    const stats = [
        { value: totalPlants, label: "Total Plants", color: "green.500" },
        { value: needWatering, label: "Need Watering", color: "blue.500" },
        { value: needAttention, label: "Need Attention", color: "yellow.500" }
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
