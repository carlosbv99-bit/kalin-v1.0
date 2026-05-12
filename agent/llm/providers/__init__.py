"""
LLM Providers: Implementaciones de diferentes servicios LLM.

Soportados:
- Ollama (local)
- OpenAI (cloud)
- Anthropic (cloud)
- Azure (cloud)
- HuggingFace (cloud)
- Groq (cloud - gratis, ultra-rápido)
- Google Gemini (cloud - gratis con límites)
- Mistral AI (cloud - económico)
- Xiaomi MiMo (cloud - gratuito temporalmente)
"""

from agent.llm.providers.base_provider import BaseLLMProvider, LLMResponse
from agent.llm.providers.ollama_provider import OllamaProvider
from agent.llm.providers.openai_provider import OpenAIProvider
from agent.llm.providers.anthropic_provider import AnthropicProvider
from agent.llm.providers.groq_provider import GroqProvider
from agent.llm.providers.gemini_provider import GeminiProvider
from agent.llm.providers.mistral_provider import MistralProvider
from agent.llm.providers.mimo_provider import MimoProvider

__all__ = [
    "BaseLLMProvider",
    "LLMResponse",
    "OllamaProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "GroqProvider",
    "GeminiProvider",
    "MistralProvider",
    "MimoProvider",
]
