"""
LLM Providers: Implementaciones de diferentes servicios LLM.

Soportados:
- Ollama (local)
- OpenAI (cloud)
- Anthropic (cloud)
- Azure (cloud)
- HuggingFace (cloud)
"""

from agent.llm.providers.base_provider import BaseLLMProvider, LLMResponse
from agent.llm.providers.ollama_provider import OllamaProvider
from agent.llm.providers.openai_provider import OpenAIProvider
from agent.llm.providers.anthropic_provider import AnthropicProvider

__all__ = [
    "BaseLLMProvider",
    "LLMResponse",
    "OllamaProvider",
    "OpenAIProvider",
    "AnthropicProvider",
]
