import { Container, Text } from "@chakra-ui/react"

export const AgentEvalContainer = () => {
    return (
        <Container
            height="100%"
            display="flex"
            flexDirection="column"
            justifyContent="space-between"
            data-testid="agent-eval-container"
        >
            <Text>Agent Evaluation</Text>
        </Container>
    );
};