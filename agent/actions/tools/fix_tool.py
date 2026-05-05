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


def _es_diff_valido(texto: str) -> bool:
    """Valida que el texto sea un diff unificado válido"""
    if not texto:
        return False
    
    lineas = texto.strip().split("\n")
    tiene_header = any(l.startswith("---") or l.startswith("+++") for l in lineas)
    tiene_hunk = any(l.startswith("@@") for l in lineas)
    tiene_cambios = any(l.startswith("+") or l.startswith("-") for l in lineas)
    
    return tiene_header and (tiene_hunk or tiene_cambios)


def reparar_codigo(codigo: str, analisis: str = "", es_flutter: bool = False, max_intentos: int = 1) -> str:
    codigo_base = codigo[:2000]
    
    if es_flutter:
        prompt = f"""Eres un experto en Flutter UI/UX. Devuelve SOLO un diff unificado para reparar este código.

FORMATO REQUERIDO (diff unificado):
--- original
+++ fixed
@@ -línea,conteo +línea,conteo @@
-línea a eliminar
+línea nueva

ANÁLISIS:
{analisis}

CÓDIGO ORIGINAL:
{codigo_base}

RESPUESTA: Solo el diff unificado. Nada más."""
    else:
        prompt = f"""Eres un experto en programación. Tu tarea es devolver SOLO un diff unificado para reparar este código.

FORMATO REQUERIDO (diff unificado):
--- original
+++ fixed
@@ -línea,conteo +línea,conteo @@
-línea a eliminar
+línea nueva

ANÁLISIS:
{analisis}

CÓDIGO ORIGINAL:
{codigo_base}

RESPUESTA: Solo el diff unificado. Nada más."""

    candidatos = []
    for intento in range(max_intentos):
        print(f"🧠 REPARACIÓN intento {intento + 1}")
        resp = generate(prompt, max_tokens=1500)
        if resp and _es_diff_valido(resp):
            candidatos.append(resp)
            print(f"✅ Diff válido generado")

    if not candidatos:
        print(f"❌ No se generó diff válido en {max_intentos} intentos")
        return ""
    
    return candidatos[0]
