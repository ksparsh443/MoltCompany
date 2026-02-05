"""
Model Configuration - Flexible LLM Backend for ADK Agents

Supports multiple model providers:
- Gemini (native ADK support, recommended)
- HuggingFace (via LiteLLM)
- OpenAI (via LiteLLM)
"""

import os
import logging
from enum import Enum
from typing import Optional, Union, Any

logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
    """Supported model providers"""
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"


# Default models for each provider
DEFAULT_MODELS = {
    ModelProvider.GEMINI: "gemini-2.0-flash",
    ModelProvider.HUGGINGFACE: "mistralai/Mistral-7B-Instruct-v0.2",
    ModelProvider.OPENAI: "gpt-4o",
}

# Role-based temperature settings (lower = more consistent, higher = more creative)
ROLE_TEMPERATURES = {
    "hr": 0.3,           # HR needs consistency in routing
    "engineer": 0.5,     # Engineer needs balance for code generation
    "analyst": 0.4,      # Analyst needs precision
    "pmo": 0.3,          # PMO needs consistency
    "security": 0.2,     # Security needs high precision
    "devops": 0.2,       # DevOps needs precision
    "default": 0.7,      # Default for general use
}


def get_model_provider() -> ModelProvider:
    """Get configured model provider from environment"""
    provider = os.getenv("MODEL_PROVIDER", "gemini").lower()
    try:
        return ModelProvider(provider)
    except ValueError:
        logger.warning(f"Unknown provider '{provider}', defaulting to Gemini")
        return ModelProvider.GEMINI


def get_model(
    provider: Optional[Union[ModelProvider, str]] = None,
    model_name: Optional[str] = None,
    role: Optional[str] = None,
) -> Any:
    """
    Get model instance for ADK agent.

    Args:
        provider: Model provider (gemini, huggingface, openai).
                  Defaults to MODEL_PROVIDER env var.
        model_name: Specific model name. Defaults to provider's default model.
        role: Agent role for temperature adjustment (hr, engineer, analyst, etc.)

    Returns:
        Model instance compatible with ADK LlmAgent:
        - String for Gemini (native support)
        - LiteLlm wrapper for other providers

    Examples:
        # Use default provider (from env)
        model = get_model()

        # Use specific provider
        model = get_model(provider="huggingface")

        # Use specific model with role-based temperature
        model = get_model(provider="gemini", model_name="gemini-1.5-pro", role="engineer")
    """
    # Resolve provider
    if provider is None:
        provider = get_model_provider()
    elif isinstance(provider, str):
        provider = ModelProvider(provider.lower())

    # Get temperature based on role
    temperature = ROLE_TEMPERATURES.get(role, ROLE_TEMPERATURES["default"]) if role else None

    if provider == ModelProvider.GEMINI:
        return _get_gemini_model(model_name, temperature)
    elif provider == ModelProvider.HUGGINGFACE:
        return _get_huggingface_model(model_name, temperature)
    elif provider == ModelProvider.OPENAI:
        return _get_openai_model(model_name, temperature)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _get_gemini_model(model_name: Optional[str] = None, temperature: Optional[float] = None) -> str:
    """
    Get Gemini model string for native ADK support.

    Note: Gemini models are specified as strings in ADK.
    Temperature is handled at the agent level, not model level.
    """
    model = model_name or os.getenv("GEMINI_MODEL_NAME", DEFAULT_MODELS[ModelProvider.GEMINI])

    # Validate API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found. Please set it in .env file.\n"
            "Get your API key from: https://aistudio.google.com/apikey"
        )

    logger.info(f"Using Gemini model: {model}")
    return model


def _get_huggingface_model(model_name: Optional[str] = None, temperature: Optional[float] = None) -> Any:
    """
    Get HuggingFace model via LiteLLM wrapper.
    """
    from google.adk.models.lite_llm import LiteLlm

    model = model_name or os.getenv("HF_MODEL_NAME", DEFAULT_MODELS[ModelProvider.HUGGINGFACE])

    # Validate API key
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key or api_key.startswith("hf_xxx"):
        raise ValueError(
            "HUGGINGFACE_API_KEY not found or invalid. Please set it in .env file.\n"
            "Get your free API key from: https://huggingface.co/settings/tokens"
        )

    # Set environment variable for LiteLLM
    os.environ["HUGGINGFACE_API_KEY"] = api_key

    logger.info(f"Using HuggingFace model via LiteLLM: {model}")

    # LiteLLM format for HuggingFace
    litellm_model = f"huggingface/{model}"

    return LiteLlm(model=litellm_model)


def _get_openai_model(model_name: Optional[str] = None, temperature: Optional[float] = None) -> Any:
    """
    Get OpenAI model via LiteLLM wrapper.
    """
    from google.adk.models.lite_llm import LiteLlm

    model = model_name or os.getenv("OPENAI_MODEL_NAME", DEFAULT_MODELS[ModelProvider.OPENAI])

    # Validate API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Please set it in .env file."
        )

    # Set environment variable for LiteLLM
    os.environ["OPENAI_API_KEY"] = api_key

    logger.info(f"Using OpenAI model via LiteLLM: {model}")

    # LiteLLM format for OpenAI
    litellm_model = f"openai/{model}"

    return LiteLlm(model=litellm_model)


def get_model_for_role(role: str) -> Any:
    """
    Convenience function to get model with role-based temperature.

    Args:
        role: Agent role (hr, engineer, analyst, pmo, security, devops)

    Returns:
        Model instance configured for the specified role
    """
    return get_model(role=role)


def validate_model_config() -> dict:
    """
    Validate current model configuration.

    Returns:
        Dict with validation results
    """
    result = {
        "provider": None,
        "model": None,
        "status": "unknown",
        "error": None
    }

    try:
        provider = get_model_provider()
        result["provider"] = provider.value

        if provider == ModelProvider.GEMINI:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                result["model"] = os.getenv("GEMINI_MODEL_NAME", DEFAULT_MODELS[ModelProvider.GEMINI])
                result["status"] = "configured"
            else:
                result["status"] = "missing_api_key"
                result["error"] = "GOOGLE_API_KEY not set"

        elif provider == ModelProvider.HUGGINGFACE:
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            if api_key and not api_key.startswith("hf_xxx"):
                result["model"] = os.getenv("HF_MODEL_NAME", DEFAULT_MODELS[ModelProvider.HUGGINGFACE])
                result["status"] = "configured"
            else:
                result["status"] = "missing_api_key"
                result["error"] = "HUGGINGFACE_API_KEY not set or invalid"

        elif provider == ModelProvider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                result["model"] = os.getenv("OPENAI_MODEL_NAME", DEFAULT_MODELS[ModelProvider.OPENAI])
                result["status"] = "configured"
            else:
                result["status"] = "missing_api_key"
                result["error"] = "OPENAI_API_KEY not set"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


# Quick test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("Model Configuration Test")
    print("=" * 50)

    config = validate_model_config()
    print(f"Provider: {config['provider']}")
    print(f"Model: {config['model']}")
    print(f"Status: {config['status']}")
    if config['error']:
        print(f"Error: {config['error']}")

    if config['status'] == 'configured':
        print("\n✅ Configuration is valid!")
        try:
            model = get_model()
            print(f"Model instance: {model}")
        except Exception as e:
            print(f"❌ Error creating model: {e}")
    else:
        print(f"\n❌ Configuration issue: {config['error']}")
