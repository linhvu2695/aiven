import { PlantHealthStatus, PlantSpecies, LightRequirement, HumidityPreference } from "@/types/plant";
import { 
    FaTree, 
    FaLeaf, 
    FaAppleAlt,
    FaSeedling
} from "react-icons/fa";
import { 
    GiCactus,
    GiFlowerPot,
    GiFern,
    GiGrass,
    GiFlowers,
    GiPalmTree,
} from "react-icons/gi";
import { IoFlower } from "react-icons/io5";

export const getHealthStatusColor = (status: PlantHealthStatus): string => {
    switch (status) {
        case PlantHealthStatus.EXCELLENT:
            return "green";
        case PlantHealthStatus.GOOD:
            return "primary";
        case PlantHealthStatus.FAIR:
            return "yellow";
        case PlantHealthStatus.POOR:
            return "orange";
        case PlantHealthStatus.CRITICAL:
            return "red";
        default:
            return "gray";
    }
};

export const formatSpeciesLabel = (species: PlantSpecies | PlantHealthStatus | LightRequirement | HumidityPreference): string => {
    return species.charAt(0).toUpperCase() + species.slice(1).replace('_', ' ');
};

export const getSpeciesIcon = (species: PlantSpecies) => {
    switch (species) {
        case PlantSpecies.CACTUS:
            return <GiCactus color="green.600" size={16} />;
        case PlantSpecies.SUCCULENT:
            return <GiFlowerPot color="var(--chakra-colors-primary-500)" size={16} />;
        case PlantSpecies.FLOWERING:
            return <IoFlower color="pink.500" size={16} />;
        case PlantSpecies.TROPICAL:
            return <GiPalmTree color="emerald.500" size={16} />;
        case PlantSpecies.HERB:
            return <GiGrass color="green.500" size={16} />;
        case PlantSpecies.FERN:
            return <GiFern color="green.400" size={16} />;
        case PlantSpecies.TREE:
            return <FaTree color="brown.500" size={16} />;
        case PlantSpecies.VEGETABLE:
            return <FaLeaf color="orange.500" size={16} />;
        case PlantSpecies.FRUIT:
            return <FaAppleAlt color="red.500" size={16} />;
        case PlantSpecies.ORCHID:
            return <GiFlowers color="purple.500" size={16} />;
        case PlantSpecies.OTHER:
        default:
            return <FaSeedling color="green.500" size={16} />;
    }
};
