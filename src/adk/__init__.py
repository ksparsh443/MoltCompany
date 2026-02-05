"""
Google ADK-based AI Company Agent System

This package provides a multi-agent AI system built on Google's Agent Development Kit (ADK).
Supports both Gemini and HuggingFace models via LiteLLM.
"""

from src.adk.models import get_model, ModelProvider
from src.adk.runner import AICompanyRunner, create_runner

__all__ = [
    "get_model",
    "ModelProvider",
    "AICompanyRunner",
    "create_runner",
]

__version__ = "2.0.0"
