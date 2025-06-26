from enum import Enum, auto


class LLMModel(str, Enum):
    # https://platform.openai.com/docs/models
    O3 = "o3"
    O3_MINI = "o3_mini"
    O1 = "o1"
    O1_MINI = "o1_mini"
    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_3_5_TURBO = "gpt-3.5-turbo"

    # https://ai.google.dev/gemini-api/docs/models
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro"

    # https://docs.anthropic.com/en/docs/about-claude/models/overview
    CLAUDE_OPUS_4_0 = "claude-opus-4-0"
    CLAUDE_SONNET_4_0 = "claude-sonnet-4-0"
    CLAUDE_SONNET_3_7 = "claude-3-7-sonnet-latest"
    CLAUDE_SONNET_3_5 = "claude-3-5-sonnet-latest"
    CLAUDE_HAIKU_3_5 = "claude-3-5-haiku-latest"
    CLAUDE_OPUS_3_0 = "claude-3-opus-latest	"

    # https://docs.x.ai/docs/models
    GROK_3 = "grok-3"
    GROK_3_FAST = "grok-3-fast"
    GROK_3_MINI = "grok-3-mini"
    GROK_3_MINI_FAST = "grok-3-mini-fast"
    GROK_2_1212 = "grok-2-1212"
    GROK_2_VISION_1212 = "grok-2-vision-1212"
    GROK_3_MINI_BETA = "grok-3-mini-beta"

    # https://docs.mistral.ai/getting-started/models/models_overview/
    MISTRAL_SMALL_LATEST = "mistral-small-latest"
    MISTRAL_MEDIUM_LATEST = "mistral-medium-latest"
    MISTRAL_LARGE_LATEST = "mistral-large-latest"
    DEVSTRAL_SMALL_LATEST = "devstral-small-latest"
    MAGISTRAL_SMALL_LATEST = "magistral-small-latest"
    MAGISTRAL_MEDIUM_LATEST = "magistral-medium-latest"

    # https://build.nvidia.com/models
    NVIDIA_NEVA_22B = "nvidia/neva-22b"
    NVIDIA_LLAMA_3_1_NEMOTRON_NANO_4B_V1_1 = "nvidia/llama-3.1-nemotron-nano-4b-v1.1"

OPENAI_MODELS = {
    LLMModel.O3,
    LLMModel.O3_MINI,
    LLMModel.O1,
    LLMModel.O1_MINI,
    LLMModel.GPT_4,
    LLMModel.GPT_4O,
    LLMModel.GPT_4O_MINI,
    LLMModel.GPT_3_5_TURBO,
}

GEMINI_MODELS = {
    LLMModel.GEMINI_1_5_PRO,
    LLMModel.GEMINI_2_0_FLASH,
    LLMModel.GEMINI_2_5_FLASH,
    LLMModel.GEMINI_2_5_PRO,
}

CLAUDE_MODELS = {
    LLMModel.CLAUDE_OPUS_4_0,
    LLMModel.CLAUDE_SONNET_4_0,
    LLMModel.CLAUDE_SONNET_3_7,
    LLMModel.CLAUDE_SONNET_3_5,
    LLMModel.CLAUDE_HAIKU_3_5,
    LLMModel.CLAUDE_OPUS_3_0,
}

GROK_MODELS = {
    LLMModel.GROK_2_1212,
    LLMModel.GROK_2_VISION_1212,
    LLMModel.GROK_3_MINI_BETA,
    LLMModel.GROK_3,
    LLMModel.GROK_3_FAST,
    LLMModel.GROK_3_MINI,
    LLMModel.GROK_3_MINI_FAST,
}

MISTRAL_MODELS = {
    LLMModel.MISTRAL_SMALL_LATEST,
    LLMModel.MISTRAL_MEDIUM_LATEST,
    LLMModel.MISTRAL_LARGE_LATEST,
    LLMModel.DEVSTRAL_SMALL_LATEST,
    LLMModel.MAGISTRAL_SMALL_LATEST,
    LLMModel.MAGISTRAL_MEDIUM_LATEST,
}

NVIDIA_MODELS = {
    LLMModel.NVIDIA_NEVA_22B,
    LLMModel.NVIDIA_LLAMA_3_1_NEMOTRON_NANO_4B_V1_1
}