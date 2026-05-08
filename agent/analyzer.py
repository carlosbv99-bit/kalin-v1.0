from agent.llm.client import generate
from agent.core.prompt_builder import PromptBuilder
import os

# Configuración de debug
DEBUG_MODE = False  # FORZADO A FALSE - Logs cortos

# Instancia global del constructor de prompts
prompt_builder = PromptBuilder()

def analizar_codigo(codigo, contexto=None):
    """
    Analiza código usando prompts dinámicos y contextuales
    
    Args:
        codigo: Código fuente a analizar
        contexto: Diccionario con información contextual (opcional)
    """
    codigo = codigo[:2000]  # Limitar tamaño
    
    # Construir prompt dinámico
    prompt = prompt_builder.build_prompt(
        intention="analyze",
        user_message=contexto.get("user_message", "Analiza este código") if contexto else "Analiza este código",
        context=contexto or {},
        code_content=codigo
    )

    # DEBUG: Mostrar prompt enviado
    if DEBUG_MODE:
        print("\n" + "="*80)
        print("🔍 [ANALYZER] PROMPT DINÁMICO ENVIADO AL LLM:")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")

    response = generate(prompt, max_tokens=300)  # Más tokens para análisis detallado
    
    # DEBUG: Mostrar respuesta recibida
    if DEBUG_MODE:
        print("\n" + "="*80)
        print("📥 [ANALYZER] RESPUESTA RECIBIDA DEL LLM:")
        print("="*80)
        print(response)
        print("="*80 + "\n")
    
    return response