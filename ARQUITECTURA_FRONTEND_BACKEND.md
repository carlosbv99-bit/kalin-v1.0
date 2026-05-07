# 🏗️ Arquitectura Frontend-Backend de Kalin

## Filosofía de Diseño

Kalin separa claramente las responsabilidades entre **Frontend inteligente** y **Backend estricto**:

---

## 🎨 Frontend (Inteligente e Intuitivo)

### Responsabilidades:
1. **Interpretar intención del usuario** en lenguaje natural
2. **Detectar solicitudes implícitas** de código
3. **Limpiar respuestas** del backend
4. **Presentar código limpio** al usuario

### Componentes Clave:

#### 1. Brain (`agent/core/brain.py`)
- Detecta intenciones desde frases naturales
- Ejemplos de detección implícita:
  ```
  "ayúdame a crear un calendario" → create
  "quiero una app de notas" → create  
  "cómo hago una función factorial" → create
  "necesito código para ordenar lista" → create
  ```

#### 2. Executor (`agent/actions/executor.py`)
- Recibe intención del brain
- Llama al backend apropiado
- Formatea y presenta resultado al usuario
- Guarda código generado para referencia futura

#### 3. Limpieza (`agent/actions/tools/fix_tool.py`)
- `limpiar_respuesta()`: Elimina texto introductorio del LLM
- `eliminar_comentarios()`: Remueve TODOS los comentarios del código
- `extraer_codigo()`: Extrae código de markdown si es necesario

---

## ⚙️ Backend (Estricto y Puro)

### Responsabilidades:
1. **Generar solo código** sin comentarios
2. **Sin explicaciones** ni texto adicional
3. **Código funcional** y ejecutable
4. **Respuesta predecible** y consistente

### Componentes Clave:

#### 1. Fix Tool (`agent/actions/tools/fix_tool.py`)
```python
def generar_codigo(requerimiento: str):
    prompt = """
    ROL: GENERADOR DE CÓDIGO - MODO ULTRA ESTRICTO
    
    REGLAS ABSOLUTAS:
    1. Genera ÚNICAMENTE código Python funcional
    2. PROHIBIDO cualquier comentario (#, //, /* */)
    3. PROHIBIDO texto explicativo
    4. PROHIBIDO markdown o formato especial
    5. Sin docstrings, sin comentarios inline
    6. Código debe empezar con import/def/class
    """
```

#### 2. Provider Manager (`agent/llm/provider_manager.py`)
- Envía prompts estrictos al modelo
- Recibe respuesta cruda
- Maneja retries y fallbacks

---

## 🔄 Flujo Completo

### Ejemplo: Usuario dice "ayúdame a crear un calendario en Python"

```
1. FRONTEND - Brain detecta intención
   Input: "ayúdame a crear un calendario en Python"
   ↓ Detecta: "ayúdame a" + "crear" + "calendario"
   Output: intencion = "create"

2. FRONTEND - Executor procesa
   ↓ Llama: fix_tool.generar_codigo("calendario en Python")

3. BACKEND - Fix Tool genera prompt estricto
   Prompt enviado al LLM:
   """
   ROL: GENERADOR DE CÓDIGO - MODO ULTRA ESTRICTO
   
   REGLAS ABSOLUTAS:
   - PROHIBIDO comentarios
   - Solo código puro
   - Sin explicaciones
   
   REQUERIMIENTO: calendario en Python
   """

4. BACKEND - LLM responde
   Respuesta cruda (puede tener comentarios):
   ```python
   # Calendario simple
   import calendar
   
   def mostrar_calendario(anio, mes):
       """Muestra calendario"""  # Docstring
       cal = calendar.TextCalendar()
       return cal.formatmonth(anio, mes)
   ```

5. FRONTEND - Limpieza automática
   ↓ limpiar_respuesta(): Quita markdown y texto introductorio
   ↓ eliminar_comentarios(): Remueve TODOS los comentarios
   
   Resultado limpio:
   ```python
   import calendar
   
   def mostrar_calendario(anio, mes):
       cal = calendar.TextCalendar()
       return cal.formatmonth(anio, mes)
   ```

6. FRONTEND - Presenta al usuario
   Output: 
   "✅ Código generado exitosamente:
   
   ```python
   import calendar
   
   def mostrar_calendario(anio, mes):
       cal = calendar.TextCalendar()
       return cal.formatmonth(anio, mes)
   ```"
```

---

## 🛡️ Capas de Seguridad para Código Limpio

### Capa 1: Prompt Estricto (Backend)
- Instrucciones claras al LLM
- Ejemplos de lo que SÍ y NO se quiere
- Prohibición explícita de comentarios

### Capa 2: Limpieza de Markdown (Frontend)
- Elimina ```python, ```, <code>, etc.
- Remueve texto introductorio ("Aquí está el código...")

### Capa 3: Eliminación de Comentarios (Frontend)
- Regex para quitar `# comentarios`
- Regex para quitar `// comentarios`
- Preserva strings que contengan # o //

### Capa 4: Validación Final (Frontend)
- Verifica que el código sea válido
- Rechaza respuestas tipo chatbot
- Score de calidad del código

---

## 💡 Ventajas de Esta Arquitectura

### 1. **Usuario Natural**
- No necesita aprender comandos
- Habla en lenguaje cotidiano
- "Ayúdame a..." es suficiente

### 2. **Código Limpio Garantizado**
- Múltiples capas de limpieza
- Sin comentarios innecesarios
- Listo para copiar y usar

### 3. **Backend Predecible**
- Prompts estrictos y consistentes
- Respuestas uniformes
- Fácil de debuggear

### 4. **Flexibilidad**
- Si el LLM falla, el frontend compensa
- Múltiples intentos automáticos
- Fallbacks inteligentes

---

## 📋 Casos de Uso

### Caso 1: Solicitud Explícita
```
Usuario: "/create calendario en Python"
Brain: intencion = "create"
Backend: Genera código
Frontend: Limpia y muestra
```

### Caso 2: Solicitud Implícita
```
Usuario: "ayúdame a hacer una calculadora"
Brain: Detecta "ayúdame a" → intencion = "create"
Backend: Genera código
Frontend: Limpia y muestra
```

### Caso 3: Petición de Mejora
```
Usuario: "muéstrame el código sin comentarios"
Brain: Detecta "sin comentarios" → intencion = "show_code"
Frontend: Obtiene último código, elimina comentarios, muestra
```

### Caso 4: Conversación Normal
```
Usuario: "hola, ¿qué tal?"
Brain: Detecta saludo → intencion = "greeting"
Frontend: Responde conversacionalmente (no genera código)
```

---

## 🎯 Reglas de Oro

### Para el Backend:
1. ✅ SIEMPRE prohibir comentarios en prompts
2. ✅ SIEMPRE pedir "SOLO CÓDIGO"
3. ✅ SIEMPRE dar ejemplos de lo esperado
4. ✅ NUNCA confiar ciegamente en la respuesta del LLM

### Para el Frontend:
1. ✅ SIEMPRE limpiar respuestas del backend
2. ✅ SIEMPRE eliminar comentarios como seguridad
3. ✅ SIEMPRE detectar intenciones implícitas
4. ✅ NUNCA asumir que el usuario sabe comandos

---

## 🔧 Implementación Técnica

### Detección de Intención Implícita
```python
# agent/core/brain.py
if any(frase in mensaje for frase in [
    "ayúdame a", "ayudame a", "ayuda con",
    "quiero un", "necesito un", "busco un",
    "cómo hago", "como hago", "cómo crear",
    "código para", "codigo para", "programa para",
]):
    return "create"  # ¡Generar código!
```

### Limpieza de Comentarios
```python
# agent/actions/tools/fix_tool.py
def eliminar_comentarios(codigo: str) -> str:
    lineas = codigo.split('\n')
    lineas_limpias = []
    
    for linea in lineas:
        if '#' in linea or '//' in linea:
            linea_limpia = re.sub(r'\s*#.*$', '', linea)
            linea_limpia = re.sub(r'\s*//.*$', '', linea_limpia)
            if linea_limpia.strip():
                lineas_limpias.append(linea_limpia.rstrip())
        else:
            lineas_limpias.append(linea)
    
    return '\n'.join(lineas_limpias)
```

### Prompt Ultra Estricto
```python
prompt = f"""
REGLAS ABSOLUTAS (NO VIOLAR NINGUNA):
1. Genera ÚNICAMENTE código {lenguaje} funcional
2. PROHIBIDO cualquier comentario en el código
3. PROHIBIDO texto explicativo antes o después
4. PROHIBIDO markdown o formato especial
5. Sin docstrings, sin comentarios inline
6. El código debe empezar DIRECTAMENTE con import/def/class
7. Si no puedes cumplir, devuelve cadena vacía

EJEMPLO DE LO QUE QUIERO:
import datetime
def funcion():
    return True

EJEMPLO DE LO QUE NO QUIERO:
# Comentario
import datetime  # Otro comentario
def funcion():
    \"\"\"Docstring\"\"\"  # NO
    return True
"""
```

---

## 📊 Métricas de Calidad

### Backend Exitoso:
- ✅ Código sin comentarios: 95%+
- ✅ Respuesta en <30 segundos
- ✅ Código ejecutable: 90%+

### Frontend Exitoso:
- ✅ Detección correcta de intención: 98%+
- ✅ Limpieza efectiva: 100%
- ✅ Usuario satisfecho: 95%+

---

## 🚀 Próximas Mejoras

1. **IA más inteligente para limpieza**
   - Usar AST parser para eliminar comentarios correctamente
   - Preservar docstrings importantes

2. **Detección de contexto**
   - Recordar conversaciones anteriores
   - Sugerir mejoras basadas en código previo

3. **Validación automática**
   - Ejecutar código generado en sandbox
   - Reportar errores antes de mostrar al usuario

4. **Personalización**
   - Permitir al usuario elegir nivel de comentarios
   - Estilos de código preferidos

---

## ✨ Resumen

**Frontend**: Inteligente, intuitivo, interpreta lenguaje natural  
**Backend**: Estricto, predecible, genera solo código puro  
**Limpieza**: Múltiples capas garantizan código sin comentarios  
**Resultado**: Usuario habla naturalmente, recibe código limpio  

🎯 **El usuario NO necesita saber comandos. Solo habla naturalmente.**
