import { IconButton, ButtonGroup } from "@chakra-ui/react";
import { FaChartBar, FaColumns } from "react-icons/fa";
import { Tooltip } from "@/components/ui/tooltip";
import { useTeamContext } from "@/context/team-ctx";

export const MemberBarChartModeSelector = () => {
    const { chartMode, setChartMode } = useTeamContext();

    return (
        <ButtonGroup size="xs" variant="outline">
            <Tooltip content="Single chart view (two separate charts)">
                <IconButton
                    aria-label="Single chart view"
                    variant={chartMode === "single" ? "solid" : "outline"}
                    onClick={() => setChartMode("single")}
                >
                    <FaColumns />
                </IconButton>
            </Tooltip>
            <Tooltip content="Dual chart view (grouped bars)">
                <IconButton
                    aria-label="Dual chart view"
                    variant={chartMode === "dual" ? "solid" : "outline"}
                    onClick={() => setChartMode("dual")}
                >
                    <FaChartBar />
                </IconButton>
            </Tooltip>
        </ButtonGroup>
    );
};
