import re

def extraer_codigo(respuesta: str) -> str:
    if not respuesta:
        return ""

    # 1. Extraer de tags <code>
    if "<code>" in respuesta and "</code>" in respuesta:
        try:
            return respuesta.split("<code>")[1].split("</code>")[0].strip()
        except:
            pass

    # 2. Extraer de bloques markdown ```
    if "```" in respuesta:
        try:
            limpio = respuesta.replace("```python", "").replace("```", "")
            return limpio.strip()
        except:
            pass

    # 3. MEJORADO: Extraer solo líneas que parecen código
    lineas = respuesta.split('\n')
    lineas_codigo = []
    
    # Detectar si es HTML completo
    es_html_completo = '<!doctype' in respuesta.lower() or '<html' in respuesta.lower()
    
    for linea in lineas:
        linea_stripped = linea.strip()
        
        # Ignorar líneas vacías al inicio/final
        if not linea_stripped:
            if lineas_codigo:  # Permitir líneas vacías en medio del código
                lineas_codigo.append(linea)
            continue
        
        # Si es HTML completo, preservar TODO (incluyendo CSS)
        if es_html_completo:
            lineas_codigo.append(linea)
            continue
        
        # Detectar si es línea de código válida
        es_codigo = False
        
        # Patrones de código Python/Java/etc
        if any(linea_stripped.startswith(kw) for kw in [
            'def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ',
            'return ', 'print(', 'try:', 'except', 'else:', 'elif ',
            'public ', 'private ', 'protected ', 'static ', 'void ',
            'int ', 'float ', 'string ', 'var ', 'const ', 'let ',
            '#', '//', '/*', '*/', '@', 'package ', 'namespace '
        ]):
            es_codigo = True
        
        # Líneas con operadores típicos de código
        elif any(op in linea_stripped for op in ['=', '+=', '-=', '*=', '/=', '==', '!=', '<', '>', '->']):
            if not linea_stripped.startswith(('¡', '¿', 'Hola', 'Claro', 'Aquí', 'Este')):
                es_codigo = True
        
        # Líneas con paréntesis/llaves/corchetes (código)
        elif any(c in linea_stripped for c in ['()', '{}', '[]', '()', '=>']):
            es_codigo = True
        
        # Si parece código, agregarla
        if es_codigo:
            lineas_codigo.append(linea)
    
    # Si encontramos líneas de código, unirlas
    if lineas_codigo:
        resultado = '\n'.join(lineas_codigo).strip()
        # Solo retornar si hay suficiente contenido de código
        if len(resultado) > 30:
            return resultado

    # 4. Fallback: si hay keywords de código, retornar todo
    if any(k in respuesta for k in ["def ", "class ", "import ", "from "]):
        return respuesta.strip()

    return ""