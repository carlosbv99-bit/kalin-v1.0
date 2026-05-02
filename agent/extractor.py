def extraer_codigo(respuesta: str) -> str:
    if not respuesta:
        return ""

    # 1. <code>
    if "<code>" in respuesta and "</code>" in respuesta:
        try:
            return respuesta.split("<code>")[1].split("</code>")[0].strip()
        except:
            pass

    # 2. ```python
    if "```" in respuesta:
        try:
            limpio = respuesta.replace("```python", "").replace("```", "")
            return limpio.strip()
        except:
            pass

    # 3. heurística
    if any(k in respuesta for k in ["def ", "class ", "import ", "from "]):
        return respuesta.strip()

    return ""