from langgraph.graph import StateGraph
import requests

# 🔍 AGENTE 1 — ANALIZADOR
def analizar_codigo(state):
    codigo = state["input"]

    prompt = f"""
Eres un experto en programación MUY ESTRICTO.

Analiza el código y SIEMPRE encuentra problemas, aunque sean pequeños.

Busca:
- errores
- malas prácticas
- código incompleto
- funciones vacías
- posibles fallos

Responde SOLO así:

--- ANALISIS ---
(lista clara de problemas)

CODIGO:
{codigo}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-coder",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 150,
                "temperature": 0.2
            }
        }
    )

    data = response.json()
    texto = data.get("response")

    if not texto:
        texto = "Error: sin respuesta del modelo"

    return {
        "input": codigo,
        "analisis": texto
    }


# 🛠 AGENTE 2 — REPARADOR
def reparar_codigo(state):
    codigo = state["input"]
    analisis = state["analisis"]

    prompt = f"""
Eres un experto programador.
Corrige el código COMPLETAMENTE y hazlo funcional.
No dejes código vacío.

Corrige el código basándote en este análisis:

{analisis}

Devuelve SOLO:

--- CODIGO CORREGIDO ---
(código completo corregido)

CODIGO ORIGINAL:
{codigo}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-coder",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 300,
                "temperature": 0.2
            }
        }
    )

    data = response.json()
    texto = data.get("response")

    if not texto:
        texto = "Error: sin respuesta del modelo"

    return {
        "output": texto
    }


# 🧠 GRAFO MULTI-AGENTE
graph = StateGraph(dict)

graph.add_node("analizar", analizar_codigo)
graph.add_node("reparar", reparar_codigo)

graph.set_entry_point("analizar")

# Flujo: analizar → reparar
graph.add_edge("analizar", "reparar")

app = graph.compile()


# 🖥️ MODO CONSOLA
if __name__ == "__main__":
    print("🤖 Agente IA listo (escribe 'salir' para terminar)\n")

    while True:
        pregunta = input(">> ")

        if pregunta.lower() in ["exit", "salir"]:
            print("👋 Cerrando agente...")
            break

        result = app.invoke({"input": pregunta})
        print("\n" + result["output"] + "\n")