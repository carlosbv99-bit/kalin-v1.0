# agent/brain.py

from typing import Dict, Any


def normalizar(texto: str) -> str:
    return (texto or "").lower().strip()


def detectar_intencion(mensaje: str) -> str:
    """
    Detecta la intención principal del usuario.
    Escalable (puedes añadir más reglas o IA luego).
    """

    m = normalizar(mensaje)

    # 🔧 FIX
    if m.startswith("/fix") or "arregla" in m or "corrige" in m:
        return "fix"

    # 📂 SET PATH
    if m.startswith("/setpath"):
        return "setpath"

    # 📊 SCAN
    if m.startswith("/scan"):
        return "scan"

    # 💾 APPLY
    if m.startswith("/apply"):
        return "apply"

    # 🏗 CREAR
    if any(k in m for k in ["crea", "crear", "genera", "haz una app", "build"]):
        return "create"

    # ♻️ REFACTOR
    if "refactor" in m or "mejora" in m:
        return "refactor"

    # 🔍 ANALIZAR
    if "analiza" in m or "explica" in m:
        return "analyze"

    # ❓ fallback
    return "chat"


def extraer_argumentos(mensaje: str, intencion: str) -> Dict[str, Any]:
    """
    Extrae argumentos útiles según la intención
    """

    partes = mensaje.split(" ", 1)

    if intencion in ["fix", "setpath"]:
        return {
            "arg": partes[1] if len(partes) > 1 else None
        }

    return {
        "texto": mensaje
    }


def construir_contexto(mensaje: str, estado: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construye el contexto que se pasa a las tools
    """

    intencion = detectar_intencion(mensaje)
    args = extraer_argumentos(mensaje, intencion)

    contexto = {
        "mensaje": mensaje,
        "intencion": intencion,
        "args": args,
        "estado": estado
    }

    return contexto


def planificar(contexto: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fase de planificación (muy simple por ahora, pero escalable)
    """

    intencion = contexto["intencion"]

    plan = {
        "accion": intencion,
        "pasos": []
    }

    # 🔧 FIX → analizar + reparar
    if intencion == "fix":
        plan["pasos"] = ["leer_archivo", "analizar", "reparar"]

    # 🏗 CREATE → generar
    elif intencion == "create":
        plan["pasos"] = ["generar_codigo"]

    # ♻️ REFACTOR
    elif intencion == "refactor":
        plan["pasos"] = ["analizar", "refactorizar"]

    # 🔍 ANALYZE
    elif intencion == "analyze":
        plan["pasos"] = ["analizar"]

    # otros
    else:
        plan["pasos"] = ["responder"]

    contexto["plan"] = plan
    return contexto