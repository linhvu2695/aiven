import { Container } from "@chakra-ui/react";
import { AgentCard } from "./agent-card";

export const AgentContainer = () => {
    return (
        <Container margin={4}>
            <AgentCard name="Anonymous" description="You can't see me" avatarUrl="/anonymous.webp"/>
        </Container>
    );
};
