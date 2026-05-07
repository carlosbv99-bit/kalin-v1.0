import re
import os
import json
from typing import List

from agent.extractor import extraer_codigo
from agent.llm.client import generate

# Configuración de debug
DEBUG_MODE = os.getenv("KALIN_DEBUG", "0").lower() in ["1", "true", "yes"]


def extract_code(input_data):
    try:
        data = json.loads(input_data)

        if "documentChunks" in data:
            code = ""
            for chunk in data["documentChunks"]:
                code += chunk.get("chunk", "") + "\n"
            return code.strip()

    except Exception:
        pass

    # Si no es JSON, devolver tal cual
    return input_data


def es_chatbot(respuesta: str) -> bool:
    """Detecta si la respuesta es tipo chatbot en lugar de código"""
    if not respuesta:
        return True

    # FRASES CONVERSACIONALES QUE INDICAN CHATBOT
    frases_chatbot = [
        # Saludos y exclamaciones
        "excelente", "genial", "perfecto", "fantástico", "estupendo",
        "¡excelente", "¡genial", "¡perfecto", "¡fantástico",
        # Preguntas al usuario
        "¿podrías", "¿te gustaría", "¿qué opinas", "¿prefieres",
        "¿tienes alguna", "¿cuál es", "¿podríamos",
        # Frases de inicio conversacional
        "empecemos", "vamos a", "comencemos", "para empezar",
        "antes de", "para continuar", "para mejorar",
        # Frases de oferta de ayuda
        "puedo ayudarte", "puedo crear", "puedo hacer",
        "estoy listo", "estoy aquí", "dime",
        # Texto que NO es código
        "este código", "this code", "el siguiente código",
        "aquí tienes", "here is", "this is the",
        # Disculpas y negativas
        "lo siento", "i'm sorry", "no puedo",
        "no estoy seguro", "no sé",
        # Explicaciones
        "explicación", "explanation", "the function",
        "this function", "esta función",
    ]

    r = respuesta.lower()
    
    # Contar cuántas frases chatbot aparecen
    coincidencias = sum(1 for frase in frases_chatbot if frase in r)
    
    # Si hay 2 o más frases chatbot, ES CHATBOT
    if coincidencias >= 2:
        return True
    
    # Si la respuesta NO tiene estructura de código, ES CHATBOT
    tiene_codigo = any(patron in r for patron in [
        'def ', 'class ', 'import ', 'function', 'public ',
        'private ', 'package ', '<!doctype', '<html', '<script',
        'console.log', 'print(', 'system.out'
    ])
    
    if not tiene_codigo and len(respuesta) > 50:
        return True
    
    return False


def score_codigo(codigo: str) -> int:
    if not codigo:
        return 0

    score = 0
    
    # Python/Java/C++ patterns
    if "def " in codigo:
        score += 2
    if "class " in codigo:
        score += 2
    if "import " in codigo:
        score += 1
    
    # HTML patterns (añadido)
    if "<!DOCTYPE" in codigo or "<html" in codigo.lower():
        score += 3
    if "<body" in codigo.lower() or "<head" in codigo.lower():
        score += 2
    if "</html>" in codigo.lower():
        score += 2
    
    # General code quality
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
            # AÑADIDO: Soporte para HTML
            if any(linea.strip().startswith(kw) for kw in [
                'import ', 'from ', 'def ', 'class ', 'public ', 
                'private ', '//', '#', '/*', '@', 'package '
            ]) or any(html_tag in linea_lower for html_tag in [
                '<!doctype', '<html', '<head', '<body', '<div', '<script', '<style'
            ]):
                omitir_lineas_iniciales = False
                lineas_limpias.append(linea)
            else:
                continue  # Seguir omitiendo
        else:
            # Ya estamos en código, agregar todas las líneas
            lineas_limpias.append(linea)
    
    resultado = '\n'.join(lineas_limpias).strip()
    
    # LIMPIAR COMENTARIOS del código (capa de seguridad adicional)
    resultado = eliminar_comentarios(resultado)
    
    return resultado


def eliminar_comentarios(codigo: str) -> str:
    """Elimina todos los comentarios del código (Python, Java, JS, HTML, etc.)"""
    if not codigo:
        return ""
    
    # Detectar si es HTML puro
    es_html = '<!doctype' in codigo.lower() or '<html' in codigo.lower()
    
    # PRIMERO: Eliminar comentarios HTML <!-- ... -->
    codigo = re.sub(r'<!--.*?-->', '', codigo, flags=re.DOTALL)
    
    # Si es HTML, NO eliminar más nada (preservar etiquetas)
    if es_html:
        # Solo limpiar espacios en blanco múltiples
        lineas = [linea.rstrip() for linea in codigo.split('\n') if linea.strip()]
        return '\n'.join(lineas).strip()
    
    # Para otros lenguajes, eliminar comentarios de línea
    lineas = codigo.split('\n')
    lineas_limpias = []
    
    for linea in lineas:
        # Eliminar comentarios de línea (# para Python, // para Java/JS/C++)
        # Pero preservar strings que contengan # o //
        if '#' in linea or '//' in linea:
            # Simple approach: eliminar desde el primer # o // que no esté en string
            linea_limpia = re.sub(r'\s*#.*$', '', linea)  # Python comments
            linea_limpia = re.sub(r'\s*//.*$', '', linea_limpia)  # Java/JS comments
            if linea_limpia.strip():  # Solo agregar si queda algo
                lineas_limpias.append(linea_limpia.rstrip())
        else:
            lineas_limpias.append(linea)
    
    resultado = '\n'.join(lineas_limpias)
    
    # LIMPIAR líneas vacías múltiples (máximo 2 consecutivas)
    lineas_finales = resultado.split('\n')
    lineas_filtradas = []
    vacias_consecutivas = 0
    
    for linea in lineas_finales:
        if not linea.strip():
            vacias_consecutivas += 1
            if vacias_consecutivas <= 2:
                lineas_filtradas.append(linea)
        else:
            vacias_consecutivas = 0
            lineas_filtradas.append(linea)
    
    return '\n'.join(lineas_filtradas).strip()


def limpiar_texto_basura(codigo: str) -> str:
    """
    Elimina texto basura que aparece después del código real.
    Detecta patrones como:
    - 'END OF CODE'
    - Texto explicativo largo después del código
    - Frases sin sentido técnico
    """
    if not codigo:
        return ""
    
    # Patrones que indican fin del código útil
    patrones_fin = [
        r'END OF CODE.*',
        r'```\s*$',  # Markdown closing
        r'#.*END.*',
        r'SIGNO DE COMPLEJIDAD.*',
        r'NO HAY PUNTO.*',
    ]
    
    lineas = codigo.split('\n')
    lineas_limpias = []
    
    for linea in lineas:
        # Verificar si esta línea o las siguientes son texto basura
        es_basura = False
        for patron in patrones_fin:
            if re.search(patron, linea, re.IGNORECASE):
                es_basura = True
                break
        
        if es_basura:
            break  # Detener procesamiento aquí
        
        lineas_limpias.append(linea)
    
    return '\n'.join(lineas_limpias).strip()


def clean_llm_output(text: str) -> str:
    """
    Limpia la salida del LLM eliminando markdown y formato innecesario.
    OBLIGATORIO para todas las respuestas de código.
    """
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        # quitar primera línea ```dart
        lines = lines[1:]

        # quitar última ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines)

    cleaned = text.strip()

    # VALIDACIÓN OBLIGATORIA: Código muy corto
    if len(cleaned) < 5:
        return ""

    # VALIDACIÓN OBLIGATORIA: Detectar respuesta de chatbot
    if "Lo siento" in cleaned or "lo siento" in cleaned:
        return ""

    return cleaned


def _generar_candidato(prompt: str, max_tokens: int = 1200) -> str:
    # LOG DEL PROMPT REAL QUE VA AL LLM
    print("\n" + "="*80)
    print("=== PROMPT START ===")
    print(prompt)
    print("=== PROMPT END ===")
    print(f"Longitud del prompt: {len(prompt)} chars")
    print("="*80 + "\n")
    
    # Detectar si es HTML para usar configuración optimizada
    es_html = '<!DOCTYPE' in prompt or 'HTML' in prompt.upper()
    if es_html and max_tokens > 1200:
        max_tokens = 1200  # Aumentado de 800 a 1200 para HTML más complejo
    
    # FORZAR uso de DeepSeek (backend) con use_case="create"
    respuesta = generate(prompt, max_tokens=max_tokens, use_case="create")
    
    # LOG DE LA RESPUESTA RAW DEL LLM
    print("\n" + "="*80)
    print("=== RAW LLM RESPONSE START ===")
    print(f"Longitud: {len(respuesta) if respuesta else 0} chars")
    if respuesta:
        print(respuesta[:1000])
        if len(respuesta) > 1000:
            print(f"... ({len(respuesta) - 1000} chars más)")
    print("=== RAW LLM RESPONSE END ===")
    print("="*80 + "\n")
    
    if not respuesta:
        return ""

    # LIMPIEZA OBLIGATORIA: Eliminar markdown y formato LLM
    respuesta = clean_llm_output(respuesta)

    respuesta_limpia = limpiar_respuesta(respuesta)
    
    # DEBUG: Mostrar código después de limpieza
    if DEBUG_MODE:
        print("\n" + "="*80)
        print("🧹 [FIX_TOOL] CÓDIGO DESPUÉS DE LIMPIEZA:")
        print("="*80)
        print(f"Longitud: {len(respuesta_limpia)} chars")
        if respuesta_limpia:
            print(respuesta_limpia[:1000])
        print("="*80 + "\n")
    
    # TEMPORAL: Desactivar filtro de chatbot para debugging
    # if es_chatbot(respuesta_limpia):
    #     return ""
    
    if es_chatbot(respuesta_limpia):
        if DEBUG_MODE:
            print(f"⚠️  Detectado como chatbot pero continuando")

    codigo_extraido = extraer_codigo(respuesta_limpia)
    resultado = codigo_extraido or respuesta_limpia
    
    # DEBUG: Mostrar código final parseado
    if DEBUG_MODE:
        print("\n" + "="*80)
        print("✅ [FIX_TOOL] CÓDIGO FINAL PARSEADO:")
        print("="*80)
        print(f"Longitud: {len(resultado)} chars")
        if resultado:
            lineas = resultado.split('\n')[:20]
            print('\n'.join(lineas))
            total_lineas = len(resultado.split('\n'))
            if total_lineas > 20:
                print(f"... ({total_lineas - 20} líneas más)")
        print("="*80 + "\n")
    
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


def generar_codigo(requerimiento: str, max_intentos: int = 3) -> str:
    """
    Genera código con validación y reintentos automáticos.
    
    Args:
        requerimiento: Descripción del código a generar
        max_intentos: Número máximo de intentos (default 3)
    
    Returns:
        Código generado y validado, o cadena vacía si falla
    """
    if not requerimiento:
        return ""

    # Detectar lenguaje de programación solicitado
    lenguajes_posibles = {
        'python': 'Python',
        'py': 'Python',
        'javascript': 'JavaScript',
        'js': 'JavaScript',
        'typescript': 'TypeScript',
        'ts': 'TypeScript',
        'html': 'HTML',
        'css': 'CSS',
        'java': 'Java',
        'c++': 'C++',
        'cpp': 'C++',
        'c#': 'C#',
        'csharp': 'C#',
        'ruby': 'Ruby',
        'go': 'Go',
        'rust': 'Rust',
    }
    
    lenguaje = 'Python'  # default
    requerimiento_lower = requerimiento.lower()
    for key, value in lenguajes_posibles.items():
        if key in requerimiento_lower:
            lenguaje = value
            break

    # Construir ejemplos según el lenguaje
    instrucciones_extra = ""  # Default vacío
    
    if lenguaje == 'HTML':
        ejemplo_bueno = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Calendario</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: center; }
        th { background: #f0f0f0; }
    </style>
</head>
<body>
    <h1>Mayo 2026</h1>
    <table>
        <tr><th>Lun</th><th>Mar</th><th>Mié</th><th>Jue</th><th>Vie</th><th>Sáb</th><th>Dom</th></tr>
        <tr><td></td><td></td><td></td><td></td><td>1</td><td>2</td><td>3</td></tr>
        <tr><td>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td><td>10</td></tr>
        <tr><td>11</td><td>12</td><td>13</td><td>14</td><td>15</td><td>16</td><td>17</td></tr>
        <tr><td>18</td><td>19</td><td>20</td><td>21</td><td>22</td><td>23</td><td>24</td></tr>
        <tr><td>25</td><td>26</td><td>27</td><td>28</td><td>29</td><td>30</td><td>31</td></tr>
    </table>
</body>
</html>"""
        ejemplo_malo = """<!-- Calendario -->
<html>
<!-- Esto es un comentario -->
<body>
<h1>Calendario</h1> <!-- Comentario inline -->
<table border="1">
<tr><td>1</td></tr>
</table>
</body>
</html>"""
        
        # INSTRUCCIONES ESPECÍFICAS PARA HTML
        instrucciones_extra = """
IMPORTANTE PARA HTML:
- NO uses comentarios HTML (<!-- -->)
- INCLUYE CSS COMPLETO y PROFESIONAL en <style> con:
  * Colores atractivos y modernos
  * Bordes redondeados (border-radius)
  * Sombras suaves (box-shadow)
  * Espaciado adecuado (padding/margin)
  * Centrado de contenido
  * Tipografía legible
- Genera un calendario COMPLETO con todos los días del mes actual
- Usa estructura semántica correcta
- El calendario debe verse PROFESIONAL y bien diseñado
- Puedes usar flexbox o grid para layout"""
    elif lenguaje == 'JavaScript':
        ejemplo_bueno = """function generarCalendario(anio, mes) {
    const fecha = new Date(anio, mes - 1, 1);
    return fecha;
}

console.log(generarCalendario(2024, 5));"""
        ejemplo_malo = """// Calendario simple
function gen_cal(a, m) { // Nombres malos
    /* Comentario */
    return a + m; // Comentario inline
}"""
    elif lenguaje == 'Python':
        ejemplo_bueno = """import calendar
from datetime import date

def generar_calendario(anio=None, mes=None):
    if anio is None:
        anio = date.today().year
    if mes is None:
        mes = date.today().month
    cal = calendar.TextCalendar(firstweekday=6)
    return cal.formatmonth(anio, mes)

if __name__ == "__main__":
    print(generar_calendario())"""
        ejemplo_malo = """# Calendario simple
import calendar  # NO COMENTARIOS

def gen_cal(a, m):  # NOMBRES MALOS
    '''Funcion calendario'''  # NO DOCSTRINGS
    c = calendar.TextCalendar()  # VARIABLES CORTAS
    return c.formatmonth(a, m).replace('\\n', '')  # CODIGO INNATURAL"""
    else:
        # Default para otros lenguajes
        ejemplo_bueno = f"""// Código {lenguaje} limpio
function main() {{
    console.log("Hello World");
}}

main();"""
        ejemplo_malo = f"""// {lenguaje} con comentarios
// Esto es un comentario
function main() {{ // Comentario inline
    /* Otro comentario */
    console.log("test");
}}"""

    prompt = f"""ERES UN GENERADOR DE CÓDIGO, NO UN ASISTENTE CONVERSACIONAL.

REGLAS ABSOLUTAS (VIOLAR CUALQUIERA = FRACASO):
1. GENERA DIRECTAMENTE código {lenguaje} funcional y completo
2. NUNCA hagas preguntas al usuario
3. NUNCA expliques qué vas a hacer
4. NUNCA pidas información adicional
5. NUNCA uses frases como "Excelente elección", "Empecemos", "¿Podrías decirme?"
6. NUNCA incluyas comentarios de ningún tipo
7. NUNCA uses markdown (```) o formato especial
8. El código DEBE empezar en la PRIMERA línea con estructura de {lenguaje}
9. NUNCA agregues texto antes o después del código
10. Si no puedes cumplir estas reglas, devuelve cadena vacía

FORMATO CORRECTO:
import calendar

def generar_calendario():
    pass

FORMATO INCORRECTO:
¡Excelente! Aquí tienes el código...
```python
import calendar
```

REQUERIMIENTO:
{requerimiento}

GENERA AHORA SOLO EL CÓDIGO {lenguaje.upper()}:"""

    candidatos = []
    for intento in range(max_intentos):
        print(f"🧠 GENERACIÓN intento {intento + 1}/{max_intentos}")
        candidato = _generar_candidato(prompt)
        
        # VALIDAR calidad del código
        if candidato and _es_codigo_de_calidad(candidato, lenguaje):
            score = calcular_score_calidad(candidato)
            print(f"✅ Código de calidad aceptable en intento {intento + 1} (score: {score:.2f})")
            candidatos.append((score, candidato))
            
            # OPTIMIZACIÓN: Si es el primer intento y tiene alta calidad (>0.7), detenerse
            if intento == 0 and score > 0.7:
                print(f"⚡ Código de ALTA calidad detectado. Omitiendo reintentos para mayor velocidad.")
                return candidato
        else:
            print(f"⚠️  Código de baja calidad, reintentando...")
            # Para HTML, mostrar por qué falló (debug)
            if lenguaje == 'HTML' and DEBUG_MODE and candidato:
                print(f"   - Longitud: {len(candidato)} chars")
                print(f"   - Tiene DOCTYPE/html: {'<!DOCTYPE' in candidato or '<html' in candidato}")
                print(f"   - Tiene comentarios: {'<!--' in candidato}")
                print(f"   - Primeras 200 chars: {candidato[:200]}")
    
    if not candidatos:
        print(f"❌ No se generó código de calidad en {max_intentos} intentos")
        # Devolver el mejor aunque no sea perfecto
        if candidatos:
            return candidatos[0][1]
        return ""
    
    # Retornar el de mayor score
    candidatos.sort(reverse=True, key=lambda x: x[0])
    return candidatos[0][1]


def _es_diff_valido(texto: str) -> bool:
    """Valida que el texto sea un diff unificado válido"""
    if not texto:
        return False
    
    lineas = texto.strip().split("\n")
    tiene_header = any(l.startswith("---") or l.startswith("+++") for l in lineas)
    tiene_hunk = any(l.startswith("@@") for l in lineas)
    tiene_cambios = any(l.startswith("+") or l.startswith("-") for l in lineas)
    
    return tiene_header and (tiene_hunk or tiene_cambios)


def _es_codigo_de_calidad(codigo: str, lenguaje: str = "Python") -> bool:
    """
    Valida que el código generado tenga calidad mínima aceptable.
    RELAJADO para modelos locales Ollama (menos estricto).
    
    Criterios:
    - Longitud mínima (no trivial)
    - Estructura básica correcta
    - Sin patrones muy sospechosos
    """
    if not codigo or len(codigo.strip()) < 30:  # Reducido de 50 a 30
        return False
    
    # Verificar que no tenga comentarios (ya deberían haberse eliminado)
    if '# NO COMENTARIOS' in codigo or '// NO COMENTARIOS' in codigo:
        return False
    
    # DETECTAR comentarios excesivos (más de 30% del código son comentarios)
    lineas = codigo.split('\n')
    lineas_comentario = sum(1 for l in lineas if l.strip().startswith('#'))
    if lineas and (lineas_comentario / len(lineas)) > 0.3:
        return False  # Demasiados comentarios
    
    # DETECTAR imports duplicados (patrón sospechoso)
    imports = [l.strip() for l in lineas if l.strip().startswith('import ') or l.strip().startswith('from ')]
    if len(imports) != len(set(imports)):
        return False  # Hay imports duplicados
    
    # DETECTAR líneas idénticas repetidas más de 2 veces
    from collections import Counter
    lineas_no_vacias = [l.strip() for l in lineas if l.strip()]
    contador_lineas = Counter(lineas_no_vacias)
    for linea, count in contador_lineas.items():
        if count > 2 and len(linea) < 100:  # Línea corta repetida muchas veces
            return False
    
    # Verificar que no tenga patrones de código malo
    patrones_malos = [
        '.replace(\\\\n',  # Eliminar saltos de línea es sospechoso
        'gen_cal',  # Nombres muy cortos
        'a, m)',  # Parámetros de una letra
        'c = calendar',  # Variables de una letra
    ]
    
    for patron in patrones_malos:
        if patron in codigo:
            return False
    
    # DETECTAR uso de funciones/métodos privados (_nombre)
    import re
    if re.search(r'\b_[a-zA-Z_]\w*\s*\(', codigo):
        # Excepciones permitidas: __init__, __main__, __name__
        if not all(priv in ['__init__', '__main__', '__name__', '__file__'] 
                   for priv in re.findall(r'__(\w+)__', codigo)):
            return False
    
    # Para Python, verificar estructura básica
    if lenguaje.lower() == 'python':
        # Debe tener al menos un import o def o class
        if not any(kw in codigo for kw in ['import ', 'def ', 'class ']):
            return False
        
        # No debe tener líneas excesivamente largas (>200 chars)
        lineas = codigo.split('\n')
        if any(len(linea) > 200 for linea in lineas):
            return False
        
        # VERIFICAR COHERENCIA: si tiene imports, debe tener al menos una función/clase
        tiene_imports = any(l.strip().startswith('import ') or l.strip().startswith('from ') for l in lineas)
        tiene_funciones = any('def ' in l or 'class ' in l for l in lineas)
        
        if tiene_imports and not tiene_funciones:
            return False  # Solo imports sin código real
    
    # Para HTML, verificar estructura básica (RELAJADO para Ollama)
    elif lenguaje.lower() == 'html':
        # Aceptar HTML básico: debe tener al menos <html> o <!DOCTYPE>
        html_lower = codigo.lower()
        if '<!doctype' not in html_lower and '<html' not in html_lower:
            return False  # No es HTML válido
            
        # RELAJADO: Permitir HTML incompleto de modelos pequeños
        # Solo rechazar si está MUY roto
            
        # DETECTAR HTML MUY roto (tags con espacios entre letras)
        if re.search(r'<\s*t\s+h\s+s', codigo):  # <t h s ... > es HTML MUY roto
            return False
            
        # Verificar longitud razonable para HTML simple
        if len(codigo) > 10000:  # Aumentado de 5000 a 10000
            return False
            
        # ACEPTAR aunque tenga comentarios (se eliminarán después)
    
    # Para JavaScript/TypeScript
    elif lenguaje.lower() in ['javascript', 'typescript']:
        if not any(kw in codigo for kw in ['function ', 'const ', 'let ', 'var ', 'class ', '=>']):
            return False
    
    return True


def calcular_score_calidad(codigo: str) -> float:
    """
    Calcula un score de calidad del código (0.0 a 1.0).
    
    Factores:
    - Longitud adecuada
    - Nombres descriptivos
    - Estructura completa
    - Sin patrones sospechosos
    """
    score = 0.0
    
    # Longitud (max 0.3 puntos)
    longitud = len(codigo)
    if longitud > 200:
        score += 0.3
    elif longitud > 100:
        score += 0.2
    elif longitud > 50:
        score += 0.1
    
    # HTML: estructura completa (max 0.5 puntos)
    if '<!DOCTYPE' in codigo or '<html' in codigo:
        score += 0.2
    if '<head>' in codigo or '<head ' in codigo:
        score += 0.1
    if '<body>' in codigo or '<body ' in codigo:
        score += 0.1
    if '<table>' in codigo or '<table ' in codigo:
        score += 0.1
    
    # Python/otros: nombres descriptivos (max 0.3 puntos)
    if all(nombre not in codigo for nombre in [' gen_cal(', ' c =', ' a, m)']):
        score += 0.3
    
    # Python: estructura completa (max 0.2 puntos)
    if 'if __name__' in codigo or 'def main' in codigo:
        score += 0.2
    elif codigo.count('def ') >= 2:
        score += 0.15
    elif codigo.count('def ') >= 1:
        score += 0.1
    
    # Indentación consistente (max 0.2 puntos)
    lineas = [l for l in codigo.split('\n') if l.strip()]
    if lineas and all(not l.startswith('    ') or l.startswith('        ') for l in lineas):
        score += 0.2
    
    return min(score, 1.0)


def reparar_codigo(codigo: str, analisis: str = "", es_flutter: bool = False, max_intentos: int = 1) -> str:
    # Extraer código si viene en formato JSON con documentChunks
    codigo_procesado = extract_code(codigo)
    codigo_base = codigo_procesado[:2000]
    
    prompt = (
        "Eres un experto en programación.\n\n"
        "Corrige el siguiente código y devuelve el código COMPLETO corregido.\n\n"
        "REGLAS OBLIGATORIAS:\n"
        "- Devuelve SOLO el código completo corregido\n"
        "- NO expliques nada\n"
        "- NO uses texto antes o después\n"
        "- NO uses markdown (```)\n"
        "- NO uses formato diff\n"
        "- Escribe el código completo directamente\n\n"
        "CÓDIGO A CORREGIR:\n"
        + codigo_base
    )

    # LOG DEL PROMPT REAL QUE VA AL LLM
    print("\n" + "="*80)
    print("=== PROMPT START ===")
    print(prompt)
    print("=== PROMPT END ===")
    print(f"Longitud del prompt: {len(prompt)} chars")
    print("="*80 + "\n")

    candidatos = []
    for intento in range(max_intentos):
        print(f"🧠 REPARACIÓN intento {intento + 1}")
        resp = generate(prompt, max_tokens=2000)
        
        # LOG DE LA RESPUESTA RAW DEL LLM
        print("\n" + "="*80)
        print("=== RAW LLM RESPONSE START ===")
        print(f"Longitud: {len(resp) if resp else 0} chars")
        if resp:
            print(resp[:1000])
            if len(resp) > 1000:
                print(f"... ({len(resp) - 1000} chars más)")
        print("=== RAW LLM RESPONSE END ===")
        print("="*80 + "\n")
        
        # LIMPIEZA OBLIGATORIA: Eliminar markdown del LLM
        if resp:
            resp = clean_llm_output(resp)
        
        # Validar que sea código válido (no diff)
        if resp and len(resp.strip()) > 50 and not resp.startswith("---"):
            candidatos.append(resp)
            if DEBUG_MODE:
                print(f"✅ Código corregido generado correctamente")

    if not candidatos:
        if DEBUG_MODE:
            print(f"❌ No se generó código válido en {max_intentos} intentos")
        return ""
    
    return candidatos[0]
