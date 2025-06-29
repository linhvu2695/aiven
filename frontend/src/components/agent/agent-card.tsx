import {
    Avatar,
    Card,
    Field,
    Separator,
    Textarea,
    VStack,
    HStack,
    Button,
    Text,
    Input,
} from "@chakra-ui/react";
import { ModelSelector } from "./model-selector";
import { useAgent, type Agent } from "@/context/agent-ctx";
import { useState } from "react";
import { BASE_URL } from "@/App";

const missingAgentFieldWarning = (field: string) => (
    <span style={{ color: "#888" }}>No {field} set.</span>
);

export const AgentCard = () => {
    const { agent, setAgent, agentDraft, setAgentDraft, updateAgentDraft } = useAgent();
    const [isEditing, setIsEditing] = useState(false);

    const handleSaveAgent = async () => {
        if (agentDraft) {
            try {
                const response = await fetch(BASE_URL + "/api/agent/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(agentDraft),
                });
                if (!response.ok) {
                    throw new Error("Failed to connect to server");
                }

                const data = await response.json();
                if (data.success) {
                    setAgent(agentDraft);
                }
                
                setIsEditing(false);
            } catch (error) {
                console.error("Error saving agent:", error);
            }
        }
    };

    return (
        <Card.Root>
            {/* Header */}
            <Card.Header flexDir={"row"} spaceX={5}>
                <Avatar.Root size="2xl" shape="rounded">
                    <Avatar.Image src={"/dinosaur.jpg"} />
                    <Avatar.Fallback name={agent?.name} />
                </Avatar.Root>
                <VStack align="flex-start">
                    {/* Name */}
                    {isEditing ? (
                        <Input
                            value={agentDraft?.name || ""}
                            placeholder="Agent name"
                            size="lg"
                            fontWeight="bold"
                            onChange={(e) =>
                                updateAgentDraft("name", e.target.value)
                            }
                        />
                    ) : (
                        <Card.Title mt={2} fontSize={"2xl"}>
                            {agentDraft?.name}
                        </Card.Title>
                    )}
                    <Card.Description fontSize={"x-small"}>
                        {agentDraft?.model}
                    </Card.Description>
                </VStack>
            </Card.Header>

            {/* Body */}
            <Card.Body spaceY={2}>
                {/* Description */}
                {isEditing ? (
                    <Input
                        value={agentDraft?.description || ""}
                        placeholder="Agent description"
                        size="sm"
                        fontSize="xs"
                        mt={1}
                        onChange={(e) =>
                            updateAgentDraft("description", e.target.value)
                        }
                    />
                ) : (
                    <Card.Description fontSize={"x-small"}>
                        {agentDraft?.description}
                    </Card.Description>
                )}

                <ModelSelector />

                <Separator />

                {/* Persona */}
                <Field.Root required={isEditing}>
                    <Field.Label>
                        Persona <Field.RequiredIndicator />
                    </Field.Label>
                    {isEditing ? (
                        <>
                            <Textarea
                                value={agentDraft?.persona}
                                placeholder="You are a helpful AI Assistant..."
                                variant="subtle"
                                onChange={(e) =>
                                    updateAgentDraft("persona", e.target.value)
                                }
                            />
                            <Field.HelperText>
                                Max 500 characters.
                            </Field.HelperText>
                        </>
                    ) : (
                        <Text
                            whiteSpace="pre-line"
                            minH="48px"
                            maxH="160px"
                            overflowY="auto"
                            p={2}
                            borderRadius="md"
                            fontSize={"sm"}
                        >
                            {agentDraft?.persona ||
                                missingAgentFieldWarning("persona")}
                        </Text>
                    )}
                </Field.Root>

                {/* Tone */}
                <Field.Root required={isEditing}>
                    <Field.Label>
                        Tone <Field.RequiredIndicator />
                    </Field.Label>
                    {isEditing ? (
                        <>
                            <Textarea
                                value={agentDraft?.tone}
                                placeholder="Be polite and humorous..."
                                variant="subtle"
                                onChange={(e) =>
                                    updateAgentDraft("tone", e.target.value)
                                }
                            />
                            <Field.HelperText>
                                Max 200 characters.
                            </Field.HelperText>
                        </>
                    ) : (
                        <Text
                            whiteSpace="pre-line"
                            minH="48px"
                            maxH="160px"
                            overflowY="auto"
                            p={2}
                            borderRadius="md"
                            fontSize={"sm"}
                        >
                            {agentDraft?.tone ||
                                missingAgentFieldWarning("tone")}
                        </Text>
                    )}
                </Field.Root>
            </Card.Body>

            <Card.Footer>
                {/* Action Buttons */}
                <HStack
                    justifyContent="flex-end"
                    width="100%"
                    spaceX={4}
                    mt={4}
                >
                    {/* Edit */}
                    <Button
                        variant="outline"
                        colorScheme="gray"
                        bgColor={isEditing ? "teal" : ""}
                        onClick={() => setIsEditing(true)}
                    >
                        Edit
                    </Button>

                    {/* Cancel */}
                    <Button
                        variant="outline"
                        colorScheme="gray"
                        disabled={!isEditing}
                        onClick={() => {
                            setIsEditing(false);
                            setAgentDraft(agent);
                        }}
                    >
                        Cancel
                    </Button>

                    {/* Save */}
                    <Button
                        colorScheme="teal"
                        variant="solid"
                        onClick={handleSaveAgent}
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
            </Card.Footer>
        </Card.Root>
    );
};
