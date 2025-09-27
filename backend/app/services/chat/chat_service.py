import logging, re
from datetime import datetime, timezone
from typing import AsyncGenerator
from pathlib import Path
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from app.classes.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatStreamChunk,
)
from app.classes.agent import AgentInfo
from app.core.config import settings
from app.utils.chat import chat_utils
from app.core.constants import (
    LLMModel,
    OPENAI_MODELS,
    GEMINI_MODELS,
    CLAUDE_MODELS,
    GROK_MODELS,
    MISTRAL_MODELS,
    NVIDIA_MODELS,
)
from app.services.agent.agent_service import AgentService
from app.services.tool.tool_service import ToolService
from app.services.chat.chat_history import MongoDBChatHistory
from app.core.database import update_document

GPT_DEFAULT_MODEL = LLMModel.GPT_4O_MINI

AGENT_SYSTEM_PROMPT = """
Name: {name}
Description: {description}
Persona: {persona}
Tone: {tone}
"""


class ChatService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(ChatService, cls).__new__(cls)
        return cls._instance

    async def _load_mcp_tools(self, tool_names: list[str]) -> list[BaseTool]:
        if not tool_names:
            return []

        try:
            # Get the path to the MCP server
            current_dir = Path(__file__).parent
            backend_dir = current_dir.parent.parent.parent
            mcp_server_path = backend_dir / "mcp_server" / "server.py"

            client = MultiServerMCPClient(
                {
                    "aiven": {
                        "command": "python",
                        "args": [str(mcp_server_path)],
                        "transport": "stdio",
                    }
                }
            )

            # Get all available tools from MCP server
            all_functions = await client.get_tools()

            allowed_mcp_functions = ToolService().get_mcp_functions_for_tools(
                tool_names
            )

            filtered_functions = []
            for function in all_functions:
                if function.name in allowed_mcp_functions:
                    filtered_functions.append(function)
            return filtered_functions

        except Exception as e:
            logging.getLogger("uvicorn.warning").warning(
                f"Warning: Could not load MCP tools: {e}"
            )
            return []

    def _parse_format_error(self, error_message: str) -> str:
        """Parse LLM provider error message to extract supported formats and return user-friendly message."""
        # Look for patterns like 'image/jpeg', 'image/png', etc. in the error message
        format_pattern = r"'(image/\w+)'"
        matches = re.findall(format_pattern, error_message)

        if matches:
            # Convert mime types to user-friendly format names
            format_names = [fmt.split("/")[1].upper() for fmt in matches]
            supported_list = ", ".join(format_names)
            return f"❌ File Upload Error: The uploaded image format is not supported by this model. Supported formats: {supported_list}"

        # Fallback for other format-related errors
        if "media_type" in error_message.lower() or "format" in error_message.lower():
            return "❌ File Upload Error: The uploaded file format is not supported by this model. Please try a different file format."

        return f"❌ File Upload Error: {error_message}"

    async def _get_trace_metadata(self, request: ChatRequest) -> dict:
        agent = await AgentService().get_agent(request.agent)

        trace_metadata = {
            "agent_id": request.agent,
            "agent_name": agent.name,
            "model": agent.model,
            "text_length": len(request.message),
            "has_files": bool(request.file_contents),
            "file_count": len(request.file_contents) if request.file_contents else 0,
        }
        return trace_metadata

    async def _get_agent_system_prompt(self, agent: AgentInfo) -> str:
        return AGENT_SYSTEM_PROMPT.format(
            name=agent.name,
            description=agent.description,
            persona=agent.persona,
            tone=agent.tone,
        )

    async def _generate_conversation_name_if_needed(self, history: MongoDBChatHistory, agent_id: str) -> None:
        """
        Generate a conversation name using AI for new conversations.
        Only generates a name if the conversation has 2-4 messages and doesn't already have a name.
        """
        conversation = await history._aget_conversation()
        if not conversation:
            return
        
        # Only generate name for new conversations (2-4 messages) without existing names
        message_count = len(conversation.messages)
        if message_count < 2 or message_count > 4 or (conversation.name and conversation.name.strip()):
            return
        
        try:
            # Get agent and model configuration
            agent = await AgentService().get_agent(agent_id)
            naming_model = self.get_chat_model(agent.model)
            
            # Get the first few messages to generate a meaningful name
            messages_for_naming = conversation.messages[:3]  # Use first 3 messages
            
            # Create a simple conversation context for naming
            conversation_context = ""
            for msg in messages_for_naming:
                role = "User" if msg.__class__.__name__ == "HumanMessage" else "Assistant"
                content = msg.content[:200] if isinstance(msg.content, str) else str(msg.content)[:200]  # Truncate for efficiency
                conversation_context += f"{role}: {content}\n"
            
            # Create a prompt for generating conversation names
            naming_prompt = f"""Based on the following conversation, generate a short, descriptive name (2-5 words) that captures the main topic or purpose. Be concise and specific.\n
            Conversation: {conversation_context}.\n
            Name (2-5 words only):"""
            
            # Generate the name
            response = await naming_model.ainvoke([HumanMessage(content=naming_prompt)])
            
            # Handle response content properly (it might be a string or list)
            content = response.content
            if isinstance(content, list):
                # If it's a list, join the text parts
                generated_name = " ".join(str(item) for item in content if isinstance(item, str))
            else:
                generated_name = str(content)
            
            generated_name = generated_name.strip().strip('"').strip("'")
            
            # Clean up the name (remove quotes, limit length)
            if len(generated_name) > 50:
                generated_name = generated_name[:50].strip()
            
            # Update the conversation with the generated name
            await update_document("conversation", history._session_id, {
                "name": generated_name,
                "updated_at": datetime.now(timezone.utc)
            })
            
            logging.getLogger("uvicorn.info").info(f"Generated conversation name: '{generated_name}' for session {history._session_id}")
            
        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Error generating conversation name: {e}")

    def get_chat_model(self, model_name) -> BaseChatModel:
        if model_name in OPENAI_MODELS:
            return init_chat_model(
                model=model_name,
                model_provider="openai",
                api_key=settings.openai_api_key,
            )
        if model_name in GEMINI_MODELS:
            return init_chat_model(
                model=model_name,
                model_provider="google_genai",
                api_key=settings.gemini_api_key,
            )
        if model_name in CLAUDE_MODELS:
            return init_chat_model(
                model=model_name,
                model_provider="anthropic",
                api_key=settings.anthropic_api_key,
            )
        if model_name in GROK_MODELS:
            return init_chat_model(
                model=model_name, model_provider="xai", api_key=settings.xai_api_key
            )
        if model_name in MISTRAL_MODELS:
            return init_chat_model(
                model=model_name,
                model_provider="mistralai",
                api_key=settings.mistral_api_key,
            )
        if model_name in NVIDIA_MODELS:
            return init_chat_model(
                model=model_name,
                model_provider="nvidia",
                api_key=settings.nvidia_api_key,
            )

        return init_chat_model(
            model=GPT_DEFAULT_MODEL,
            model_provider="openai",
            api_key=settings.openai_api_key,
        )

    async def generate_chat_response(self, request: ChatRequest) -> ChatResponse:
        """
        Generate a chat response using LangGraph's invoke capabilities.
        Persists messages to chat history and returns the complete response.
        """
        assistant_response = ""
        history = None
        
        try:
            logging.getLogger("uvicorn.info").info("Step 1: Starting chat response")
            agent = await AgentService().get_agent(request.agent)
            model = self.get_chat_model(agent.model)

            logging.getLogger("uvicorn.info").info("Step 2: Retrieve conversation history")
            history = MongoDBChatHistory(request.session_id, request.agent)
            history_messages = await history.aget_messages()

            logging.getLogger("uvicorn.info").info("Step 3: Building current message with file content")
            if request.file_contents and len(request.file_contents) > 0:
                # Create multimodal message with both text and file content
                file_content = request.file_contents[0]  # expect only one file
                multimodal_content = [
                    {"type": "text", "text": request.message},
                    file_content.model_dump()
                ]
                current_message = HumanMessage(content=multimodal_content)
            else:
                # Use the converted content as-is (handles both string and multimodal)
                current_message = HumanMessage(content=request.message)
            await history.aadd_messages([current_message])
            history_messages.append(current_message)

            logging.getLogger("uvicorn.info").info("Step 4: Loading MCP tools")
            functions = []
            if agent.tools is not None and len(agent.tools) > 0:
                functions = await self._load_mcp_tools(agent.tools)

            logging.getLogger("uvicorn.info").info("Step 5: Creating LangGraph react agent")
            graph = create_react_agent(
                model,
                functions,
                prompt=await self._get_agent_system_prompt(agent),
            )

            logging.getLogger("uvicorn.info").info("Step 6: Adding custom metadata and tags")
            config = RunnableConfig(
                metadata=await self._get_trace_metadata(request),
                tags=[
                    self.__class__.__name__,
                ],
                run_name=f"Chat with {agent.name}",
            )

            logging.getLogger("uvicorn.info").info("Step 7: Invoking the graph with messages")
            result = await graph.ainvoke({"messages": history_messages}, config=config)

            # Extract the final response from the graph result
            response_message = result["messages"][-1]
            response_content = response_message.content
            if isinstance(response_content, list):
                # Handle list content (like tool calls or complex content)
                assistant_response = ""
                for item in response_content:
                    if isinstance(item, str):
                        assistant_response += item
                    elif isinstance(item, dict) and "text" in item:
                        assistant_response += item["text"]
            else:
                assistant_response = str(response_content)

            return ChatResponse(response=assistant_response)

        except Exception as e:
            error_msg = str(e)
            logging.getLogger("uvicorn.error").error(f"Chat Error: {error_msg}")

            # Determine error response
            error_response = ""
            if any(
                keyword in error_msg.lower()
                for keyword in ["media_type", "format", "image/", "audio/", "video/"]
            ):
                error_response = self._parse_format_error(error_msg)
            elif "BadRequestError" in str(type(e)) or "400" in error_msg:
                error_response = f"❌ Request Error: There was an issue with your request. Please check your input and try again."
            else:
                error_response = f"❌ An error occurred while processing your request. Please try again or contact support if the issue persists."
            
            assistant_response = error_response
            return ChatResponse(response=error_response)
        
        finally:
            logging.getLogger("uvicorn.info").info("Step 8: Persisting assistant's response to chat history")
            if history and assistant_response.strip():
                try:
                    assistant_message = AIMessage(content=assistant_response)
                    await history.aadd_messages([assistant_message])
                except Exception as persist_error:
                    logging.getLogger("uvicorn.error").error(f"Failed to persist assistant message: {persist_error}")
            
            logging.getLogger("uvicorn.info").info("Step 9: Generating conversation name for new conversations")
            if history and assistant_response.strip():
                try:
                    await self._generate_conversation_name_if_needed(history, request.agent)
                except Exception as name_error:
                    logging.getLogger("uvicorn.error").error(f"Failed to generate conversation name: {name_error}")

    async def generate_streaming_chat_response(self, request: ChatRequest) -> AsyncGenerator[ChatStreamChunk, None]:
        """
        Generate a streaming chat response using LangGraph's streaming capabilities.
        Yields individual tokens as they are produced by the LLM.
        After streaming completes, persists the assistant's response to chat history.
        """
        assistant_response = "" 
        history = None
        first_chunk_sent = False
        
        try:
            logging.getLogger("uvicorn.info").info("Step 1: Starting getting LLM stream chat response")
            agent = await AgentService().get_agent(request.agent)
            model = self.get_chat_model(agent.model)

            logging.getLogger("uvicorn.info").info("Step 2: Retrieve conversation history")
            history = MongoDBChatHistory(request.session_id, request.agent)
            history_messages = await history.aget_messages()

            logging.getLogger("uvicorn.info").info("Step 3: Building current message with file content")
            if request.file_contents and len(request.file_contents) > 0:
                # Create multimodal message with both text and file content
                file_content = request.file_contents[0]  # expect only one file
                multimodal_content = [
                        {"type": "text", "text": request.message},
                        file_content.model_dump()
                    ]
                current_message = HumanMessage(content=multimodal_content)
            else:
                # Use the converted content as-is (handles both string and multimodal)
                current_message = HumanMessage(content=request.message)
            await history.aadd_messages([current_message])
            history_messages.append(current_message)

            logging.getLogger("uvicorn.info").info("Step 4: Loading MCP tools")
            functions = []
            if agent.tools is not None and len(agent.tools) > 0:
                functions = await self._load_mcp_tools(agent.tools)

            logging.getLogger("uvicorn.info").info("Step 5: Creating LangGraph react agent")
            graph = create_react_agent(
                model,
                functions,
                prompt=await self._get_agent_system_prompt(agent),
            )

            logging.getLogger("uvicorn.info").info("Step 6: Adding custom metadata and tags")
            config = RunnableConfig(
                metadata=await self._get_trace_metadata(request),
                tags=[
                    self.__class__.__name__,
                ],
                run_name=f"Streaming Chat with {agent.name}",
            )

            logging.getLogger("uvicorn.info").info("Step 7: Streaming graph response")
            async for token, metadata in graph.astream(
                {"messages": history_messages}, 
                config=config,
                stream_mode="messages"
            ):
                # Stream individual tokens as they are produced
                token_content = ""
                if isinstance(token, str):
                    token_content = token
                elif hasattr(token, 'content') and token.content:
                    if isinstance(token.content, str):
                        token_content = token.content
                    elif isinstance(token.content, list):
                        # Handle list content (like tool calls or complex content)
                        for item in token.content:
                            if isinstance(item, str):
                                token_content += item
                            elif isinstance(item, dict) and "text" in item:
                                token_content += item["text"]
                
                # Yield token as ChatStreamChunk
                if token_content:
                    chunk = ChatStreamChunk(
                        content=token_content,
                        session_id=history._session_id if not first_chunk_sent else "",
                        is_complete=False
                    )
                    first_chunk_sent = True
                    yield chunk
                    
                    # Accumulate the response content
                    assistant_response += token_content

        except Exception as e:
            error_msg = str(e)
            logging.getLogger("uvicorn.error").error(f"Chat Streaming Error: {error_msg}")

            # Determine error response
            error_response = ""
            if any(
                keyword in error_msg.lower()
                for keyword in ["media_type", "format", "image/", "audio/", "video/"]
            ):
                error_response = self._parse_format_error(error_msg)
            elif "BadRequestError" in str(type(e)) or "400" in error_msg:
                error_response = f"❌ Request Error: There was an issue with your request. Please check your input and try again."
            else:
                error_response = f"❌ An error occurred while processing your request. Please try again or contact support if the issue persists."
            
            # Yield error as ChatStreamChunk
            assistant_response = error_response
            yield ChatStreamChunk(
                content=error_response,
                session_id=history._session_id if history else "",
                is_complete=True
            )
        
        finally:
            logging.getLogger("uvicorn.info").info("Step 8: Persisting assistant's response to chat history")
            if history and assistant_response.strip():
                try:
                    assistant_message = AIMessage(content=assistant_response)
                    await history.aadd_messages([assistant_message])
                except Exception as persist_error:
                    logging.getLogger("uvicorn.error").error(f"Failed to persist assistant message: {persist_error}")
            
            logging.getLogger("uvicorn.info").info("Step 9: Generating conversation name for new conversations")
            if history and assistant_response.strip():
                try:
                    await self._generate_conversation_name_if_needed(history, request.agent)
                except Exception as name_error:
                    logging.getLogger("uvicorn.error").error(f"Failed to generate conversation name: {name_error}")
            
            logging.getLogger("uvicorn.info").info(f"Step 10: Sending final completion chunk with session_id {history._session_id if history else 'None'}")
            if history:
                yield ChatStreamChunk(
                    content="",
                    session_id=history._session_id,
                    is_complete=True
                )

    async def get_models(self) -> dict[str, list[dict[str, str]]]:
        def model_info(model: LLMModel) -> dict[str, str]:
            return {"value": model.value, "label": model.value}

        models = {
            "openai": [model_info(model) for model in OPENAI_MODELS],
            "google_genai": [model_info(model) for model in GEMINI_MODELS],
            "anthropic": [model_info(model) for model in CLAUDE_MODELS],
            "xai": [model_info(model) for model in GROK_MODELS],
            "mistralai": [model_info(model) for model in MISTRAL_MODELS],
            "nvidia": [model_info(model) for model in NVIDIA_MODELS],
        }
        return models