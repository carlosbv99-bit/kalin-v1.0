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

    # Eliminar markdown
    texto = re.sub(r"```(?:python|java|javascript|cpp|c)?", "", respuesta)
    texto = texto.replace("<code>", "").replace("</code>", "").strip()
    
    # ELIMINAR texto introductorio común de LLMs
    lineas = texto.split('\n')
    lineas_limpias = []
    omitir_lineas_iniciales = True
    
    for linea in lineas:
        linea_lower = linea.lower().strip()
        
        # Si estamos en modo de omisión inicial
        if omitir_lineas_iniciales:
            # Detectar y saltar líneas introductorias
            if any(frase in linea_lower for frase in [
                'aquí está', 'aqui esta', 'here is', 'this is', 
                'este es', 'esta es', 'implementación', 'implementacion',
                'el siguiente', 'the following', 'below is',
                'te muestro', 'te presento', 'i will show',
                'claro', 'sure', 'por supuesto', 'of course'
            ]):
                continue  # Saltar esta línea
            
            # Si encontramos código real, dejar de omitir
            if any(linea.strip().startswith(kw) for kw in [
                'import ', 'from ', 'def ', 'class ', 'public ', 
                'private ', '//', '#', '/*', '@', 'package '
            ]):
                omitir_lineas_iniciales = False
                lineas_limpias.append(linea)
            else:
                continue  # Seguir omitiendo
        else:
            # Ya estamos en código, agregar todas las líneas
            lineas_limpias.append(linea)
    
    return '\n'.join(lineas_limpias).strip()


def _generar_candidato(prompt: str, max_tokens: int = 1200) -> str:
    # FORZAR uso de DeepSeek (backend) con use_case="create"
    respuesta = generate(prompt, max_tokens=max_tokens, use_case="create")
    
    print(f"🔍 DEBUG _generar_candidato - Respuesta raw: {len(respuesta) if respuesta else 0} chars")
    if respuesta:
        print(f"🔍 DEBUG - Primeros 300 chars:\n{respuesta[:300]}")
    
    if not respuesta:
        return ""

    respuesta_limpia = limpiar_respuesta(respuesta)
    print(f"🔍 DEBUG - Después de limpiar: {len(respuesta_limpia)} chars")
    
    # TEMPORAL: Desactivar filtro de chatbot para debugging
    # if es_chatbot(respuesta_limpia):
    #     print(f"❌ DEBUG - Detectado como chatbot, descartando")
    #     return ""
    
    if es_chatbot(respuesta_limpia):
        print(f"⚠️  DEBUG - Detectado como chatbot PERO CONTINUANDO (temporal)")

    codigo_extraido = extraer_codigo(respuesta_limpia)
    resultado = codigo_extraido or respuesta_limpia
    print(f"🔍 DEBUG - Código final extraído: {len(resultado)} chars")
    if resultado and len(resultado) > 50:
        print(f"🔍 DEBUG - Primeras 3 líneas del código:\n'\n'.join(resultado.split('\\n')[:3])")
    return resultado


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

    prompt = f"""ROL: GENERADOR DE CÓDIGO - MODO ESTRICTO

INSTRUCCIONES CRÍTICAS:
- Genera ÚNICAMENTE código {requerimiento.split('en ')[-1].split()[0] if 'en ' in requerimiento else 'Python'} puro
- PROHIBIDO cualquier texto explicativo antes o después del código
- PROHIBIDO comentarios introductorios como "Aquí está", "Este código", "Implementación"
- PROHIBIDO markdown (```) a menos que sea parte del código
- El código debe empezar DIRECTAMENTE con import/def/class
- Sin introducciones, sin despedidas, sin explicaciones
- Código completo, funcional y bien identado

REQUERIMIENTO:
{requerimiento}

RESPUESTA (SOLO CÓDIGO, NADA MÁS):"""

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
        prompt = f"""ROL: BACKEND - REPARADOR DE CÓDIGO FLUTTER

REGLAS ESTRICTAS:
- SOLO devuelve diff unificado válido
- CERO explicaciones
- CERO texto adicional
- CERO comentarios

FORMATO EXACTO:
--- original
+++ fixed
@@ -línea,conteo +línea,conteo @@
-línea a eliminar
+línea nueva

CÓDIGO A REPARAR:
{codigo_base}

RESPUESTA: Solo el diff. Nada más."""
    else:
        prompt = f"""ROL: BACKEND - REPARADOR DE CÓDIGO

REGLAS ESTRICTAS:
- SOLO devuelve diff unificado válido
- CERO explicaciones
- CERO texto adicional  
- CERO comentarios

FORMATO EXACTO:
--- original
+++ fixed
@@ -línea,conteo +línea,conteo @@
-línea a eliminar
+línea nueva

CÓDIGO A REPARAR:
{codigo_base}

RESPUESTA: Solo el diff. Nada más."""

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
