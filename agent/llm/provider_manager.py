"""
Manager de proveedores LLM.
Gestiona múltiples proveedores, fallbacks, routing, costos.
+ CONTROL DE OUTPUT (validación + limpieza + retry)
"""

import os
import re
from typing import Optional, List, Dict
from agent.llm.config import LLMConfig, ProviderType
from agent.llm.providers.base_provider import LLMResponse
from agent.llm.providers.ollama_provider import OllamaProvider
from agent.llm.providers.openai_provider import OpenAIProvider
from agent.llm.providers.anthropic_provider import AnthropicProvider
from agent.llm.providers.groq_provider import GroqProvider
from agent.llm.providers.mimo_provider import MimoProvider

DEBUG_MODE = False  # FORZADO A FALSE - Logs cortos

# =========================
# PROMPTS CONTROLADOS
# =========================

SYSTEM_CODE = """
Genera SOLO código. Sin texto extra. Sin markdown.
"""

SYSTEM_CODE_DETAILED = """
ERES UN MOTOR DE GENERACIÓN DE CÓDIGO UNIVERSAL.

INSTRUCCIÓN MAESTRA:
- Analiza el lenguaje solicitado por el usuario (C, C++, Java, Python, HTML, JS, etc.).
- Genera ÚNICAMENTE el código fuente correspondiente a ese lenguaje.
- Si el usuario pide C o C++, NO uses Python ni librerías de alto nivel. Usa sintaxis nativa.
- NO incluyas NUNCA texto conversacional, saludos, explicaciones o markdown (```).
- El output debe ser 100% código ejecutable o estructural válido.
- Si el usuario pide algo visual en un lenguaje de consola (como C), usa la librería estándar o gráficos básicos si es posible.
- Si el usuario pide una modificación, genera el CÓDIGO COMPLETO actualizado, no solo el fragmento.

PROHIBIDO:
- Usar marcadores como [INICIO DEL CÓDIGO] o [FIN DEL CÓDIGO].
- Decir "Aquí tienes el código..."
- Decir "Espero que te sirva..."
"""

SYSTEM_CHAT = """
Eres un asistente útil. Responde claro y breve.
"""

# =========================
# VALIDACIÓN
# =========================

def is_valid_code(output: str) -> bool:
    # Validación minimalista temporal
    if not output.strip():
        return False

    return True


def clean_llm_output(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    # remove markdown fences
    text = re.sub(r"^```[\w]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)

    # remove accidental assistant artifacts
    garbage_lines = [
        "obj['response']",
        'obj["response"]',
    ]

    lines = []

    for line in text.splitlines():
        clean = line.strip()

        if clean in garbage_lines:
            continue

        lines.append(line)

    return "\n".join(lines).strip()


# COMENTADO - CLEANER AGRESIVO DESACTIVADO
# def clean_code_response(text: str) -> str:
#     if not text:
#         return ""
#
#     # quitar markdown
#     text = text.replace("```dart", "")
#     text = text.replace("```", "")
#
#     # quitar explicaciones comunes
#     lines = text.splitlines()
#
#     cleaned = []
#     for line in lines:
#         if any(x in line.lower() for x in [
#             "aquí tienes",
#             "he corregido",
#             "explicación",
#             "este código",
#         ]):
#             continue
#         cleaned.append(line)
#
#     return "\n".join(cleaned).strip()


class LLMProviderManager:
    """Manager central de proveedores LLM"""

    def __init__(self):
        self.providers = {}
        self.config = LLMConfig()
        self._initialize_providers()
        self.stats = {
            "total_requests": 0,
            "total_cost": 0.0,
            "provider_usage": {},
            "errors": {}
        }

    def _initialize_providers(self):
        provider_classes = {
            ProviderType.OLLAMA: OllamaProvider,
            ProviderType.OPENAI: OpenAIProvider,
            ProviderType.ANTHROPIC: AnthropicProvider,
            ProviderType.GROQ: GroqProvider,
            ProviderType.MIMO: MimoProvider,
        }

        for provider_type, ProviderClass in provider_classes.items():
            config = LLMConfig.PROVIDERS[provider_type]
            try:
                self.providers[provider_type] = ProviderClass(config)
            except Exception as e:
                print(f"⚠️ No se pudo inicializar {provider_type.value}: {e}")

    def generate(
        self,
        prompt: str,
        use_case: str = "fix",
        max_tokens: Optional[int] = None
    ) -> Optional[LLMResponse]:

        selected_provider = self.config.get_primary_provider(use_case)

        if use_case not in self.config.USE_CASE_ROUTER:
            use_case = "fix"

        route = self.config.USE_CASE_ROUTER[use_case]

        fallback_providers = [
            p for p in self.config.get_fallback_order()
            if p != selected_provider
        ]

        if max_tokens is None:
            max_tokens = route.get("max_tokens", 1200)

        temperature = route.get("temperature", 0.2)

        providers_to_try = [selected_provider] + fallback_providers

        self.stats["total_requests"] += 1

        # =========================
        # SELECCIÓN DE MODO
        # =========================

        # Usar SYSTEM_CODE para TODO excepto saludos muy breves
        is_greeting = use_case in ["greeting"] and len(prompt) < 50
        is_code_task = not is_greeting

        system_prompt = SYSTEM_CODE if is_code_task else SYSTEM_CHAT

        full_prompt = f"{system_prompt}\n\n{prompt}"

        # =========================
        # RETRY LOOP 🔥
        # =========================

        for attempt in range(3):

            for provider_type in providers_to_try:
                if provider_type not in self.providers:
                    continue

                provider = self.providers[provider_type]

                if not provider.is_available():
                    self._record_error(provider_type, "not_available")
                    continue

                print(f"🤖 {provider_type.value} intento {attempt+1}")

                try:
                    # Corregimos el orden de los argumentos según la firma del proveedor
                    response = provider.generate(full_prompt, temperature, max_tokens)

                    if not response or not response.text:
                        continue

                    raw = response.text.strip()

                    # LIMPIAR markdown ANTES de validar
                    cleaned = clean_llm_output(raw)

                    # =========================
                    # VALIDACIÓN SOLO PARA CÓDIGO
                    # =========================

                    if is_code_task:
                        if not is_valid_code(cleaned):
                            print("❌ Output inválido, reintentando...")

                            full_prompt = f"""
Tu respuesta anterior fue inválida.

REGLAS:
- SOLO código
- SIN markdown
- SIN explicaciones

Reintenta:

{prompt}
"""
                            continue

                        # COMENTADO - CLEANER AGRESIVO DESACTIVADO
                        # response.text = clean_code_response(cleaned)
                        # response.text = clean_code_response(response.text)
                        response.text = cleaned

                    # éxito
                    self._record_success(provider_type, response)
                    return response

                except Exception as e:
                    self._record_error(provider_type, str(e))
                    print(f"❌ Error: {e}")
                    continue

        print("💥 Todos los intentos fallaron")
        return None

    def _record_success(self, provider_type: ProviderType, response: LLMResponse):
        if provider_type not in self.stats["provider_usage"]:
            self.stats["provider_usage"][provider_type.value] = 0

        self.stats["provider_usage"][provider_type.value] += 1
        self.stats["total_cost"] += response.cost

    def _record_error(self, provider_type: ProviderType, error: str):
        key = provider_type.value
        if key not in self.stats["errors"]:
            self.stats["errors"][key] = []
        self.stats["errors"][key].append(error)

    def get_stats(self) -> Dict:
        return {
            "total_requests": self.stats["total_requests"],
            "total_cost": f"${self.stats['total_cost']:.4f}",
            "provider_usage": self.stats["provider_usage"],
            "errors": self.stats["errors"],
            "available_providers": [p.value for p in self.config.get_available_providers()],
        }

    def get_provider_status(self) -> Dict[str, bool]:
        return {
            provider_type.value: provider.is_available()
            for provider_type, provider in self.providers.items()
        }


_manager = None

def get_manager() -> LLMProviderManager:
    global _manager
    if _manager is None:
        _manager = LLMProviderManager()
    return _manager