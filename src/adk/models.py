"""
Model Configuration - Flexible LLM Backend for ADK Agents

Supports multiple model providers:
- Gemini (native ADK support, recommended)
- HuggingFace (via LiteLLM)
- OpenAI (via LiteLLM)
"""

import os
import time
import logging
from enum import Enum
from typing import Optional, Union, Any

logger = logging.getLogger(__name__)


# ============================================================================
# LITELLM TOKEN TRACKING CALLBACK
# ============================================================================

class TokenTrackingCallback:
    """
    LiteLLM callback handler that logs token consumption per agent.
    Integrates with TokenConsumptionLogger for prod-grade monitoring.
    """

    def __init__(self):
        self._current_agent = "unknown"
        self._current_session = ""
        self._current_user = ""

    def set_context(self, agent_name: str = "", session_id: str = "", user_id: str = ""):
        """Set the current agent context for token attribution"""
        self._current_agent = agent_name
        self._current_session = session_id
        self._current_user = user_id

    def success_handler(self, kwargs, completion_response, start_time, end_time):
        """Called by LiteLLM after successful completion"""
        try:
            from src.adk.tools import get_token_logger

            usage = getattr(completion_response, 'usage', None)
            if not usage:
                # Try dict access
                if isinstance(completion_response, dict):
                    usage = completion_response.get("usage", {})
                else:
                    return

            tokens_in = getattr(usage, 'prompt_tokens', 0) or (usage.get('prompt_tokens', 0) if isinstance(usage, dict) else 0)
            tokens_out = getattr(usage, 'completion_tokens', 0) or (usage.get('completion_tokens', 0) if isinstance(usage, dict) else 0)

            model = kwargs.get("model", "unknown")
            latency = int((end_time - start_time).total_seconds() * 1000) if end_time and start_time else 0

            # Determine provider from model string
            provider = "unknown"
            if "gemini" in model.lower():
                provider = "gemini"
            elif "huggingface/" in model:
                provider = "huggingface"
            elif "openai/" in model or "gpt" in model.lower():
                provider = "openai"
            elif "ollama/" in model:
                provider = "ollama"

            # Extract query preview
            messages = kwargs.get("messages", [])
            query_preview = ""
            if messages:
                last_user = [m for m in messages if m.get("role") == "user"]
                if last_user:
                    query_preview = str(last_user[-1].get("content", ""))[:500]

            # Extract response preview
            response_preview = ""
            if hasattr(completion_response, 'choices') and completion_response.choices:
                first_choice = completion_response.choices[0]
                if hasattr(first_choice, 'message') and first_choice.message:
                    response_preview = str(first_choice.message.content or "")[:500]

            get_token_logger().log(
                agent_name=self._current_agent,
                model_name=model,
                model_provider=provider,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                query_preview=query_preview,
                response_preview=response_preview,
                session_id=self._current_session,
                user_id=self._current_user,
                latency_ms=latency,
                status="success"
            )

        except Exception as e:
            logger.warning(f"Token tracking callback error: {e}")

    def failure_handler(self, kwargs, completion_response, start_time, end_time):
        """Called by LiteLLM after failed completion"""
        try:
            from src.adk.tools import get_token_logger

            model = kwargs.get("model", "unknown")
            latency = int((end_time - start_time).total_seconds() * 1000) if end_time and start_time else 0
            error_msg = str(completion_response) if completion_response else "Unknown error"

            get_token_logger().log(
                agent_name=self._current_agent,
                model_name=model,
                model_provider="unknown",
                tokens_in=0,
                tokens_out=0,
                session_id=self._current_session,
                user_id=self._current_user,
                latency_ms=latency,
                status="error",
                error_message=error_msg[:500]
            )
        except Exception as e:
            logger.warning(f"Token tracking failure handler error: {e}")


# Global token tracking callback
_token_callback = TokenTrackingCallback()


def get_token_callback() -> TokenTrackingCallback:
    """Get the global token tracking callback"""
    return _token_callback


def setup_litellm_callbacks():
    """Register token tracking callbacks with LiteLLM"""
    try:
        import litellm
        litellm.success_callback = [_token_callback.success_handler]
        litellm.failure_callback = [_token_callback.failure_handler]
        logger.info("LiteLLM token tracking callbacks registered")
    except ImportError:
        logger.warning("LiteLLM not available - token tracking via callbacks disabled")
    except Exception as e:
        logger.warning(f"Failed to setup LiteLLM callbacks: {e}")


class ModelProvider(str, Enum):
    """Supported model providers"""
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"
    OLLAMA = "ollama"  # FREE - Local LLM


# Default models for each provider
DEFAULT_MODELS = {
    ModelProvider.GEMINI: "gemini-2.0-flash",
    ModelProvider.HUGGINGFACE: "mistralai/Mistral-7B-Instruct-v0.2",
    ModelProvider.OPENAI: "gpt-4o",
    ModelProvider.OLLAMA: "llama3.1",  # FREE - Runs locally
}

# FREE Model Options (No API Key / No Cost)
FREE_MODELS = {
    "ollama": {
        "llama3.1": "Best quality - Meta Llama 3.1 8B (local, FREE)",
        "llama3.1:70b": "Highest quality - Llama 3.1 70B (requires 48GB+ RAM)",
        "codellama": "Best for code generation (local, FREE)",
        "mistral": "Fast and efficient - Mistral 7B (local, FREE)",
        "deepseek-coder": "Specialized for coding tasks (local, FREE)",
    },
    "huggingface_free": {
        "mistralai/Mistral-7B-Instruct-v0.2": "Mistral 7B - Excellent quality (FREE tier)",
        "HuggingFaceH4/zephyr-7b-beta": "Zephyr 7B - Great for chat (FREE tier)",
        "microsoft/Phi-3-mini-4k-instruct": "Phi-3 Mini - Fast and compact (FREE tier)",
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0": "TinyLlama - Very fast (FREE tier)",
        "codellama/CodeLlama-7b-Instruct-hf": "CodeLlama - For code (FREE tier)",
    }
}

# Role-based temperature settings (lower = more consistent, higher = more creative)
ROLE_TEMPERATURES = {
    "hr": 0.3,           # HR needs consistency in routing
    "engineer": 0.5,     # Engineer needs balance for code generation
    "analyst": 0.4,      # Analyst needs precision
    "pmo": 0.3,          # PMO needs consistency
    "security": 0.2,     # Security needs high precision
    "devops": 0.2,       # DevOps needs precision
    "marketing": 0.7,    # Marketing needs creativity for content generation
    "default": 0.7,      # Default for general use
}


def get_model_provider() -> ModelProvider:
    """Get configured model provider from environment"""
    provider = os.getenv("MODEL_PROVIDER", "openai").lower()
    try:
        return ModelProvider(provider)
    except ValueError:
        logger.warning(f"Unknown provider '{provider}', defaulting to OpenAI")
        return ModelProvider.OPENAI


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
    elif provider == ModelProvider.OLLAMA:
        return _get_ollama_model(model_name, temperature)
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

    # Remove GOOGLE_API_KEY to prevent fallback to Gemini
    os.environ.pop("GOOGLE_API_KEY", None)

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


def _get_ollama_model(model_name: Optional[str] = None, temperature: Optional[float] = None) -> Any:
    """
    Get Ollama model via LiteLLM wrapper.
    Ollama runs locally - completely FREE, no API key needed.

    Prerequisites:
    1. Install Ollama: https://ollama.ai/download
    2. Pull a model: ollama pull llama3.1
    3. Ollama runs automatically on localhost:11434
    """
    from google.adk.models.lite_llm import LiteLlm

    model = model_name or os.getenv("OLLAMA_MODEL_NAME", DEFAULT_MODELS[ModelProvider.OLLAMA])
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    # Set Ollama base URL for LiteLLM
    os.environ["OLLAMA_API_BASE"] = ollama_host

    logger.info(f"Using Ollama model (FREE, local): {model} at {ollama_host}")

    # LiteLLM format for Ollama
    litellm_model = f"ollama/{model}"

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

        elif provider == ModelProvider.OLLAMA:
            # Ollama doesn't need API key - it's local
            result["model"] = os.getenv("OLLAMA_MODEL_NAME", DEFAULT_MODELS[ModelProvider.OLLAMA])
            result["status"] = "configured"
            result["note"] = "FREE - Runs locally. Ensure Ollama is running: ollama serve"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def list_free_models() -> dict:
    """
    List all available FREE model options.
    Use this to choose models that don't require payment.

    Returns:
        Dict with free model options for each provider
    """
    return {
        "huggingface": {
            "provider": "HuggingFace Inference API",
            "cost": "FREE (with free API token)",
            "setup": "Get token from https://huggingface.co/settings/tokens",
            "recommended": "mistralai/Mistral-7B-Instruct-v0.2",
            "models": FREE_MODELS["huggingface_free"]
        },
        "ollama": {
            "provider": "Ollama (Local)",
            "cost": "FREE (runs on your machine)",
            "setup": "Install from https://ollama.ai/download, then: ollama pull llama3.1",
            "recommended": "llama3.1",
            "models": FREE_MODELS["ollama"]
        },
        "gemini": {
            "provider": "Google Gemini",
            "cost": "FREE tier available (limited)",
            "setup": "Get API key from https://aistudio.google.com/apikey",
            "recommended": "gemini-2.0-flash",
            "models": {"gemini-2.0-flash": "Fast and capable (FREE tier)"}
        }
    }


def get_best_free_model() -> tuple:
    """
    Get the best FREE model configuration.

    Returns:
        Tuple of (provider, model_name, description)
    """
    # Check if Ollama is running (best free option)
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            return ("ollama", "llama3.1", "Best quality - Local Ollama (FREE)")
    except:
        pass

    # Fall back to HuggingFace (also free)
    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    if hf_key and not hf_key.startswith("hf_xxx"):
        return ("huggingface", "mistralai/Mistral-7B-Instruct-v0.2", "Mistral 7B via HuggingFace (FREE)")

    # Fall back to Gemini free tier
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        return ("gemini", "gemini-2.0-flash", "Gemini Flash (FREE tier)")

    return ("huggingface", "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "TinyLlama (FREE, no key needed)")


# Auto-register LiteLLM callbacks on import
setup_litellm_callbacks()


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
