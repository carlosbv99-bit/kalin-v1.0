import re
from typing import List

from agent.extractor import extraer_codigo
from agent.llm.client import generate


def es_chatbot(respuesta: str) -> bool:
    if not respuesta:
        return True

    basura = [
        "this code",
        "este código",
        "explica",
        "explanation",
        "the function",
        "this function",
        "this answer",
        "soporte",
        "lo siento",
    ]

    r = respuesta.lower()
    return any(b in r for b in basura)


def score_codigo(codigo: str) -> int:
    if not codigo:
        return 0

    score = 0
    if "def " in codigo:
        score += 2
    if "class " in codigo:
        score += 2
    if "import " in codigo:
        score += 1
    if len(codigo) > 120:
        score += 2
    if "print(" in codigo:
        score -= 1
    if "TODO" in codigo or "FIXME" in codigo:
        score -= 2

    return score


def limpiar_respuesta(respuesta: str) -> str:
    if not respuesta:
        return ""

    texto = re.sub(r"```(?:python)?", "", respuesta)
    texto = texto.replace("<code>", "").replace("</code>", "").strip()
    return texto


def _generar_candidato(prompt: str, max_tokens: int = 1200) -> str:
    respuesta = generate(prompt, max_tokens=max_tokens)
    if not respuesta:
        return ""

    respuesta_limpia = limpiar_respuesta(respuesta)
    if es_chatbot(respuesta_limpia):
        return ""

    codigo_extraido = extraer_codigo(respuesta_limpia)
    return codigo_extraido or respuesta_limpia


def _seleccionar_mejor(candidatos: List[str]) -> str:
    puntuados = []
    for candidato in candidatos:
        if not candidato:
            continue
        puntuados.append((score_codigo(candidato), candidato))

    if not puntuados:
        return ""

    puntuados.sort(reverse=True, key=lambda item: item[0])
    return puntuados[0][1]


def generar_codigo(requerimiento: str, max_intentos: int = 1) -> str:
    if not requerimiento:
        return ""

    prompt = f"""
Eres un asistente experto en desarrollo de software. Genera sólo código válido y completo sin explicaciones.

REQUERIMIENTO:
{requerimiento}

Devuelve únicamente el código resultado.
"""

    candidatos = []
    for intento in range(max_intentos):
        print(f"🧠 GENERACIÓN intento {intento + 1}")
        candidato = _generar_candidato(prompt)
        if candidato:
            candidatos.append(candidato)

    return _seleccionar_mejor(candidatos)


def reparar_codigo(codigo: str, analisis: str = "", es_flutter: bool = False, max_intentos: int = 1) -> str:
    codigo_base = codigo[:2000]
    if es_flutter:
        prompt = f"""
Eres un experto en Flutter UI/UX. Corrige este código de Flutter y devuélvelo completo, funcional y profesional.

ANÁLISIS:
{analisis}

CÓDIGO ORIGINAL:
{codigo_base}

Devuelve sólo el código corregido sin comentarios adicionales.
"""
    else:
        prompt = f"""
Eres un experto en programación. Corrige este código y devuélvelo completo y válido.

ANÁLISIS:
{analisis}

CÓDIGO ORIGINAL:
{codigo_base}

Devuelve sólo el código corregido sin explicaciones.
"""

    candidatos = []
    for intento in range(max_intentos):
        print(f"🧠 REPARACIÓN intento {intento + 1}")
        candidato = _generar_candidato(prompt)
        if candidato:
            candidatos.append(candidato)

    return _seleccionar_mejor(candidatos)
