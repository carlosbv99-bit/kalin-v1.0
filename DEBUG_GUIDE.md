# 🔍 Sistema de Debug Completo - Kalin

## Visión General

Kalin ahora cuenta con un **sistema avanzado de debugging** que te permite ver exactamente qué está pasando en cada paso del proceso de generación y análisis de código.

---

## ¿Qué puedes ver con el modo DEBUG?

### ✅ Información Completa

1. **PROMPT ENVIADO AL LLM**: El texto exacto que se envía al modelo
2. **RESPUESTA RAW DEL MODELO**: La respuesta cruda sin procesar
3. **CÓDIGO PARSEADO**: El código final después de limpieza y extracción
4. **MÉTRICAS**: Tokens usados, costo, tiempo de respuesta
5. **PROCESO COMPLETO**: Cada paso desde el análisis hasta la generación

---

## Cómo Activar el Modo DEBUG

### Opción 1: Variable de Entorno (.env)

Edita tu archivo `.env`:

```env
# Cambiar de 0 a 1 para activar
KALIN_DEBUG=1
```

### Opción 2: Variable de Sistema

```bash
# Windows PowerShell
$env:KALIN_DEBUG="1"

# Linux/Mac
export KALIN_DEBUG=1
```

### Opción 3: En línea de comandos

```bash
KALIN_DEBUG=1 python run.py
```

---

## Ejemplo de Output con DEBUG Activado

### Cuando ejecutas `/fix main.py`:

```
================================================================================
🔍 [ANALYZER] PROMPT ENVIADO AL LLM:
================================================================================

Eres un experto en programación.

Analiza este código y detecta errores:

def hello():
    print("world"

Responde claro.

================================================================================


================================================================================
📥 [ANALYZER] RESPUESTA RECIBIDA DEL LLM:
================================================================================

El código tiene un error de sintaxis: falta cerrar el paréntesis en la línea 2.

Debería ser: print("world")

================================================================================


================================================================================
🛠️ [FIX_TOOL] PROMPT DE GENERACIÓN:
================================================================================

ROL: GENERADOR DE CÓDIGO - MODO ESTRICTO

INSTRUCCIONES CRÍTICAS:
- Genera ÚNICAMENTE código Python puro
- PROHIBIDO cualquier texto explicativo antes o después del código
...

================================================================================


================================================================================
📥 [FIX_TOOL] RESPUESTA RAW DEL MODELO:
================================================================================

Longitud: 245 chars
Primeros 500 chars:
Aquí está el código corregido:

```python
def hello():
    print("world")
```

Espero que esto ayude.

================================================================================


================================================================================
🧹 [FIX_TOOL] CÓDIGO DESPUÉS DE LIMPIEZA:
================================================================================

Longitud: 180 chars
def hello():
    print("world")
```

================================================================================


================================================================================
✅ [FIX_TOOL] CÓDIGO FINAL PARSEADO:
================================================================================

Longitud: 35 chars
def hello():
    print("world")
================================================================================
```

---

## Niveles de Debugging

### Nivel 0: Producción (Default)
```env
KALIN_DEBUG=0
```
- Solo muestra información básica
- Ideal para uso diario
- Output limpio y conciso

### Nivel 1: Desarrollo/Debug
```env
KALIN_DEBUG=1
```
- Muestra prompts completos
- Muestra respuestas raw
- Muestra código parseado
- Muestra métricas detalladas
- Ideal para troubleshooting

---

## Dónde se aplica el Debug

### 1. Analyzer (`agent/analyzer.py`)
- 📤 Prompt enviado para análisis de código
- 📥 Respuesta del análisis

### 2. Fix Tool (`agent/actions/tools/fix_tool.py`)
- 📤 Prompt de generación de código
- 📥 Respuesta raw del modelo
- 🧹 Código después de limpieza
- ✅ Código final parseado
- 📤 Prompt de reparación
- 📥 Diff recibido

### 3. Provider Manager (`agent/llm/provider_manager.py`)
- 📤 Prompt completo enviado al proveedor
- 📥 Respuesta completa del proveedor
- 📊 Métricas (tokens, costo, etc.)

---

## Casos de Uso

### Caso 1: El código generado no es válido

**Sin DEBUG:**
```
❌ Código inválido
```

**Con DEBUG:**
```
📥 RESPUESTA RAW DEL MODELO:
Aquí está el código que pediste...
[ves que el modelo agregó texto introductorio]

🧹 CÓDIGO DESPUÉS DE LIMPIEZA:
[código limpio pero incompleto]

✅ CÓDIGO FINAL PARSEADO:
[código truncado]

💡 Solución: Ajustar el prompt para ser más estricto
```

### Caso 2: El modelo no entiende el prompt

**Con DEBUG puedes ver:**
- Exactamente qué prompt se envió
- Si el prompt está bien formateado
- Si hay instrucciones contradictorias
- Qué respondió el modelo

### Caso 3: Debugging de estrategias

**Con DEBUG puedes comparar:**
- Diferentes prompts
- Diferentes respuestas
- Qué estrategia funciona mejor
- Por qué ciertas respuestas fallan

---

## Tips de Debugging

### Tip 1: Capturar output en archivo

```bash
# Windows
python run.py > debug_output.txt 2>&1

# Linux/Mac
python run.py 2>&1 | tee debug_output.txt
```

### Tip 2: Buscar patrones específicos

```bash
# Buscar todos los prompts enviados
grep "PROMPT ENVIADO" debug_output.txt

# Buscar respuestas del modelo
grep "RESPUESTA.*MODELO" debug_output.txt

# Buscar código parseado
grep "CÓDIGO FINAL PARSEADO" debug_output.txt
```

### Tip 3: Comparar múltiples intentos

Activa DEBUG y ejecuta el mismo comando varias veces para ver:
- Si las respuestas son consistentes
- Si el modelo mejora con reintentos
- Qué variaciones hay

---

## Estructura del Output

Cada sección de debug sigue este formato:

```
================================================================================
🏷️ [COMPONENTE] DESCRIPCIÓN:
================================================================================
[Contenido]
================================================================================
```

### Componentes:
- `[ANALYZER]` - Análisis de código
- `[FIX_TOOL]` - Generación/reparación de código
- `[PROVIDER_MANAGER]` - Llamadas al proveedor LLM

### Emojis:
- 📤 = Enviado (prompt)
- 📥 = Recibido (respuesta)
- 🧹 = Después de limpieza
- ✅ = Resultado final
- 🔍 = Información/diagnóstico
- 🛠️ = Herramienta/proceso
- 🔧 = Reparación

---

## Desactivar DEBUG

Para volver al modo normal:

```env
# En .env
KALIN_DEBUG=0
```

O simplemente comenta la línea:

```env
# KALIN_DEBUG=1
```

---

## Impacto en Rendimiento

### Modo DEBUG Desactivado (KALIN_DEBUG=0)
- ✅ Sin impacto en rendimiento
- ✅ Output limpio
- ✅ Ideal para producción

### Modo DEBUG Activado (KALIN_DEBUG=1)
- ⚠️ Output verbose (puede ser largo)
- ⚠️ Ligeramente más lento por prints
- ✅ Insignificante en términos de velocidad real
- ✅ No afecta la calidad del código generado

---

## Ejemplos Prácticos

### Ejemplo 1: Debugging de un fix fallido

```bash
# Activar DEBUG
# Editar .env: KALIN_DEBUG=1

# Ejecutar fix
python run.py

# En la interfaz web: /fix problematic_file.py

# Revisar output en consola:
# 1. Ver prompt enviado
# 2. Ver respuesta del modelo
# 3. Ver código parseado
# 4. Identificar dónde falla el proceso
```

### Ejemplo 2: Optimización de prompts

```bash
# Con DEBUG activado, puedes:
# 1. Ver qué prompt se envía
# 2. Ver cómo responde el modelo
# 3. Ajustar el prompt en el código
# 4. Probar nuevamente
# 5. Comparar resultados
```

### Ejemplo 3: Testing de diferentes modelos

```bash
# Cambiar modelo en .env
OLLAMA_MODEL=deepseek-coder:latest

# Con DEBUG, ver:
# - Cómo responde deepseek-coder
# - Calidad del código generado
# - Comparar con otros modelos
```

---

## Troubleshooting Común

### Problema: No veo output de debug

**Solución:**
1. Verifica que `KALIN_DEBUG=1` en `.env`
2. Reinicia el servidor (`python run.py`)
3. Verifica que estás viendo la consola donde corre Flask

### Problema: Output demasiado largo

**Solución:**
1. Redirige a archivo: `python run.py > debug.log 2>&1`
2. Usa `grep` para buscar secciones específicas
3. Desactiva DEBUG cuando no lo necesites

### Problema: No entiendo el output

**Solución:**
1. Busca los emojis (📤 📥 ✅ 🧹)
2. Lee las etiquetas de componente ([ANALYZER], [FIX_TOOL])
3. Sigue el flujo: Prompt → Respuesta → Limpieza → Código Final

---

## Futuras Mejoras

🚀 **Roadmap de Debugging:**

1. **Niveles de verbosidad**: DEBUG_BASIC, DEBUG_VERBOSE, DEBUG_FULL
2. **Filtros por componente**: Activar debug solo para analyzer o fix_tool
3. **Exportación a JSON**: Guardar debug estructurado para análisis
4. **Visualización web**: Ver debug en interfaz web
5. **Comparador de prompts**: UI para comparar diferentes prompts
6. **Métricas avanzadas**: Tiempo por etapa, success rate, etc.
7. **Alertas inteligentes**: Detectar automáticamente problemas comunes

---

## Resumen

El **Sistema de Debug Completo** te da visibilidad total del proceso interno de Kalin:

✅ Ves exactamente qué prompts se envían  
✅ Ves las respuestas crudas del modelo  
✅ Ves cómo se limpia y parsea el código  
✅ Puedes identificar problemas rápidamente  
✅ Puedes optimizar prompts y estrategias  
✅ Es configurable y fácil de activar/desactivar  

**¡Ahora tienes control total sobre el debugging!** 🔍✨
