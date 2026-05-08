# 🔧 SOLUCIÓN DE PROBLEMAS - Generación de Código

## Problema: El agente sigue generando código de calendario

### Síntoma
```
Usuario: "quiero crear una agenda personal"
Agente: genera código con `import calendar` y función `generar_calendario()`
```

---

## Causa Raíz

**El servidor web no se reinició después de los cambios en el código.**

Python carga los módulos en memoria al iniciar. Si modificas archivos `.py` pero no reinicias el servidor, **sigue usando el código antiguo**.

---

## Solución Rápida (Windows)

### Opción 1: Script Automático ✅ RECOMENDADO

1. **Ejecuta el script de reinicio**:
   ```bash
   # Doble clic en:
   E:\kalin\reiniciar_servidor.bat
   ```

2. **El script hará automáticamente**:
   - ✓ Detiene todos los servidores Python
   - ✓ Limpia cache de Python (`__pycache__`)
   - ✓ Inicia el servidor web nuevo

3. **Abre tu navegador**:
   ```
   http://127.0.0.1:5000
   ```

4. **Prueba**:
   ```
   "quiero crear una agenda personal en Python"
   ```

---

### Opción 2: Manual

1. **Detén el servidor actual**:
   - Ve a la terminal donde está corriendo
   - Presiona `Ctrl+C`

2. **Limpia cache manualmente** (PowerShell):
   ```powershell
   cd E:\kalin
   Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
   Remove-Item -Recurse -Force agent\__pycache__ -ErrorAction SilentlyContinue
   Remove-Item -Recurse -Force agent\core\__pycache__ -ErrorAction SilentlyContinue
   Remove-Item -Recurse -Force agent\actions\__pycache__ -ErrorAction SilentlyContinue
   Remove-Item -Recurse -Force agent\actions\tools\__pycache__ -ErrorAction SilentlyContinue
   ```

3. **Reinicia el servidor**:
   ```bash
   python web.py
   ```

4. **Prueba en el navegador**:
   ```
   http://127.0.0.1:5000
   ```

---

## Cómo Verificar que Funciona

### Logs Correctos ✅

Deberías ver en los logs:
```
🧠 GENERACIÓN intento 1/3
❌ RECHAZADO TEMPRANO: Generó calendario en lugar de agenda personal
   Longitud: 907 chars
   Primera línea: import calendar
🧠 GENERACIÓN intento 2/3
✅ Código de calidad aceptable en intento 2 (score: 0.85)
```

**Indicadores de éxito**:
- ✅ Aparece `❌ RECHAZADO TEMPRANO` cuando intenta generar calendar
- ✅ Reintenta automáticamente
- ✅ Eventualmente genera código SIN calendar
- ✅ Score > 0.7

### Logs Incorrectos ❌

Si ves esto, el servidor NO se reinició:
```
FORMATO CORRECTO:
import calendar

def generar_calendario():
    pass
```

**Solución**: Reinicia el servidor obligatoriamente.

---

## Cambios Implementados

### 1. Validación Temprana Anti-Calendario
**Archivo**: `agent/actions/tools/fix_tool.py` (líneas ~597-603)

```python
# VALIDACIÓN ESPECIAL TEMPRANA: Rechaza ANTES de validar calidad
if candidato and 'agenda' in requerimiento.lower() and 'import calendar' in candidato.lower():
    print(f"❌ RECHAZADO TEMPRANO: Generó calendario en lugar de agenda personal")
    continue  # Reintentar inmediatamente
```

**Cómo funciona**:
1. Detecta si el usuario pidió "agenda"
2. Verifica si el código tiene `import calendar`
3. Si ambos son verdad → **RECHAZA INMEDIATAMENTE**
4. No pierde tiempo validando calidad
5. Reintenta generación

---

### 2. Ejemplos Genéricos Sin Calendario
**Archivo**: `agent/actions/tools/fix_tool.py`

- ✅ HTML: Página web moderna con botón (NO tabla de calendario)
- ✅ JavaScript: Clase AgendaPersonal (NO función generarCalendario)
- ✅ Python: Clase AgendaPersonal con CRUD de contactos

---

### 3. Prompt Principal Universal
**Archivo**: `agent/actions/tools/fix_tool.py` (líneas ~556-590)

```python
prompt = f"""ERES UN GENERADOR DE CÓDIGO PROFESIONAL.

INSTRUCCIONES IMPORTANTES:
- Analiza el REQUERIMIENTO del usuario cuidadosamente
- Genera código apropiado para el tipo de aplicación solicitada
- Usa nombres de variables descriptivos y profesionales
- Sigue las mejores prácticas del lenguaje {lenguaje}
{instrucciones_extra}

FORMATO CORRECTO:
{ejemplo_bueno}  # ← Ejemplo dinámico según lenguaje

REQUERIMIENTO DEL USUARIO:
{requerimiento}

GENERA AHORA SOLO EL CÓDIGO {lenguaje.upper()}:"""
```

**Ventajas**:
- ✅ No menciona "agenda personal" específicamente
- ✅ Se adapta a cualquier tipo de aplicación
- ✅ El ejemplo cambia según el lenguaje detectado
- ✅ Sin referencias confusas a calendarios

---

## Testing Completo

### Prueba 1: Agenda Personal Python
```
Mensaje: "quiero crear una agenda personal en Python"

Resultado esperado:
→ Detecta lenguaje: Python
→ Rechaza intentos con 'import calendar'
→ Genera clase AgendaPersonal con métodos CRUD
→ Score > 0.7
```

### Prueba 2: App Web HTML
```
Mensaje: "crea una página web moderna en HTML"

Resultado esperado:
→ Detecta lenguaje: HTML
→ Genera HTML completo con CSS moderno
→ Diseño responsive con container, botones, etc.
→ NO tiene referencias a calendario
```

### Prueba 3: API JavaScript
```
Mensaje: "necesito una API REST en JavaScript"

Resultado esperado:
→ Detecta lenguaje: JavaScript
→ Genera código JS con rutas/endpoints
→ Estructura profesional
```

---

## Preguntas Frecuentes

### ¿Por qué necesito reiniciar el servidor?
Python carga los módulos `.py` en memoria RAM al iniciar. Los cambios en disco no se reflejan hasta que reinicias el proceso.

### ¿Cada vez que cambio código debo reiniciar?
Sí, cada vez que modificas archivos `.py` en:
- `agent/core/*.py`
- `agent/actions/*.py`
- `agent/actions/tools/*.py`
- `web.py`

### ¿Hay forma de evitar reiniciar?
Sí, puedes usar herramientas como:
- `flask --reload` (auto-reload en desarrollo)
- `watchdog` (monitorea cambios y reinicia automáticamente)

Pero para producción, siempre reinicia manualmente.

### ¿Qué pasa si no limpio el cache?
Python puede usar archivos `.pyc` compilados antiguos, ignorando tus cambios en `.py`. Por eso limpiamos `__pycache__`.

---

## Checklist de Verificación

Antes de reportar un problema, verifica:

- [ ] ¿Reiniciaste el servidor después de los cambios?
- [ ] ¿Limpiaste la carpeta `__pycache__`?
- [ ] ¿Los logs muestran el prompt nuevo (sin "import calendar")?
- [ ] ¿Aparece el mensaje "❌ RECHAZADO TEMPRANO"?
- [ ] ¿Probaste en una ventana nueva del navegador (Ctrl+Shift+R)?

---

## Contacto

Si después de reiniciar el servidor el problema persiste:

1. Copia los logs completos
2. Indica qué mensaje enviaste
3. Muestra el código generado
4. Verifica la versión de Python: `python --version`

---

## Fecha de Actualización
**2026-05-08**

## Archivos Relacionados
- `reiniciar_servidor.bat` - Script de reinicio automático
- `agent/actions/tools/fix_tool.py` - Lógica de generación de código
- `NUEVA_ARQUITECTURA_PROMPTS.md` - Documentación de prompts
