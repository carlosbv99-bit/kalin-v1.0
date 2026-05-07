from agent.llm.client import generate
import os

# Configuración de debug
DEBUG_MODE = os.getenv("KALIN_DEBUG", "0").lower() in ["1", "true", "yes"]

def analizar_codigo(codigo):
    codigo = codigo[:2000]

    prompt = f"""
Eres un experto en programación.

Analiza este código y detecta errores:

{codigo}

Responde claro.
"""

    # DEBUG: Mostrar prompt enviado
    if DEBUG_MODE:
        print("\n" + "="*80)
        print("🔍 [ANALYZER] PROMPT ENVIADO AL LLM:")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")

    response = generate(prompt, max_tokens=200)  # Increased from 60 to 200 for better analysis
    
    # DEBUG: Mostrar respuesta recibida
    if DEBUG_MODE:
        print("\n" + "="*80)
        print("📥 [ANALYZER] RESPUESTA RECIBIDA DEL LLM:")
        print("="*80)
        print(response)
        print("="*80 + "\n")
    
    return response