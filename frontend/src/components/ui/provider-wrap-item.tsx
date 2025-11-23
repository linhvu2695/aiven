import { RadioCard, WrapItem } from "@chakra-ui/react";
import type { ComponentType } from "react";

interface ProviderWrapItemProps {
    value: string;
    title: string;
    icon?: ComponentType<{ size?: number }>;
    disabled?: boolean;
}

export const ProviderWrapItem = ({ value, title, icon: Icon, disabled }: ProviderWrapItemProps) => {
    return (
        <WrapItem key={value}>
            <RadioCard.Item value={value} disabled={disabled}>
                <RadioCard.ItemHiddenInput />
                <RadioCard.ItemControl>
                    <RadioCard.ItemText fontSize={14}>
                        {Icon && (
                            <span
                                style={{
                                    marginRight: 6,
                                    display: "inline-flex",
                                    alignSelf: "center",
                                }}
                            >
                                <Icon size={13} />
                            </span>
                        )}
                        {title}
                    </RadioCard.ItemText>
                    <RadioCard.ItemIndicator />
                </RadioCard.ItemControl>
            </RadioCard.Item>
        </WrapItem>
    );
};

