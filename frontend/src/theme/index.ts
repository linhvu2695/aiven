import { createSystem, defaultConfig, defineConfig, mergeConfigs } from "@chakra-ui/react"

const theme = defineConfig({
    theme: {
        tokens: {
            colors: {
                brand: {
                    50: { value: "#e6f6ff" },
                    100: { value: "#b3e0ff" },
                    200: { value: "#80caff" },
                    300: { value: "#4daeff" },
                    400: { value: "#1a92ff" },
                    500: { value: "#007bff" },
                    600: { value: "#0062cc" },
                    700: { value: "#004c99" },
                    800: { value: "#003566" },
                    900: { value: "#001f33" },
                },
                background: {
                    light: { value: "#ffffff" },
                    dark: { value: "#1a202c" },
                },
                text: {
                    light: { value: "#1a202c" },
                    dark: { value: "#ffffff" },
                },
            },
        },
        semanticTokens: {
            colors: {
                "bg.default": {
                    default: { value: "{colors.background.light}" },
                    _dark: { value: "{colors.background.dark}" },
                },
                "bg.subtle": {
                    default: { value: "{colors.gray.100}" },
                    _dark: { value: "{colors.gray.800}" },
                },
                "fg.default": {
                    default: { value: "{colors.text.light}" },
                    _dark: { value: "{colors.text.dark}" },
                },
                "border.default": {
                    default: { value: "{colors.gray.200}" },
                    _dark: { value: "{colors.red.700}" },
                },
                "button.primary.bg": {
                    default: { value: "{colors.brand.500}" },
                    _dark: { value: "{colors.brand.300}" },
                },
                "button.primary.text": {
                    default: { value: "white" },
                    _dark: { value: "black" },
                },
            },
        },
    }
});

const config = mergeConfigs(defaultConfig, theme);

const system = createSystem(config);

export default system; 