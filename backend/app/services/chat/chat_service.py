from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.prebuilt import create_react_agent
from app.classes.chat import ChatMessage, ChatRequest, ChatResponse
from app.core.config import settings
from app.utils.chat import chat_utils
from app.core.constants import LLMModel, OPENAI_MODELS, GEMINI_MODELS, CLAUDE_MODELS, GROK_MODELS, MISTRAL_MODELS, NVIDIA_MODELS
from app.services.agent.agent_service import AgentService

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

    async def generate_chat_response(self, request: ChatRequest) -> ChatResponse:
        agent = await AgentService().get_agent(request.agent)
        model = self._get_chat_model(agent.model)

        messages = [ChatMessage(role="system", content=agent.persona)]
        messages.extend(request.messages)
        lc_messages = chat_utils.convert_chat_messages(messages)

        agent_executor = create_react_agent(model, [])
        response = agent_executor.invoke({"messages": lc_messages})

        return ChatResponse(response=response["messages"][-1].content)
    
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



