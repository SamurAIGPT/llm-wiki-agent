"""LLM provider factory for multi-provider support.

Supports OpenAI and MiniMax (via OpenAI-compatible API).
"""

import os

from langchain.chat_models import ChatOpenAI


# Provider constants
PROVIDER_OPENAI = "openai"
PROVIDER_MINIMAX = "minimax"

SUPPORTED_PROVIDERS = [PROVIDER_OPENAI, PROVIDER_MINIMAX]

# Default models per provider
DEFAULT_MODELS = {
    PROVIDER_OPENAI: "gpt-3.5-turbo",
    PROVIDER_MINIMAX: "MiniMax-M2.5",
}

# Available models per provider
AVAILABLE_MODELS = {
    PROVIDER_OPENAI: [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo",
    ],
    PROVIDER_MINIMAX: [
        "MiniMax-M2.5",
        "MiniMax-M2.5-highspeed",
    ],
}

# MiniMax API base URL (OpenAI-compatible)
MINIMAX_API_BASE = "https://api.minimax.io/v1"


def clamp_temperature(temperature, provider):
    """Clamp temperature to valid range for the given provider.

    MiniMax accepts temperature in [0, 1.0].
    OpenAI accepts temperature in [0, 2.0].
    """
    if provider == PROVIDER_MINIMAX:
        return max(0.0, min(temperature, 1.0))
    return temperature


def create_chat_model(provider=None, api_key=None, model_name=None,
                      temperature=0.2):
    """Create a LangChain ChatOpenAI instance for the specified provider.

    Args:
        provider: LLM provider name ("openai" or "minimax").
        api_key: API key for the provider.
        model_name: Model name to use. Defaults to provider's default.
        temperature: Sampling temperature.

    Returns:
        ChatOpenAI instance configured for the specified provider.
    """
    if provider is None:
        provider = PROVIDER_OPENAI

    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported: {SUPPORTED_PROVIDERS}"
        )

    if model_name is None:
        model_name = DEFAULT_MODELS[provider]

    temperature = clamp_temperature(temperature, provider)

    if provider == PROVIDER_MINIMAX:
        if not api_key:
            api_key = os.environ.get("MINIMAX_API_KEY", "")
        return ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=MINIMAX_API_BASE,
            model_name=model_name,
            temperature=temperature,
        )

    # OpenAI (default)
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    return ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
    )
