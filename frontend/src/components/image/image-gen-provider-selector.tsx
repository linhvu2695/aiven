import { BASE_URL } from "@/App";
import {
    RadioCard,
    Wrap,
    VStack,
} from "@chakra-ui/react";
import { Dropdown } from "@/components/ui";
import { ProviderWrapItem } from "@/components/ui/provider-wrap-item";
import { Gemini, OpenAI } from "@lobehub/icons";
import { useState, useEffect } from "react";
import { useImageGen } from "@/context/image-gen-ctx";

export const IMAGE_GEN_PROVIDERS = [
    { value: "google_genai", title: "Gemini", icon: Gemini.Color },
    { value: "openai", title: "OpenAI", icon: OpenAI },
];

export const ImageGenProviderSelector = () => {
    const { provider, model, setProvider, setModel, isGenerating } = useImageGen();
    const [providerOptions, setProviderOptions] = useState<
        Record<string, { value: string; label: string }[]>
    >({});
    const [loading, setLoading] = useState(true);

    // Fetch model options on mount
    useEffect(() => {
        const fetchOptions = async () => {
            setLoading(true);
            const url = BASE_URL + "/api/image/models";

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

                // Set default model for the current provider if not already set
                if (!model && data[provider] && data[provider][0]) {
                    setModel(data[provider][0].value);
                }
            } catch (e) {
                console.log(e);
            } finally {
                setLoading(false);
            }
        };
        fetchOptions();
    }, [provider, model, setModel]);

    const handleProviderChange = (value: string) => {
        setProvider(value);
        // Set the first model for the new provider
        if (providerOptions[value] && providerOptions[value][0]) {
            setModel(providerOptions[value][0].value);
        }
    };

    return (
        <VStack spaceY={4}>
            {/* Image Gen Provider Selector */}
            <RadioCard.Root
                colorPalette="teal"
                value={provider}
                onValueChange={
                    !isGenerating
                        ? (val) => handleProviderChange(val.value ?? "google_genai")
                        : undefined
                }
                disabled={isGenerating}
                size="sm"
            >
                <Wrap align="stretch">
                    {IMAGE_GEN_PROVIDERS.map((item) => (
                        <ProviderWrapItem
                            key={item.value}
                            value={item.value}
                            title={item.title}
                            icon={item.icon}
                        />
                    ))}
                </Wrap>
            </RadioCard.Root>

            {/* Image Model selector */}
            <Dropdown
                title="Select model"
                value={model}
                onValueChange={setModel}
                options={providerOptions[provider] || []}
                placeholder="Select model"
                disabled={loading || !providerOptions[provider] || isGenerating}
                fontSize="sm"
                fontWeight="medium"
                mb={0}
            />
        </VStack>
    );
};