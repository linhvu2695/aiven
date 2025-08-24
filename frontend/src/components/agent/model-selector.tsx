import { BASE_URL } from "@/App";
import { useAgent } from "@/context/agent-ctx";
import {
    RadioCard,
    Wrap,
    WrapItem,
    VStack,
} from "@chakra-ui/react";
import { Dropdown } from "@/components/ui";
import { Claude, Gemini, Mistral, Nvidia, OpenAI, XAI } from "@lobehub/icons";
import { useState, useEffect } from "react";

export const LLM_PROVIDERS = [
    { value: "openai", title: "OpenAI", icon: OpenAI },
    { value: "google_genai", title: "Gemini", icon: Gemini.Color },
    { value: "anthropic", title: "Claude", icon: Claude.Color },
    { value: "xai", title: "xAI", icon: XAI },
    { value: "mistralai", title: "Mistral", icon: Mistral.Color },
    { value: "nvidia", title: "NVIDIA", icon: Nvidia.Color },
];

export interface ModelSelectorProps {
    mode?: "view" | "edit";
}

export const ModelSelector = ({
    mode = "edit",
}: ModelSelectorProps) => {
    const { agentDraft, updateAgentDraft } = useAgent();
    const [provider, setProvider] = useState("openai");
    const [providerOptions, setProviderOptions] = useState<
        Record<string, { value: string; label: string }[]>
    >({});
    const [loading, setLoading] = useState(true);

    // Fetch model options on mount
    useEffect(() => {
        const fetchOptions = async () => {
            setLoading(true);
            try {
                const response = await fetch(BASE_URL + "/api/chat/models", {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });
                const data = await response.json();

                // Expecting data to be in the format: { [provider: string]: { value, label }[] }
                setProviderOptions(data);

                // If agentDraft.model is set, find the provider that contains it
                let initialProvider = "google_genai";
                if (agentDraft?.model) {
                    for (const [prov, models] of Object.entries(data) as [
                        string,
                        { value: string; label: string }[]
                    ][]) {
                        if (models.some((m) => m.value === agentDraft.model)) {
                            initialProvider = prov;
                            break;
                        }
                    }
                }
                setProvider(initialProvider);
            } catch (e) {
                console.log(e);
            } finally {
                setLoading(false);
            }
        };
        fetchOptions();
    }, [agentDraft]);

    const handleProviderChange = (value: string) => {
        setProvider(value);
        if (providerOptions[value] && providerOptions[value][0]) {
            updateAgentDraft("model", providerOptions[value][0].value);
        } else {
            updateAgentDraft("model", "");
        }
    };

    return (
        <VStack spaceY={4} padding={4}>
            {/* LLM Provider Selector */}
            <RadioCard.Root
                colorPalette="teal"
                value={provider}
                onValueChange={
                    mode === "edit"
                        ? (val) => handleProviderChange(val.value ?? "openai")
                        : undefined
                }
                disabled={mode === "view"}
                size="sm"
            >
                <Wrap align="stretch">
                    {LLM_PROVIDERS.map((item) => (
                        <WrapItem key={item.value}>
                            <RadioCard.Item value={item.value}>
                                <RadioCard.ItemHiddenInput />
                                <RadioCard.ItemControl>
                                    <RadioCard.ItemText fontSize={14}>
                                        {item.icon && (
                                            <span
                                                style={{
                                                    marginRight: 6,
                                                    display: "inline-flex",
                                                    alignSelf: "center",
                                                }}
                                            >
                                                {<item.icon size={13} />}
                                            </span>
                                        )}
                                        {item.title}
                                    </RadioCard.ItemText>
                                    <RadioCard.ItemIndicator />
                                </RadioCard.ItemControl>
                            </RadioCard.Item>
                        </WrapItem>
                    ))}
                </Wrap>
            </RadioCard.Root>

            {/* Chat Model selector */}
            <Dropdown
                title={mode === "edit" ? "Select model" : undefined}
                value={agentDraft?.model ?? ""}
                onValueChange={
                    mode === "edit"
                        ? (value: string) => updateAgentDraft("model", value)
                        : () => {}
                }
                options={providerOptions[provider] || []}
                placeholder={mode === "edit" ? "Select model" : ""}
                disabled={
                    loading || !providerOptions[provider] || mode === "view"
                }
                fontSize="sm"
                fontWeight="medium"
                mb={0}
            />
        </VStack>
    );
};
