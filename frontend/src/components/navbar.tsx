import { Box, Container, Flex, Text, IconButton } from "@chakra-ui/react";
import { ColorModeButton } from "@/components/ui/color-mode";
import { FaBook, FaComment } from "react-icons/fa";
import { Tooltip } from "@/components/ui/tooltip";
import { useNavigate } from "react-router-dom";
import { FaRobot } from "react-icons/fa6";
import { useChat } from "@/context/chat-ctx";

function Navbar() {
    const navigate = useNavigate();
    const { resetMessages } = useChat();
    
    return (
        <>
            <Container as="nav" maxW={"1800px"} paddingTop={1}>
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

                            {/* Start new chat */}
                            <Tooltip content="Start new chat" showArrow>
                                <IconButton
                                    aria-label="Start new chat"
                                    variant="ghost"
                                    size="xl"
                                    onClick={() => {
                                        resetMessages();
                                        navigate("/chat");
                                    }}
                                >
                                    <FaComment />
                                </IconButton>
                            </Tooltip>

                            {/* Agents management */}
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

                            {/* Knowledge base */}
                            <Tooltip content="Knowledge base" showArrow>
                                <IconButton
                                    aria-label="Knowledge base"
                                    variant="ghost"
                                    size="xl"
                                    onClick={() => navigate("/knowledge")}
                                >
                                    <FaBook />
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
