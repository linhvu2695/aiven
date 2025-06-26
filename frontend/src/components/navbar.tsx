import { Box, Container, Flex, Text } from "@chakra-ui/react";
import { ColorModeButton } from "@/components/ui/color-mode";

function Navbar() {
    return (
        <>
            <Container maxW={"1800px"} paddingTop={1}>
                <Box
                    px={4}
                    my={4}
                    borderRadius={5}
                    bg={{ base: "gray.200", _dark: "gray.900" }}
                >
                    <Flex
                        h="16"
                        alignItems={"center"}
                        justifyContent={"space-between"}
                    >
                        {/* Left side */}
                        <Flex
                            alignItems={"center"}
                            justifyContent={"center"}
                            gap={3}
                            display={{ base: "none", sm: "flex" }}
                        >
                            <ColorModeButton />
                            <Text fontSize={"18px"} fontWeight={"bold"}>
                                aiven
                            </Text>
                        </Flex>
                    </Flex>
                </Box>
            </Container>
        </>
    );
}

export default Navbar;
