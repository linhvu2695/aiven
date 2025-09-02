import { Box, Input, Text } from "@chakra-ui/react";
import type { InputProps } from "@chakra-ui/react";
import { forwardRef } from "react";

export interface FormFieldProps extends Omit<InputProps, 'value' | 'onChange'> {
    label: string;
    labelColor?: string;
    value: string;
    onChange: (value: string) => void;
    isRequired?: boolean;
    error?: string;
    helperText?: string;
}

export const FormField = forwardRef<HTMLInputElement, FormFieldProps>(
    ({ label, labelColor, value, onChange, isRequired, error, helperText, ...inputProps }, ref) => {
        return (
            <Box flex={inputProps.flex || 1}>
                <Text fontSize="sm" fontWeight="medium" mb={2} color={labelColor || "white"}>
                    {label}
                    {isRequired && (
                        <Text as="span" color="red.500" ml={1}>
                            *
                        </Text>
                    )}
                </Text>
                <Input
                    ref={ref}
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    {...inputProps}
                />
                {error && (
                    <Text fontSize="xs" color="red.500" mt={1}>
                        {error}
                    </Text>
                )}
                {helperText && !error && (
                    <Text fontSize="xs" color="gray.500" mt={1}>
                        {helperText}
                    </Text>
                )}
            </Box>
        );
    }
);

FormField.displayName = "FormField";
