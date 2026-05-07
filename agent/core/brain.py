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

    # =========================
    # DETECTOR INTELIGENTE DE CONTEXTO
    # =========================
    
    # Fix - corrección de errores (prioridad ALTA)
    if m.startswith("/fix") or any(palabra in m for palabra in [
        "arregla", "corrige", "fix", "repara", "soluciona", 
        "hay un error", "no funciona", "bug", "falla", "problema",
        "encuentras errores", "hay errores", "errores en", "tiene errores",
        "qué errores", "que errores", "detecta errores", "busca errores",
        "está mal", "algo mal", "incorrecto", "no está bien",
        "funciona correctamente", "está bien el código",
        "revisa si hay", "verifica si hay", "chequea si hay",
        # Acciones de corrección/eliminación
        "elimina", "eliminar", "quita", "quitar", "borra", "borrar",
        "remueve", "remover", "saca", "sacar",
        "optimiza", "optimizar", "limpia", "limpiar",
        "actualiza", "actualizar", "mejora", "mejorar"
    ]):
        return "fix"

    # Setpath - configurar ruta
    if m.startswith("/setpath") or m.startswith("/ruta") or any(frase in m for frase in [
        "mi proyecto está en", "mi proyecto esta en", 
        "la ruta es", "configura la ruta",
        "trabaja en", "abre el proyecto", 
        "proyecto en", "está en el disco",
        "carpeta del proyecto", "directorio del proyecto"
    ]):
        return "setpath"

    # Scan - escanear/revisar proyecto completo (detecta cuando habla del PROYECTO)
    if m.startswith("/scan") or any(frase in m for frase in [
        "escanea", "scan", "revisa mi proyecto", "revisar el proyecto",
        "analiza el proyecto", "estado del proyecto",
        "cómo está el proyecto", "qué hay en el proyecto",
        "verifica el proyecto", "diagnóstico del proyecto",
        "proyecto completo", "todo el proyecto", "el proyecto entero"
    ]):
        return "scan"

    # Apply - aplicar cambios
    if m.startswith("/apply") or any(palabra in m for palabra in [
        "aplicar", "aplica", "guardar cambios", "confirmar",
        "aceptar cambios", "implementar"
    ]):
        return "apply"

    # Analyze - analizar archivos o código específico (muy flexible)
    if m.startswith("/analyze") or any(frase in m for frase in [
        "analiza", "analizar", "explica", "describe", 
        "muéstrame", "qué hace", "cómo funciona",
        "analiza los archivos", "analiza el código",
        "explícame", "detalles", "información",
        "qué es esto", "significa", "comprender",
        "revisa el código", "verifica el código", "chequea",
        "analiza y encuentra", "encuentra y analiza",
        "dime sobre", "cuéntame sobre", "hablame de",
        "quiero ver", "mostrar", "ver el",
        "puedes analizar", "me explicas", "necesito analizar",
        # Cuando menciona tipos de proyecto
        "proyecto android", "app android", "aplicación android",
        "proyecto flutter", "app flutter", "aplicación flutter",
        "proyecto python", "script python",
        "proyecto java", "código java"
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

    # Show code - mostrar código generado o contenido de archivo
    if any(frase in m for frase in [
        "muestrame el codigo", "muéstrame el código",
        "muestra el codigo", "muestra el código",
        "ver el codigo", "ver el código",
        "mostrar codigo", "mostrar código",
        "dame el codigo", "dame el código",
        "codigo completo", "código completo",
        "todo el codigo", "todo el código"
    ]):
        return "show_code"

    # Chat conversacional (default)
    return "chat"


def extraer_argumentos(mensaje: str, intencion: str) -> Dict[str, Any]:
    """
    Extrae argumentos inteligentes del mensaje usando patrones avanzados.
    
    Soporta:
    - Nombres de archivo con extensión (main.py, pubspec.yaml, etc.)
    - Rutas de Windows (E:\carpeta, C:\proyecto\app)
    - Referencias naturales ("mi archivo X", "el archivo Y")
    """
    import re
    
    if intencion == "setpath":
        # Intenta extraer ruta de lenguaje natural
        ruta_extraida = extraer_ruta_de_mensaje(mensaje)
        if ruta_extraida:
            return {"arg": ruta_extraida}
        # Si no, usa el argumento tradicional
        partes = mensaje.split(" ", 1)
        return {"arg": partes[1].strip() if len(partes) > 1 else None}

    if intencion in ["fix", "analyze", "refactor"]:
        # PATRÓN 1: Buscar nombre de archivo con extensión (soporta . y , como separador)
        file_pattern = r'([\w-]+[.,](?:py|java|dart|js|ts|html|css|json|yaml|yml|xml|txt|gradle|md))'
        match = re.search(file_pattern, mensaje, re.IGNORECASE)
        
        if match:
            filename = match.group(1).replace(',', '.')  # Normalizar coma a punto
            
            # PATRÓN 1.5: Buscar ruta mencionada en el mensaje (incluso si no está al final)
            path_pattern = r'([A-Z]:\\[\w\\ ]+)'
            path_match = re.search(path_pattern, mensaje, re.IGNORECASE)
            
            if path_match:
                project_path = path_match.group(1).strip()
                return {
                    "arg": filename,
                    "project_path": project_path,
                    "has_location": True
                }
            
            return {"arg": filename}
        
        # PATRÓN 2: Buscar ruta completa de Windows (sin nombre de archivo)
        path_pattern = r'([A-Z]:\\[^\s"]+)'
        match = re.search(path_pattern, mensaje, re.IGNORECASE)
        
        if match:
            full_path = match.group(1)
            return {"arg": full_path, "full_path": True}
        
        # PATRÓN 3: Extraer todo después del comando (fallback)
        partes = mensaje.split(" ", 1)
        arg_text = partes[1].strip() if len(partes) > 1 else None
        
        # Si hay una ruta mencionada al final, extraerla
        if arg_text:
            # Buscar patrón "ubicado en/an X" o "en X"
            location_pattern = r'(?:ubicado\s+(?:en|an)|en)\s+([A-Z]:\\[^\s"]+)'
            match = re.search(location_pattern, arg_text, re.IGNORECASE)
            if match:
                return {
                    "arg": arg_text,  # Texto completo para contexto
                    "project_path": match.group(1),  # Ruta extraída
                    "has_location": True
                }
        
        return {"arg": arg_text}

    if intencion == "create":
        partes = mensaje.split(" ", 1)
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
