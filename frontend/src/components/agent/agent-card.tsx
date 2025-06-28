import {
    Avatar,
    Card,
    Field,
    Separator,
    Textarea,
    VStack,
    HStack,
    Button,
} from "@chakra-ui/react";
import { ModelSelector } from "./model-selector";
import { useAgent } from "@/context/agent-ctx";

export const AgentCard = () => {
    const { agent, setAgent } = useAgent();

    return (
        <Card.Root>
            {/* Header */}
            <Card.Header flexDir={"row"} spaceX={5}>
                <Avatar.Root size="2xl" shape="rounded">
                    <Avatar.Image src={"/dinosaur.jpg"} />
                    <Avatar.Fallback name={agent?.name} />
                </Avatar.Root>
                <VStack align="flex-start">
                    <Card.Title mt={2} fontSize={"2xl"}>
                        {agent?.name}
                    </Card.Title>
                    <Card.Description fontSize={"x-small"}>
                        {agent?.model}
                    </Card.Description>
                </VStack>
            </Card.Header>

            {/* Body */}
            <Card.Body spaceY={2}>
                <Card.Description>{agent?.description}</Card.Description>

                <ModelSelector />

                <Separator />

                <Field.Root required>
                    <Field.Label>
                        Persona <Field.RequiredIndicator />
                    </Field.Label>
                    <Textarea
                        value={agent?.persona}
                        placeholder="You are a helpful AI Assistant..."
                        variant="subtle"
                    />
                    <Field.HelperText>Max 500 characters.</Field.HelperText>
                </Field.Root>

                <Field.Root>
                    <Field.Label>
                        Tone <Field.RequiredIndicator />
                    </Field.Label>
                    <Textarea
                        value={agent?.tone}
                        placeholder="Be polite and humorous..."
                        variant="subtle"
                    />
                </Field.Root>

                {/* Action Buttons */}
                <HStack
                    justifyContent="flex-end"
                    width="100%"
                    spaceX={4}
                    mt={4}
                >
                    <Button variant="outline" colorScheme="gray">
                        Cancel
                    </Button>
                    <Button
                        colorScheme="teal"
                        variant="solid"
                        transition="all 0.3s ease"
                        _hover={{
                            transform: "scale(1.1)",
                            bgColor: "teal.500",
                            boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
                        }}
                    >
                        Save
                    </Button>
                </HStack>
            </Card.Body>
        </Card.Root>
    );
};
