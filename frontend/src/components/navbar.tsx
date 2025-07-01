import { Box, Container, Flex, Text, IconButton } from "@chakra-ui/react";
import { ColorModeButton } from "@/components/ui/color-mode";
import { FaComment, FaComments } from "react-icons/fa";
import { Tooltip } from "@/components/ui/tooltip";
import { useNavigate } from "react-router-dom";
import { FaRobot } from "react-icons/fa6";

function Navbar() {
    const navigate = useNavigate();
    
    return (
        <>
            <Container maxW={"1800px"} paddingTop={1}>
                <Box
                    px={4}
                    my={4}
                    borderRadius={5}
                    bg="bg.subtle"
                    borderWidth="1px"
                    borderColor="border.default"
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

                        {/* Right side */}
                        <Flex gap={3} alignItems={"center"}>

                            {/* Chat */}
                            <Tooltip content="New chat" showArrow>
                                <IconButton
                                    aria-label="Open chat"
                                    variant="ghost"
                                    size="xl"
                                    onClick={() => navigate("/chat")}
                                >
                                    <FaComment />
                                </IconButton>
                            </Tooltip>

                            {/* Chat */}
                            <Tooltip content="Agents" showArrow>
                                <IconButton
                                    aria-label="Agent management"
                                    variant="ghost"
                                    size="xl"
                                    onClick={() => navigate("/agent")}
                                >
                                    <FaRobot />
                                </IconButton>
                            </Tooltip>
                        </Flex>
                    </Flex>
                </Box>
            </Container>
        </>
    );
}

export default Navbar;
