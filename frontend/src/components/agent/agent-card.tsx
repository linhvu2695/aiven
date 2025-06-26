import { Avatar, Card } from "@chakra-ui/react";
import { ModelSelector } from "./model-selector";

interface AgentCardProps {
    name: string;
    description: string;
    avatarUrl: string;
}

export const AgentCard = ({ name, description, avatarUrl }: AgentCardProps) => {
    

    return (
        <Card.Root>
            {/* Header */}
            <Card.Header flexDir={"row"} spaceX={5}>
                <Avatar.Root size="lg" shape="rounded">
                    <Avatar.Image src={avatarUrl} />
                    <Avatar.Fallback name={name} />
                </Avatar.Root>
                <Card.Title mt={2} fontSize={"2xl"}>
                    {name}
                </Card.Title>
            </Card.Header>

            {/* Body */}
            <Card.Body spaceY={2}>
                <Card.Description>{description}</Card.Description>

                <ModelSelector />
            </Card.Body>
        </Card.Root>
    );
};
