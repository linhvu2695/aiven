import { BASE_URL } from "@/App";
import { useAgent } from "@/context/agent-ctx";
import {
    RadioCard,
    Wrap,
    VStack,
} from "@chakra-ui/react";
import { Dropdown } from "@/components/ui";
import { ProviderWrapItem } from "@/components/ui/provider-wrap-item";
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

export interface LLMProviderSelectorProps {
    mode?: "view" | "edit";
}

export const LLMProviderSelector = ({
    mode = "edit",
}: LLMProviderSelectorProps) => {
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
            const url = BASE_URL + "/api/chat/models";

            try {
                const response = await fetch(url, {
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
                colorPalette="primary"
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
                        <ProviderWrapItem
                            key={item.value}
                            value={item.value}
                            title={item.title}
                            icon={item.icon}
                        />
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

