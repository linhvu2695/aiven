import { Container } from "@chakra-ui/react";
import { AgentCard } from "./agent-card";

export const AgentContainer = () => {
    return (
        <Container margin={4}>
            <AgentCard />
        </Container>
    );
};
