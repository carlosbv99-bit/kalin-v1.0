# agent/core/brain.py

from typing import Dict, Any
import re


def normalizar(texto: str) -> str:
    return (texto or "").lower().strip()


def extraer_ruta_de_mensaje(mensaje: str) -> str:
    """Extrae una ruta de Windows de un mensaje en lenguaje natural"""
    m = mensaje.lower()
    
    # Patrón 1: "disco X en la carpeta Y" o "disco X carpeta Y"
    match = re.search(r'disco\s+([a-z])\s+(?:en\s+)?(?:la\s+)?carpeta\s+(\w+)', m)
    if match:
        drive = match.group(1).upper()
        folder = match.group(2)
        return f"{drive}:\\{folder}"
    
    # Patrón 2: Ruta directa tipo "E:\carpeta" o "E:/carpeta"
    match = re.search(r'([a-z]):[\\/](\S+)', m)
    if match:
        drive = match.group(1).upper()
        path = match.group(2).replace('/', '\\')
        return f"{drive}:\\{path}"
    
    # Patrón 3: Solo menciona disco sin ruta específica
    match = re.search(r'disco\s+([a-z])', m)
    if match:
        drive = match.group(1).upper()
        return f"{drive}:\\"
    
    return None


def detectar_intencion(mensaje: str) -> str:
    m = normalizar(mensaje)

    # =========================
    # DETECTOR SIMPLE DE CÓDIGO
    # =========================
    CODE_PATTERNS = [
        "void main",
        "print(",
        "{",
        "}",
        ";",
        "class ",
        "def ",
        "function ",
        "import ",
        "#include",
    ]

    def looks_like_code(text: str) -> bool:
        text = text.strip()
        matches = 0
        for pattern in CODE_PATTERNS:
            if pattern in text:
                matches += 1
        return matches >= 2

    # =========================
    # DETECTOR DE FIX REQUESTS
    # =========================
    FIX_WORDS = [
        "fix this",
        "corrige",
        "arregla",
        "repair",
        "debug",
    ]

    def is_fix_request(text: str) -> bool:
        lower = text.lower()
        return any(word in lower for word in FIX_WORDS)

    # =========================
    # ROUTER - PRIORIDAD ALTA
    # =========================
    # Si parece código o es fix request → code_fix
    if looks_like_code(mensaje):
        return "code_fix"

    if is_fix_request(mensaje):
        return "code_fix"

    # Saludos
    if any(saludo in m for saludo in [
    # Español (formal e informal)
    "hola", "buenas", "qué tal", "saludos", "buenos días", "buenas tardes", "buenas noches",
    "holi", "holita", "que onda", "que hubo", "epa", "quibo",
    
    # Inglés (formal e informal)
    "hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings",
    "howdy", "yo", "sup", "what's up", "whats up", "hey there",
    
    # Francés (formal e informal)
    "bonjour", "salut", "bonsoir", "coucou", "allô", "allo",
    "comment ça va", "ça va",
    
    # Catalán (formal e informal)
    "hola", "bon dia", "bones", "bona tarda", "bona nit",
    "ei", "com va", "què passa",
    
    # Alemán (formal e informal)
    "hallo", "guten tag", "guten morgen", "guten abend",
    "hi", "hey", "moin", "servus",
    
    # Italiano (formal e informal)
    "ciao", "buongiorno", "buonasera", "salve",
    "ehi", "come va", "bella",
    
    # Portugués (formal e informal)
    "olá", "oi", "boa tarde", "boa noite", "bom dia",
    "e aí", "beleza", "tudo bem",
    
    # Sueco (formal e informal)
    "hej", "hallå", "god morgon", "god dag", "god kväll", "god natt",
    "tjena", "tjenare", "hejsan", "läget", "hur är läget"
]):
        return "greeting"

    # Fix - corrección de errores (prioridad alta)
    if m.startswith("/fix") or any(palabra in m for palabra in [
        "arregla", "corrige", "fix", "repara", "soluciona", 
        "hay un error", "no funciona", "bug", "falla", "problema"
    ]):
        return "fix"

    # Setpath - configurar ruta
    if m.startswith("/setpath") or m.startswith("/ruta") or any(frase in m for frase in [
        "mi proyecto está en", "mi proyecto esta en", 
        "la ruta es", "configura la ruta",
        "trabaja en", "abre el proyecto", 
        "proyecto en", "está en el disco"
    ]):
        return "setpath"

    # Scan - escanear/revisar proyecto completo
    if m.startswith("/scan") or any(frase in m for frase in [
        "escanea", "scan", "revisa mi proyecto", "revisar el proyecto",
        "analiza el proyecto", "estado del proyecto",
        "cómo está el proyecto", "qué hay en el proyecto",
        "verifica el proyecto", "diagnóstico del proyecto"
    ]):
        return "scan"

    # Apply - aplicar cambios
    if m.startswith("/apply") or any(palabra in m for palabra in [
        "aplicar", "aplica", "guardar cambios", "confirmar",
        "aceptar cambios", "implementar"
    ]):
        return "apply"

    # Analyze - analizar archivos o código específico
    if m.startswith("/analyze") or any(frase in m for frase in [
        "analiza", "analizar", "explica", "describe", 
        "muéstrame", "qué hace", "cómo funciona",
        "analiza los archivos", "analiza el código",
        "explícame", "detalles", "información",
        "qué es esto", "significa", "comprender"
    ]):
        return "analyze"

    # Create - crear/generar código (detecta solicitudes implícitas)
    if m.startswith("/create") or any(frase in m for frase in [
        "crea", "crear", "genera", "generar", "haz una app",
        "build", "desarrolla", "desarrollar", "construye",
        "nuevo proyecto", "quiero hacer", "necesito crear",
        "diseña", "diseñar",
        # Solicitudes implícitas de código
        "ayúdame a", "ayudame a", "ayuda con",
        "quiero un", "necesito un", "busco un",
        "cómo hago", "como hago", "cómo crear",
        "código para", "codigo para", "programa para",
        "función para", "funcion para", "clase para",
        "app de", "aplicación de", "sistema de"
    ]):
        return "create"

    # Refactor - mejorar código
    if any(palabra in m for palabra in [
        "refactor", "mejora", "optimiza", "limpia",
        "mejorar código", "código limpio", "organiza",
        "estructura mejor", "más eficiente"
    ]):
        return "refactor"

    # Help - ayuda (solo si pregunta explícitamente por comandos/ayuda)
    if any(palabra in m for palabra in [
        "ayuda", "help", "comandos disponibles", "lista de comandos",
        "cómo se usa kalin", "instrucciones de uso"
    ]):
        return "help"

    # Experience - mostrar experiencia/aprendizaje
    if m.startswith("/experience") or any(frase in m for frase in [
        "experiencia", "aprendizaje", "memoria de aprendizaje",
        "estadísticas de uso", "qué has aprendido",
        "resumen de experiencia", "learning"
    ]):
        return "experience"

    # Learn - mostrar patrones aprendidos
    if m.startswith("/learn") or any(frase in m for frase in [
        "patrones", "qué patrones", "qué has detectado",
        "insights", "recomendaciones",
        "qué sabes de mi", "qué conoces"
    ]):
        return "learn"

    # LLM status
    if any(frase in m for frase in [
        "llm-status", "estado llm", "proveedores",
        "ollama funciona", "api disponible"
    ]):
        return "llm_status"

    # Chat conversacional (default)
    return "chat"


def extraer_argumentos(mensaje: str, intencion: str) -> Dict[str, Any]:
    partes = mensaje.split(" ", 1)

    if intencion == "setpath":
        # Intenta extraer ruta de lenguaje natural
        ruta_extraida = extraer_ruta_de_mensaje(mensaje)
        if ruta_extraida:
            return {"arg": ruta_extraida}
        # Si no, usa el argumento tradicional
        return {"arg": partes[1].strip() if len(partes) > 1 else None}

    if intencion in ["fix", "analyze", "refactor"]:
        return {"arg": partes[1].strip() if len(partes) > 1 else None}

    if intencion == "create":
        return {"texto": partes[1].strip() if len(partes) > 1 else mensaje}

    return {"texto": mensaje}


def construir_contexto(mensaje: str, estado: Dict[str, Any]) -> Dict[str, Any]:
    intencion = detectar_intencion(mensaje)
    args = extraer_argumentos(mensaje, intencion)

    return {
        "mensaje": mensaje,
        "intencion": intencion,
        "args": args,
        "estado": estado
    }


def planificar(contexto: Dict[str, Any]) -> Dict[str, Any]:
    intencion = contexto["intencion"]
    plan = {"accion": intencion, "pasos": []}

    if intencion == "fix" or intencion == "code_fix":
        plan["pasos"] = ["leer_archivo", "analizar", "reparar"]
    elif intencion == "create":
        plan["pasos"] = ["generar_codigo"]
    elif intencion == "scan":
        plan["pasos"] = ["escanear"]
    elif intencion == "apply":
        plan["pasos"] = ["aplicar"]
    elif intencion == "analyze":
        plan["pasos"] = ["analizar"]
    elif intencion == "show_code":
        plan["pasos"] = ["mostrar_codigo"]
    elif intencion == "refactor":
        plan["pasos"] = ["analizar", "refactorizar"]
    elif intencion == "help":
        plan["pasos"] = ["responder"]
    elif intencion == "greeting":
        plan["pasos"] = ["saludar"]
    elif intencion == "llm_status":
        plan["pasos"] = ["verificar_estado"]
    elif intencion == "chat":
        plan["pasos"] = ["conversar"]
    else:
        plan["pasos"] = ["responder"]

    contexto["plan"] = plan
    return contexto
