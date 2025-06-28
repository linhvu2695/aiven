import { Avatar, Card, VStack } from "@chakra-ui/react";
import { ModelSelector } from "./model-selector";
import { useChatModel } from "@/context/chat-model-ctx";

interface AgentCardProps {
    name: string;
    description: string;
    avatarUrl: string;
}

export const AgentCard = ({ name, description, avatarUrl }: AgentCardProps) => {
    const { chatModel, setChatModel } = useChatModel();

    return (
        <Card.Root>
            {/* Header */}
            <Card.Header flexDir={"row"} spaceX={5}>
                <Avatar.Root size="2xl" shape="rounded">
                    <Avatar.Image src={avatarUrl} />
                    <Avatar.Fallback name={name} />
                </Avatar.Root>
                <VStack align="flex-start">
                    <Card.Title mt={2} fontSize={"2xl"}>
                        {name}
                    </Card.Title>
                    <Card.Description fontSize={"x-small"}>{chatModel}</Card.Description>
                </VStack>
            </Card.Header>

            {/* Body */}
            <Card.Body spaceY={2}>
                <Card.Description>{description}</Card.Description>

                <ModelSelector />
            </Card.Body>
        </Card.Root>
    );
};
