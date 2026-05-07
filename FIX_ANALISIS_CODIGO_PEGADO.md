# 🐛 Problema: Análisis de Código Pegado Directamente

## Situación Actual

Cuando el usuario dice **"Analiza este código"** y pega un bloque de código entre ```:

```
MENSAJE DEL USUARIO: "Analiza este código"

CÓDIGO A ANALIZAR:
```dart
import 'package:flutter/material.dart';
...
```
```

El sistema:
1. ✅ Detecta intención "analyze" correctamente
2. ❌ Intenta buscar un archivo llamado "este código" en disco
3. ❌ No encuentra el archivo → Error
4. ❌ O peor: ignora el código pegado y analiza algo diferente

---

## Problemas Identificados

### 1. **Código Incompleto**
El código proporcionado se corta abruptamente:
```dart
if (
```
No hay cierre del `if`, lo que causa errores de sintaxis.

### 2. **LLM Genera Análisis Incorrecto**
El análisis generado tiene errores:
- Dice "Lenguaje Incorrecto" pero luego dice "Esto es correcto" (contradictorio)
- Menciona problemas que no son reales (los imports están bien)
- No detecta el problema real: código truncado

### 3. **Executor No Maneja Código Pegado**
La sección `analyze` en executor.py siempre busca archivos en disco:
```python
ruta = utils["buscar_archivo_inteligente"](nombre, ruta_proyecto_actual)
if not ruta:
    return jsonify({"respuesta": f"❌ Archivo '{nombre}' no encontrado..."})
```

No verifica si hay código pegado directamente en el mensaje.

---

## Solución Propuesta

### Paso 1: Detectar Código Pegado en el Mensaje

En `executor.py`, antes de buscar archivos, verificar si hay código entre ``` en el mensaje:

```python
if intencion == "analyze":
    nombre = args.get("arg")
    mensaje_original = contexto.get("mensaje", "")
    
    # VERIFICAR SI HAY CÓDIGO PEGADO DIRECTAMENTE
    import re
    code_blocks = re.findall(r'```(?:\w+)?\s*\n(.*?)\n```', mensaje_original, re.DOTALL)
    
    if code_blocks:
        # Hay código pegado, analizarlo directamente
        codigo = code_blocks[0]  # Tomar primer bloque
        
        # Detectar lenguaje
        lang_match = re.search(r'```(\w+)', mensaje_original)
        language = lang_match.group(1) if lang_match else "unknown"
        
        # Verificar si el código está completo
        if is_code_truncated(codigo):
            return jsonify({
                "respuesta": "⚠️ El código proporcionado parece estar incompleto o truncado.\n\n"
                           "Por favor, proporciona el código COMPLETO para poder analizarlo correctamente.\n\n"
                           "El código se corta en:\n" + get_last_complete_line(codigo)
            })
        
        # Analizar código directamente
        contexto_analisis = {
            "user_message": contexto.get("mensaje", "Analiza este código"),
            "project_type": detect_language(language),
            "files": [f"code_snippet.{language}"],
            "conversation_history": True,
            "is_inline_code": True  # Flag para indicar que es código pegado
        }
        
        start_time = time.time()
        analisis = analizar_codigo(codigo, contexto=contexto_analisis)
        duration = time.time() - start_time
        
        # Guardar en memoria conversacional
        self.conversation_memory.update_context(
            intention="analyze",
            args={"source": "inline_code", "language": language},
            result=analisis,
            metadata={
                "duration": duration,
                "file_type": language,
                "code_length": len(codigo)
            }
        )
        
        return jsonify({
            "respuesta": f"🔍 **Análisis del código proporcionado:**\n\n{analisis}"
        })
    
    # Si no hay código pegado, continuar con búsqueda de archivo normal...
```

### Paso 2: Funciones Auxiliares

```python
def is_code_truncated(code: str) -> bool:
    """Detecta si el código está truncado/incompleto"""
    lines = code.strip().split('\n')
    last_line = lines[-1].strip() if lines else ""
    
    # Patrones de código incompleto
    incomplete_patterns = [
        r'if\s*\($',           # if ( sin cerrar
        r'for\s*\(',           # for ( sin cerrar
        r'while\s*\(',         # while ( sin cerrar
        r'def\s+\w+\([^)]*$',  # def func( sin cerrar
        r'class\s+\w+\([^)]*$', # class X( sin cerrar
        r'\{$',                # { sin cerrar (en lenguajes C-style)
        r'=>\s*$',             # => sin cuerpo (Dart/JS)
    ]
    
    for pattern in incomplete_patterns:
        if re.search(pattern, last_line):
            return True
    
    # Verificar balance de llaves/paréntesis
    open_braces = code.count('{') - code.count('}')
    open_parens = code.count('(') - code.count(')')
    
    if open_braces > 0 or open_parens > 0:
        return True
    
    return False


def get_last_complete_line(code: str) -> str:
    """Obtiene la última línea completa antes del corte"""
    lines = code.strip().split('\n')
    # Buscar la última línea que termine con ; o }
    for line in reversed(lines[:-1]):  # Excluir última línea (incompleta)
        if line.strip().endswith(';') or line.strip().endswith('}'):
            return line.strip()
    return lines[-2].strip() if len(lines) > 1 else lines[0].strip()


def detect_language(lang_name: str) -> str:
    """Convierte nombre de lenguaje a extensión"""
    lang_map = {
        'dart': 'dart',
        'python': 'py',
        'javascript': 'js',
        'typescript': 'ts',
        'java': 'java',
        'html': 'html',
        'css': 'css',
    }
    return lang_map.get(lang_name.lower(), 'txt')
```

---

## Comportamiento Esperado

### Escenario 1: Código Completo
```
Usuario: "Analiza este código
```dart
void main() {
  print('Hello');
}
```"

Respuesta:
🔍 **Análisis del código proporcionado:**

El código es una función main básica en Dart...
✅ Código completo y válido
```

### Escenario 2: Código Incompleto
```
Usuario: "Analiza este código
```dart
void main() {
  if (
```"

Respuesta:
⚠️ El código proporcionado parece estar incompleto o truncado.

Por favor, proporciona el código COMPLETO para poder analizarlo correctamente.

El código se corta en:
void main() {
```

---

## Beneficios

✅ **Soporte para código pegado**: No requiere guardar en archivo primero  
✅ **Detección de código incompleto**: Evita análisis erróneos  
✅ **Mejor UX**: Mensajes claros sobre qué está mal  
✅ **Flexibilidad**: Usuario puede pegar snippets rápidos  

---

## Implementación Prioritaria

1. **Alta prioridad**: Agregar detección de código pegado en executor.py
2. **Media prioridad**: Implementar detección de código truncado
3. **Baja prioridad**: Mejorar prompts de análisis para evitar respuestas contradictorias

---

## Notas Adicionales

### Sobre el Análisis Incorrecto del LLM

El LLM generó un análisis con errores porque:
1. El código estaba incompleto
2. El prompt no especificaba que debía detectar truncamiento
3. El modelo intentó "adivinar" en lugar de reportar el problema

**Solución**: Agregar al prompt de análisis:
```
IMPORTANTE:
- Si el código está incompleto o truncado, REPÓRTALO inmediatamente
- NO intentes adivinar qué falta
- Indica exactamente dónde se corta el código
```

---

## Conclusión

El sistema necesita soporte nativo para analizar código pegado directamente en el chat, con validación de integridad antes de procesar.
