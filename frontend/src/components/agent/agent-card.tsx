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
    IconButton,
    Spinner,
    Box,
    Badge,
    CloseButton,
    Flex,
    Dialog,
    Portal,
} from "@chakra-ui/react";
import { LLMProviderSelector } from "./llm-provider-selector";
import { ToolSelectionGrid } from "./tool-selection-grid";
import { useAgent } from "@/context/agent-ctx";
import type { ToolInfo } from "@/types/tool";
import { useState, useRef, useEffect } from "react";
import { BASE_URL } from "@/App";
import { FaPencilAlt, FaPlus } from "react-icons/fa";
import { toaster } from "../ui/toaster";

const missingAgentFieldWarning = (field: string) => (
    <span style={{ color: "#888" }}>No {field} set.</span>
);

export interface AgentCardProps {
    mode?: "view" | "edit" | "create";
    onSave?: (agent: any) => void;
    onCancel?: () => void;
    inDialog?: boolean;
}

export const AgentCard = ({
    mode = "view",
    onSave,
    onCancel,
    inDialog = false,
}: AgentCardProps) => {
    const { agent, setAgent, agentDraft, setAgentDraft, updateAgentDraft } =
        useAgent();
    const [isEditing, setIsEditing] = useState(
        mode === "edit" || mode === "create"
    );
    const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
    const [avatarFile, setAvatarFile] = useState<File | null>(null);
    const [isAvatarLoading, setIsAvatarLoading] = useState(false);
    const [availableTools, setAvailableTools] = useState<ToolInfo[]>([]);
    const [isToolPopupOpen, setIsToolPopupOpen] = useState(false);
    const [selectedToolIds, setSelectedToolIds] = useState<Set<string>>(
        new Set()
    );
    const fileInputRef = useRef<HTMLInputElement | null>(null);

    const fetchAvailableTools = async (): Promise<ToolInfo[]> => {
        try {
            const response = await fetch(BASE_URL + "/api/tool/search", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) throw new Error("Failed to fetch available tools");

            const data = await response.json();
            return data.tools;
        } catch (error) {
            console.error("Error fetching available tools:", error);
            return [];
        }
    };

    // Load available tools
    useEffect(() => {
        fetchAvailableTools().then(setAvailableTools);
    }, []);

    // Tool management functions
    const handleRemoveTool = (toolId: string) => {
        if (agentDraft?.tools) {
            updateAgentDraft(
                "tools",
                agentDraft.tools.filter((id) => id !== toolId)
            );
        }
    };

    // Tool Popup management functions
    const openToolPopup = () => {
        setSelectedToolIds(new Set());
        setIsToolPopupOpen(true);
    };

    const closeToolPopup = () => {
        setIsToolPopupOpen(false);
        setSelectedToolIds(new Set());
    };

    const toggleToolSelection = (toolId: string) => {
        const newSelected = new Set(selectedToolIds);
        if (newSelected.has(toolId)) {
            newSelected.delete(toolId);
        } else {
            newSelected.add(toolId);
        }
        setSelectedToolIds(newSelected);
    };

    const handleAddSelectedTools = () => {
        const toolIdsToAdd = Array.from(selectedToolIds).filter(
            (toolId) => !agentDraft?.tools?.includes(toolId)
        );

        if (toolIdsToAdd.length > 0) {
            updateAgentDraft("tools", [
                ...(agentDraft?.tools || []),
                ...toolIdsToAdd,
            ]);
        }

        closeToolPopup();
    };

    const isToolAssigned = (toolId: string) => {
        return agentDraft?.tools?.includes(toolId) || false;
    };

    // Load avatar
    useEffect(() => {
        if (agentDraft?.avatar_image_url && agentDraft.avatar_image_url.trim() !== "") {
            setIsAvatarLoading(true);
        }
    }, [agentDraft?.avatar_image_url]);

    // Setup Modes
    useEffect(() => {
        if (mode === "create") {
            setIsEditing(true);
            setAgentDraft({
                id: "",
                name: "",
                description: "",
                avatar_image_url: "",
                model: "",
                persona: "",
                tone: "",
                tools: [],
            });
        } else if (mode === "edit") {
            setIsEditing(true);
        } else {
            setIsEditing(false);
        }
    }, [mode]);

    const handleAvatarClick = () => {
        if (isEditing && fileInputRef.current) {
            fileInputRef.current.click();
        }
    };

    const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setAvatarFile(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setAvatarPreview(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    // Validate agent
    const validateAgent = (agentDraft: any) => {
        if (!agentDraft?.name || agentDraft.name.trim() === "")
            return { valid: false, message: "Agent name is required." };
        if (!agentDraft?.persona || agentDraft.persona.trim() === "")
            return { valid: false, message: "Agent persona is required." };
        if (!agentDraft?.model || agentDraft.model.trim() === "")
            return { valid: false, message: "Agent model is required." };
        return { valid: true };
    };

    const handleSaveAgent = async () => {
        // Variable to store Agent ID in creation mode
        var agentId = agentDraft?.id;

        if (agentDraft) {
            const validation = validateAgent(agentDraft);
            if (!validation.valid) {
                alert(validation.message);
                return;
            }

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
                    if (!agentDraft.id) {
                        updateAgentDraft("id", data.id);
                        agentId = data.id;
                    }
                    setAgent(agentDraft);
                    if (onSave) onSave({ ...agentDraft, id: data.id });

                    toaster.create({
                        description: "Agent saved successfully",
                        type: "success",
                    });
                }

                setIsEditing(false);
            } catch (error) {
                console.error("Error saving agent:", error);
                toaster.create({
                    description: "Failed to save agent",
                    type: "error",
                });
            }
        }

        // Upload agent avatar if a new avatar is set
        if (avatarFile) {
            try {
                const formData = new FormData();
                formData.append("avatar", avatarFile);
                const response = await fetch(
                    BASE_URL +
                        `/api/agent/avatar?id=${agentDraft?.id || agentId}`,
                    {
                        method: "POST",
                        body: formData,
                    }
                );

                if (!response.ok) {
                    throw new Error("Failed to upload avatar");
                }
                // Optionally, update agentDraft/avatar with the returned URL
                const result = await response.json();
                updateAgentDraft("avatar_image_url", result.url);
                setAvatarFile(null);
                setAvatarPreview(null);
            } catch (error) {
                console.error("Error uploading avatar:", error);
                toaster.create({
                    description: "Failed to upload avatar",
                    type: "error",
                });
            }
        }
    };

    return (
        <>
            <Card.Root maxH={"85vh"}>
                {/* Header */}
                <Card.Header flexDir={"row"} spaceX={5}>
                    {/* Avatar */}
                    <div
                        style={{
                            position: "relative",
                            display: "inline-block",
                        }}
                    >
                        <Avatar.Root
                            size="2xl"
                            shape="rounded"
                            style={{
                                cursor: isEditing ? "pointer" : "default",
                            }}
                            onClick={handleAvatarClick}
                        >
                            <Avatar.Image
                                src={
                                    avatarPreview ||
                                    agentDraft?.avatar_image_url ||
                                    undefined
                                }
                                onLoad={() => setIsAvatarLoading(false)}
                                onError={() => setIsAvatarLoading(false)}
                            />
                            {isAvatarLoading ? (
                                <Avatar.Fallback>
                                    <Spinner size="sm" color="teal.500" />
                                </Avatar.Fallback>
                            ) : (
                                <Avatar.Fallback name={agent?.name} />
                            )}
                        </Avatar.Root>
                        {isEditing && (
                            <IconButton
                                pos={"absolute"}
                                bottom={-2}
                                right={-2}
                                bg={"white"}
                                borderRadius={"50%"}
                                boxShadow={"0 1px 4px rgba(0,0,0,0.15)"}
                                zIndex={2}
                                display={"flex"}
                                alignItems={"center"}
                                justifyContent={"center"}
                                onClick={handleAvatarClick}
                            >
                                <FaPencilAlt color="teal" />
                            </IconButton>
                        )}
                        {isEditing && (
                            <input
                                type="file"
                                accept="image/*"
                                style={{ display: "none" }}
                                ref={fileInputRef}
                                onChange={handleAvatarChange}
                            />
                        )}
                    </div>

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

                        {/* Model */}
                        <Card.Description fontSize={"x-small"}>
                            {agentDraft?.model}
                        </Card.Description>
                    </VStack>
                </Card.Header>

                {/* Body */}
                <Card.Body maxH={"600px"} overflowY={"auto"} spaceY={2}>
                    {/* Description */}
                    {isEditing ? (
                        <Input
                            value={agentDraft?.description || ""}
                            placeholder="Agent description"
                            size="sm"
                            fontSize="xs"
                            p={2}
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

                    <LLMProviderSelector
                        mode={isEditing ? "edit" : "view"}
                    />

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
                                        updateAgentDraft(
                                            "persona",
                                            e.target.value
                                        )
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
                    <Field.Root>
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

                    {/* Tools */}
                    <Field.Root>
                        <Field.Label>Tools</Field.Label>
                        <Box>
                            {/* Current Tools */}
                            {agentDraft?.tools &&
                            agentDraft.tools.length > 0 ? (
                                <Flex wrap="wrap" gap={2} mb={2}>
                                    {agentDraft.tools.map((toolId) => (
                                        <Badge
                                            key={toolId}
                                            colorScheme="teal"
                                            variant="solid"
                                            px={3}
                                            py={1}
                                            borderRadius="4xl"
                                            display="flex"
                                            justifyContent="center"
                                            alignItems="center"
                                            gap={2}
                                        >
                                            <Text fontSize="sm">
                                                {toolId}
                                            </Text>
                                            {isEditing && (
                                                <CloseButton
                                                    size="xs"
                                                    borderRadius="4xl"
                                                    onClick={() =>
                                                        handleRemoveTool(toolId)
                                                    }
                                                    color="black"
                                                    _hover={{
                                                        bg: "red.500",
                                                        color: "white",
                                                    }}
                                                />
                                            )}
                                        </Badge>
                                    ))}
                                </Flex>
                            ) : (
                                !isEditing && (
                                    <Text fontSize="sm" color="gray.500" mb={2}>
                                        No tools assigned
                                    </Text>
                                )
                            )}

                            {/* Add Tool Button */}
                            {isEditing && (
                                <IconButton
                                    size="sm"
                                    variant="outline"
                                    colorScheme="teal"
                                    onClick={openToolPopup}
                                    aria-label="Add Tools"
                                    _hover={{
                                        bg: "teal.500",
                                        color: "black",
                                        borderColor: "teal.500",
                                    }}
                                >
                                    <FaPlus />
                                </IconButton>
                            )}
                        </Box>
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
                        {mode != "create" && !inDialog && (
                            <Button
                                variant="outline"
                                colorScheme="gray"
                                bgColor={isEditing ? "teal.500" : ""}
                                color={isEditing ? "black" : ""}
                                onClick={() => setIsEditing(true)}
                            >
                                Edit
                            </Button>
                        )}

                        {/* Cancel */}
                        <Button
                            variant="outline"
                            colorScheme="gray"
                            disabled={!isEditing}
                            onClick={() => {
                                setIsEditing(false);
                                setAgentDraft(agent);
                                setAvatarPreview(null);
                                if (onCancel) onCancel();
                            }}
                        >
                            Cancel
                        </Button>

                        {/* Save */}
                        <Button
                            colorScheme="teal"
                            variant="solid"
                            disabled={!isEditing || !agentDraft?.name}
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

            {/* Tool Selection Popup */}
            <Dialog.Root
                open={isToolPopupOpen}
                onOpenChange={(details) => setIsToolPopupOpen(details.open)}
                size="xl"
                placement="center"
            >
                <Portal>
                    <Dialog.Backdrop />
                    <Dialog.Positioner>
                        <Dialog.Content maxW="4xl">
                            <Dialog.Header>
                                <Dialog.Title>Select Tools</Dialog.Title>
                            </Dialog.Header>
                            <Dialog.Body>
                                <ToolSelectionGrid
                                    availableTools={availableTools}
                                    isToolAssigned={isToolAssigned}
                                    selectedToolIds={selectedToolIds}
                                    onToggleToolSelection={toggleToolSelection}
                                    onRemoveTool={handleRemoveTool}
                                />
                            </Dialog.Body>
                            <Dialog.Footer>
                                <Button
                                    variant="outline"
                                    onClick={closeToolPopup}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    colorScheme="teal"
                                    onClick={handleAddSelectedTools}
                                    disabled={selectedToolIds.size === 0}
                                >
                                    Add Selected ({selectedToolIds.size})
                                </Button>
                            </Dialog.Footer>
                            <Dialog.CloseTrigger asChild>
                                <CloseButton size="sm" />
                            </Dialog.CloseTrigger>
                        </Dialog.Content>
                    </Dialog.Positioner>
                </Portal>
            </Dialog.Root>
        </>
    );
};
