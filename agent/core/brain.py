# agent/brain.py

from typing import Dict, Any


def normalizar(texto: str) -> str:
    return (texto or "").lower().strip()


def detectar_intencion(mensaje: str) -> str:
    """
    Detecta la intención principal del usuario.
    Esta capa es ligera pero extensible para futuras reglas o IA.
    """

    m = normalizar(mensaje)

    if m.startswith("/fix") or "arregla" in m or "corrige" in m or "fix" in m:
        return "fix"

    if m.startswith("/setpath") or m.startswith("/ruta") or ("ruta" in m and "/setpath" in m):
        return "setpath"

    if m.startswith("/scan") or "escanea" in m or "scan" in m:
        return "scan"

    if m.startswith("/apply") or "aplicar" in m:
        return "apply"

    if m.startswith("/create") or any(k in m for k in ["crea", "crear", "genera", "haz una app", "build", "desarrolla"]):
        return "create"

    if "refactor" in m or "mejora" in m or "optimiza" in m:
        return "refactor"

    if "analiza" in m or "explica" in m or "describe" in m:
        return "analyze"

    if "ayuda" in m or "help" in m or m == "?":
        return "help"

    return "chat"


def extraer_argumentos(mensaje: str, intencion: str) -> Dict[str, Any]:
    """
    Extrae argumentos útiles según la intención.
    """

    partes = mensaje.split(" ", 1)

    if intencion in ["fix", "setpath", "analyze", "refactor"]:
        return {
            "arg": partes[1].strip() if len(partes) > 1 else None
        }

    if intencion == "create":
        return {
            "texto": partes[1].strip() if len(partes) > 1 else mensaje
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

    if intencion == "fix":
        plan["pasos"] = ["leer_archivo", "analizar", "reparar"]
    elif intencion == "create":
        plan["pasos"] = ["generar_codigo"]
    elif intencion == "scan":
        plan["pasos"] = ["escanear"]
    elif intencion == "apply":
        plan["pasos"] = ["aplicar"]
    elif intencion == "analyze":
        plan["pasos"] = ["analizar"]
    elif intencion == "refactor":
        plan["pasos"] = ["analizar", "refactorizar"]
    elif intencion == "help":
        plan["pasos"] = ["responder"]
    else:
        plan["pasos"] = ["responder"]

    contexto["plan"] = plan
    return contexto