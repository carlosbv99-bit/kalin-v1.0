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
    if len(codigo) > 100:
        score += 2
    if "print(" in codigo:
        score -= 1

    return score


def extraer_codigo(respuesta: str) -> str:
    if not respuesta:
        return ""

    if "<code>" in respuesta and "</code>" in respuesta:
        try:
            return respuesta.split("<code>")[1].split("</code>")[0].strip()
        except:
            pass

    if "```" in respuesta:
        try:
            return respuesta.split("```")[1].replace("python", "").strip()
        except:
            pass

    lineas = respuesta.splitlines()
    for i, l in enumerate(lineas):
        if any(k in l for k in ["import ", "from ", "def ", "class ", "@"]):
            return "\n".join(lineas[i:]).strip()

    return ""


def reparar_codigo(codigo, analisis, es_flutter=False):
    codigo = codigo[:2000]
    candidatos = []

    for intento in range(5):
        prompt = f"""
        ```

        # código completo

        ```

        PROHIBIDO:

        * explicaciones
        * texto

        CODIGO:
        {codigo}
        """

        respuesta = generate(prompt, max_tokens=1200)
        print("\n🧠 RAW LLM:")
        print(respuesta)
        print("=" * 50)

        if not respuesta:
            continue

        if es_chatbot(respuesta):
            continue

        codigo_extraido = extraer_codigo(respuesta)

        if not codigo_extraido:
            continue

        score = score_codigo(codigo_extraido)

        candidatos.append((score, codigo_extraido))

    if not candidatos:
        return ""

    candidatos.sort(reverse=True)

    return candidatos[0][1]