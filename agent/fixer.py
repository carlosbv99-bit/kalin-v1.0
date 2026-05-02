from agent.llm_client import generar_respuesta


def extraer_codigo(respuesta: str) -> str:
    """Extrae código de múltiples formatos posibles"""
    if not respuesta:
        return ""

    # 1. <code>
    if "<code>" in respuesta and "</code>" in respuesta:
        try:
            return respuesta.split("<code>")[1].split("</code>")[0].strip()
        except:
            pass

    # 2. markdown ```
    if "```" in respuesta:
        try:
            return respuesta.split("```")[1].replace("python", "").strip()
        except:
            pass

    # 3. heurística básica (buscar inicio de código real)
    lineas = respuesta.splitlines()

    for i, l in enumerate(lineas):
        if any(k in l for k in ["import ", "from ", "def ", "class ", "@"]):
            return "\n".join(lineas[i:]).strip()

    return ""


def reparar_codigo(codigo, analisis, es_flutter=False):
    codigo = codigo[:2000]

    respuesta = ""

    for intento in range(3):

        # ==========================
        # 🧠 PROMPTS ESCALONADOS
        # ==========================
        if intento == 0:
            prompt = f"""
Eres un agente que repara código automáticamente.

RESPONDE SOLO CÓDIGO.

FORMATO:
<code>
# código completo
</code>

REGLAS:
- Sin explicaciones
- Archivo completo
- Mantener estructura
- No agregar dependencias nuevas

CODIGO:
{codigo}
"""

        elif intento == 1:
            prompt = f"""
SOLO CÓDIGO.

USA:
<code>
# código
</code>

PROHIBIDO TEXTO.

CODIGO:
{codigo}
"""

        else:
            prompt = f"""
DEVUELVE SOLO CÓDIGO AUNQUE SEA IGUAL.

FORMATO:
<code>
# código
</code>

SIN TEXTO.

CODIGO:
{codigo}
"""

        # ==========================
        # 🤖 LLAMADA
        # ==========================
        respuesta = generar_respuesta(prompt, max_tokens=1200)

        print(f"🧠 INTENTO {intento+1} RAW:")
        print(repr(respuesta))

        if not respuesta:
            continue

        # ==========================
        # 🔍 EXTRACCIÓN FUERTE
        # ==========================
        codigo_extraido = extraer_codigo(respuesta)

        if codigo_extraido:
            print("✅ código extraído correctamente")
            return codigo_extraido

        # ==========================
        # 🔁 FALLBACK HEURÍSTICO
        # ==========================
        limpio = respuesta.replace("```python", "").replace("```", "").strip()

        # 🔥 recorte inteligente (clave)
        lineas = limpio.splitlines()
        for i, l in enumerate(lineas):
            if any(k in l for k in ["import ", "from ", "def ", "class ", "@"]):
                candidato = "\n".join(lineas[i:]).strip()

                if candidato:
                    print("✅ código detectado por heurística")
                    return candidato

        print("⚠️ no se pudo extraer código, reintentando...")

    # ==========================
    # 🚨 FALLBACK FINAL (IMPORTANTE)
    # ==========================
    print("🚨 fallback final")

    if respuesta:
        # 🔥 último intento de limpieza
        limpio = extraer_codigo(respuesta)

        if limpio:
            return limpio

        # 🔥 devolver SOLO parte útil
        lineas = respuesta.splitlines()
        for i, l in enumerate(lineas):
            if any(k in l for k in ["import ", "from ", "def ", "class "]):
                return "\n".join(lineas[i:]).strip()

        # ⚠️ si TODO falla → devolver vacío (mejor que romper)
        return ""

    return ""