import { Box, Container, Flex, Text, IconButton } from "@chakra-ui/react";
import { ColorModeButton } from "@/components/ui/color-mode";
import { FaBook, FaClipboardList, FaComment, FaImages, FaSeedling, FaUsers, FaVideo } from "react-icons/fa";
import { Tooltip } from "@/components/ui/tooltip";
import { useNavigate, useLocation } from "react-router-dom";
import { FaRobot } from "react-icons/fa6";
import { useChat } from "@/context/chat-ctx";
import { SettingsPopover } from "@/components/settings/settings-popover";

function Navbar() {
    const navigate = useNavigate();
    const location = useLocation();
    const { resetMessages } = useChat();
    
    const isActive = (path: string) => location.pathname === path;
    
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
                            <SettingsPopover />
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
                                    variant={isActive("/chat") ? "solid" : "ghost"}
                                    colorPalette={isActive("/chat") ? "primary" : undefined}
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
                                    variant={isActive("/agent") ? "solid" : "ghost"}
                                    colorPalette={isActive("/agent") ? "primary" : undefined}
                                    size="xl"
                                    onClick={() => navigate("/agent")}
                                >
                                    <FaRobot />
                                </IconButton>
                            </Tooltip>

                            {/* Image library */}
                            <Tooltip content="Image" showArrow>
                                <IconButton
                                    aria-label="Image library"
                                    variant={isActive("/image") ? "solid" : "ghost"}
                                    colorPalette={isActive("/image") ? "primary" : undefined}
                                    size="xl"
                                    onClick={() => navigate("/image")}
                                >
                                    <FaImages />
                                </IconButton>
                            </Tooltip>

                            {/* Video library */}
                            <Tooltip content="Video" showArrow>
                                <IconButton
                                    aria-label="Video library"
                                    variant={isActive("/video") ? "solid" : "ghost"}
                                    colorPalette={isActive("/video") ? "primary" : undefined}
                                    size="xl"
                                    onClick={() => navigate("/video")}
                                >
                                    <FaVideo />
                                </IconButton>
                            </Tooltip>

                            {/* Knowledge */}
                            <Tooltip content="Knowledge" showArrow>
                                <IconButton
                                    aria-label="Knowledge"
                                    variant={isActive("/knowledge") ? "solid" : "ghost"}
                                    colorPalette={isActive("/knowledge") ? "primary" : undefined}
                                    size="xl"
                                    onClick={() => navigate("/knowledge")}
                                >
                                    <FaBook />
                                </IconButton>
                            </Tooltip>

                            {/* Plant page */}
                            <Tooltip content="Plant" showArrow>
                                <IconButton
                                    aria-label="Plant"
                                    variant={isActive("/plant") ? "solid" : "ghost"}
                                    colorPalette={isActive("/plant") ? "primary" : undefined}
                                    size="xl"
                                    onClick={() => navigate("/plant")}
                                >
                                    <FaSeedling />
                                </IconButton>
                            </Tooltip>

                            {/* Work management */}
                            <Tooltip content="Work" showArrow>
                                <IconButton
                                    aria-label="Work management"
                                    variant={isActive("/work") ? "solid" : "ghost"}
                                    colorPalette={isActive("/work") ? "primary" : undefined}
                                    size="xl"
                                    onClick={() => navigate("/work")}
                                >
                                    <FaClipboardList />
                                </IconButton>
                            </Tooltip>

                            {/* Team */}
                            <Tooltip content="Team" showArrow>
                                <IconButton
                                    aria-label="Team"
                                    variant={isActive("/team") ? "solid" : "ghost"}
                                    colorPalette={isActive("/team") ? "primary" : undefined}
                                    size="xl"
                                    onClick={() => navigate("/team")}
                                >
                                    <FaUsers />
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
