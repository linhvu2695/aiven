from fastapi import UploadFile
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from app.classes.chat import ChatFileContent, ChatFileUrl, ChatMessage, ChatRequest, ChatResponse
from app.core.config import settings
from app.utils.chat import chat_utils
from app.core.constants import LLMModel, OPENAI_MODELS, GEMINI_MODELS, CLAUDE_MODELS, GROK_MODELS, MISTRAL_MODELS, NVIDIA_MODELS
from app.services.agent.agent_service import AgentService
import base64
import mimetypes
import re
from typing import Optional

GPT_DEFAULT_MODEL = LLMModel.GPT_4O_MINI

class ChatService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance') or cls._instance is None:
            cls._instance = super(ChatService, cls).__new__(cls)
        return cls._instance
    
    def _get_chat_model(self, model_name) -> BaseChatModel:
        if model_name in OPENAI_MODELS:
            return init_chat_model(model=model_name, model_provider="openai", api_key=settings.openai_api_key)
        if model_name in GEMINI_MODELS:
            return init_chat_model(model=model_name, model_provider="google_genai", api_key=settings.gemini_api_key)
        if model_name in CLAUDE_MODELS:
            return init_chat_model(model=model_name, model_provider="anthropic", api_key=settings.anthropic_api_key)
        if model_name in GROK_MODELS:
            return init_chat_model(model=model_name, model_provider="xai", api_key=settings.xai_api_key)
        if model_name in MISTRAL_MODELS:
            return init_chat_model(model=model_name, model_provider="mistralai", api_key=settings.mistral_api_key)
        if model_name in NVIDIA_MODELS:
            return init_chat_model(model=model_name, model_provider="nvidia", api_key=settings.nvidia_api_key)
        
        return init_chat_model(model=GPT_DEFAULT_MODEL, model_provider="openai", api_key=settings.openai_api_key)

    def _parse_format_error(self, error_message: str) -> str:
        """Parse LLM provider error message to extract supported formats and return user-friendly message."""
        # Look for patterns like 'image/jpeg', 'image/png', etc. in the error message
        format_pattern = r"'(image/\w+)'"
        matches = re.findall(format_pattern, error_message)
        
        if matches:
            # Convert mime types to user-friendly format names
            format_names = [fmt.split('/')[1].upper() for fmt in matches]
            supported_list = ", ".join(format_names)
            return f"❌ File Upload Error: The uploaded image format is not supported by this model. Supported formats: {supported_list}"
        
        # Fallback for other format-related errors
        if "media_type" in error_message.lower() or "format" in error_message.lower():
            return "❌ File Upload Error: The uploaded file format is not supported by this model. Please try a different file format."
        
        return f"❌ File Upload Error: {error_message}"

    def _get_file_type_category(self, mime_type: str) -> str:
        """Determine the file type category based on mime type."""
        if not mime_type:
            return "file"
        
        if mime_type.startswith("image/"):
            return "image"
        elif mime_type.startswith("audio/"):
            return "audio"
        elif mime_type.startswith("video/"):
            return "video"
        elif mime_type.startswith("text/"):
            return "text"
        elif mime_type in ["application/pdf"]:
            return "document"
        elif mime_type.startswith("application/"):
            return "application"
        else:
            return "file"

    async def _get_file_content(self, file: UploadFile) -> Optional[ChatFileContent]:
        """Convert uploaded file to ChatFileContent with base64 encoding."""
        if not file or not file.filename:
            return None
        
        try:
            content = await file.read()
            mime_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
            file_type = self._get_file_type_category(mime_type)
            
            # Convert to base64
            base64_data = base64.b64encode(content).decode('utf-8')
            
            # Reset file pointer for potential future reads
            await file.seek(0)
            
            return ChatFileContent(
                type=file_type,
                source_type="base64",
                data=base64_data,
                mime_type=mime_type
            )
            
        except Exception as e:
            print(f"Error processing file {file.filename}: {str(e)}")
            return None

    async def _get_trace_metadata(self, request: ChatRequest) -> dict:
        agent = await AgentService().get_agent(request.agent)

        trace_metadata = {
                "agent_id": request.agent,
                "agent_name": agent.name,
                "model": agent.model,
                "message_count": len(request.messages),
                "has_files": bool(request.files),
                "file_count": len(request.files) if request.files else 0
            }
        return trace_metadata
    
    async def generate_chat_response(self, request: ChatRequest) -> ChatResponse:
        try:
            agent = await AgentService().get_agent(request.agent)
            model = self._get_chat_model(agent.model)

            messages = [ChatMessage(role="system", content=agent.persona)]
            messages.extend(request.messages)
            lc_messages = chat_utils.convert_chat_messages(messages)
            
            # Process uploaded files if any
            if request.files:
                file = request.files[0] # expect only one file
                file_content = await self._get_file_content(file)
                    
                if file_content:
                    file_message = HumanMessage(content=[
                        file_content.model_dump()
                    ])
                    lc_messages.append(file_message)

            # Add custom metadata and tags to the LLM call for better tracing
            config = RunnableConfig(
                metadata=await self._get_trace_metadata(request),
                tags=[
                    self.__class__.__name__,
                ],
                run_name=f"Chat with {agent.name}"
            )

            # Invoke!
            response = model.invoke(lc_messages, config=config)
            return ChatResponse(response=str(response.content))
            
        except Exception as e:
            error_msg = str(e)
            
            # Check for specific format/media type errors
            if any(keyword in error_msg.lower() for keyword in ["media_type", "format", "image/", "audio/", "video/"]):
                return ChatResponse(response=self._parse_format_error(error_msg))
            
            # Handle other API errors
            if "BadRequestError" in str(type(e)) or "400" in error_msg:
                return ChatResponse(response=f"❌ Request Error: There was an issue with your request. Please check your input and try again.")
            
            # Generic error handling
            return ChatResponse(response=f"❌ An error occurred while processing your request. Please try again or contact support if the issue persists.")
    
    async def get_models(self) -> dict[str, list[dict[str, str]]]:
        def model_info(model: LLMModel) -> dict[str, str]: return {"value": model.value, "label": model.value}

        models = {
            "openai": [model_info(model) for model in OPENAI_MODELS],
            "google_genai": [model_info(model) for model in GEMINI_MODELS],
            "anthropic": [model_info(model) for model in CLAUDE_MODELS],
            "xai": [model_info(model) for model in GROK_MODELS],
            "mistralai": [model_info(model) for model in MISTRAL_MODELS],
            "nvidia": [model_info(model) for model in NVIDIA_MODELS]
        }
        return models



