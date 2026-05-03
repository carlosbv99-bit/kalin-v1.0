from agent.llm.client import generate

def analizar_codigo(codigo):
    codigo = codigo[:2000]

    prompt = f"""
Eres un experto en programación.

Analiza este código y detecta errores:

{codigo}

Responde claro.
"""

    return generate(prompt, max_tokens=200)  # Increased from 60 to 200 for better analysis