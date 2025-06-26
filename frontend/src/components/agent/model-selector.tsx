import { BASE_URL } from "@/App";
import {
    RadioCard,
    Wrap,
    WrapItem,
    Select,
    Portal,
    createListCollection,
    VStack,
} from "@chakra-ui/react";
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

export const ModelSelector = () => {
    const [provider, setProvider] = useState("google_genai");
    const [model, setModel] = useState("");
    const [providerOptions, setProviderOptions] = useState<Record<string, { value: string; label: string }[]>>({});
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

                // Set initial model if available
                if (data[provider] && data[provider][0]) {
                    setModel(data[provider][0].value);
                }
            } catch (e) {
                console.log(e);
            } finally {
                setLoading(false);
            }
        };
        fetchOptions();
    }, []);

    const handleProviderChange = (value: string) => {
        setProvider(value);
        if (providerOptions[value] && providerOptions[value][0]) {
            setModel(providerOptions[value][0].value);
        } else {
            setModel("");
        }
    };

    return (
        <VStack spaceY={4} padding={4}>
            {/* LLM Provider Selector */}
            <RadioCard.Root
                colorPalette="teal"
                value={provider}
                onValueChange={(val) =>
                    handleProviderChange(val.value ?? "google_genai")
                }
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
            <Select.Root
                collection={createListCollection({
                    items: providerOptions[provider] || [],
                })}
                value={[model]}
                onValueChange={(items) => setModel(items.value[0])}
                disabled={loading || !providerOptions[provider]}
            >
                <Select.HiddenSelect />
                <Select.Label>Select model</Select.Label>
                <Select.Control>
                    <Select.Trigger>
                        <Select.ValueText placeholder="Select model" />
                    </Select.Trigger>
                    <Select.IndicatorGroup>
                        <Select.Indicator />
                    </Select.IndicatorGroup>
                </Select.Control>
                <Portal>
                    <Select.Positioner>
                        <Select.Content>
                            {(providerOptions[provider] || []).map((modelItem) => (
                                <Select.Item
                                    item={modelItem}
                                    key={modelItem.value}
                                >
                                    {modelItem.label}
                                    <Select.ItemIndicator />
                                </Select.Item>
                            ))}
                        </Select.Content>
                    </Select.Positioner>
                </Portal>
            </Select.Root>
        </VStack>
    );
};
