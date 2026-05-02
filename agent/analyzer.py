from agent.llm_client import generar_respuesta

def analizar_codigo(codigo):
    codigo = codigo[:2000]

    prompt = f"""
Eres un experto en programación.

Analiza este código y detecta errores:

{codigo}

Responde claro.
"""

    return generar_respuesta(prompt, max_tokens=60)