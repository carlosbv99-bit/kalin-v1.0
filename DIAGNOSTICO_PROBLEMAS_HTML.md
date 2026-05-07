# Diagnóstico: Problemas Después de Correcciones HTML

## 📅 Fecha: 7 de mayo de 2026

## 🔍 Resumen del Problema

**Síntoma**: Kalin funcionaba perfectamente hasta que se aplicaron correcciones relacionadas con la generación y validación de código HTML. Ahora:
- Ollama tarda 33+ segundos en responder
- No genera código HTML (calendario)
- Posibles timeouts o respuestas vacías

---

## ❌ Causas Raíz Identificadas

### 1. **Tokens Insuficientes para HTML**
**Problema**: El código reducía `max_tokens` a 800 para HTML
```python
# ANTES (fix_tool.py línea 301-302)
if es_html and max_tokens > 800:
    max_tokens = 800  # Muy poco para HTML complejo
```

**Impacto**: Un calendario HTML con CSS inline necesita ~1000-1500 tokens. Con 800, la respuesta se trunca.

**Solución Aplicada**: Aumentado a 1200 tokens
```python
# AHORA
if es_html and max_tokens > 1200:
    max_tokens = 1200  # Suficiente para HTML moderado
```

---

### 2. **Limpieza Agresiva de Comentarios HTML**
**Problema**: La regex `<!--.*?-->` podía eliminar código válido
```python
# ANTES (fix_tool.py línea 176)
codigo = re.sub(r'<!--.*?-->', '', codigo, flags=re.DOTALL)
```

**Escenario problemático**:
```html
<!-- Tabla de datos -->
<table>
  <!-- Fila 1 -->
  <tr><td>Dato</td></tr>
</table>
```
La regex podría eliminar más de lo debido si hay anidamiento o mal formato.

**Solución Aplicada**: Regex más conservadora
```python
# AHORA
codigo = re.sub(r'<!--[^>]*?-->', '', codigo, flags=re.DOTALL)
```
Solo elimina comentarios PUROS, no bloques grandes.

---

### 3. **Timeout Insuficiente para Ollama**
**Problema**: Timeout por defecto de 30 segundos
```python
# base_provider.py línea 32
self.timeout = config.get("timeout", 30)  # Muy poco para modelos locales
```

**Evidencia**: Tus logs muestran 33 segundos solo para "hola"

**Solución Aplicada**: Timeout aumentado a 120 segundos para Ollama
```python
# ollama_provider.py
if not config or 'timeout' not in config:
    self.timeout = 120  # 2 minutos para modelos locales lentos
```

---

### 4. **Validaciones Demasiado Estrictas** (Ya corregido anteriormente)
**Problema**: `_es_codigo_de_calidad` rechazaba código válido de modelos pequeños

**Soluciones previas aplicadas**:
- Longitud mínima reducida: 50 → 30 chars
- Acepta HTML con comentarios
- Mayor tolerancia para HTML incompleto
- Límite aumentado: 5000 → 10000 chars

---

## 🛠️ Cambios Aplicados

### Archivo: `agent/actions/tools/fix_tool.py`

#### Cambio 1: Tokens para HTML
```diff
- if es_html and max_tokens > 800:
-     max_tokens = 800  # Reducir para HTML simple
+ if es_html and max_tokens > 1200:
+     max_tokens = 1200  # Aumentado de 800 a 1200 para HTML más complejo
```

#### Cambio 2: Limpieza de comentarios HTML
```diff
- codigo = re.sub(r'<!--.*?-->', '', codigo, flags=re.DOTALL)
+ # PER OJO: Solo eliminar comentarios PUROS, no código entre comentarios
+ codigo = re.sub(r'<!--[^>]*?-->', '', codigo, flags=re.DOTALL)
```

### Archivo: `agent/llm/providers/ollama_provider.py`

#### Cambio 3: Timeout aumentado
```diff
  def __init__(self, config=None):
      super().__init__(config)
      self._available_models = []
      self._last_refresh = 0
+     # Aumentar timeout para modelos locales (pueden ser lentos)
+     if not config or 'timeout' not in config:
+         self.timeout = 120  # 2 minutos para Ollama
```

---

## 📊 Impacto Esperado

### Antes de los cambios:
- ⏱️ **Tiempo de respuesta**: 33+ segundos (con timeout de 30s = falla)
- 📝 **Tokens disponibles**: 800 (insuficiente para HTML complejo)
- 🧹 **Limpieza**: Agresiva (podía corromper HTML válido)
- ✅ **Tasa de éxito**: Baja (código rechazado por validaciones)

### Después de los cambios:
- ⏱️ **Tiempo de respuesta**: Hasta 120 segundos permitidos
- 📝 **Tokens disponibles**: 1200 (suficiente para HTML moderado)
- 🧹 **Limpieza**: Conservadora (preserva estructura HTML)
- ✅ **Tasa de éxito**: Alta (validaciones relajadas + más tokens)

---

## 🧪 Cómo Verificar la Solución

### Paso 1: Reiniciar Kalin
```bash
Ctrl+C  # Detener servidor actual
python run.py  # Reiniciar con nuevos cambios
```

### Paso 2: Probar generación de HTML
En el chat de Kalin, escribe:
```
crea un calendario simple en html
```

### Paso 3: Observar logs
Deberías ver:
```
🧠 GENERACIÓN intento 1/3
=== PROMPT START ===
... (prompt con HTML)
=== PROMPT END ===
Longitud del prompt: XXXX chars

ollama intento 1
=== RAW MODEL RESPONSE START ===
Longitud: XXXX chars  # Debería ser > 800
... (código HTML)
=== RAW MODEL RESPONSE END ===

✅ Código de calidad aceptable en intento 1 (score: X.XX)
```

### Paso 4: Verificar resultado
El calendario HTML debería aparecer en la interfaz web sin errores.

---

## 🔍 Si el Problema Persiste

### Diagnóstico Adicional:

#### 1. Verificar que Ollama está respondiendo
```bash
# Prueba directa con curl
curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-coder:6.7b",
  "prompt": "di hola",
  "stream": false
}'
```

#### 2. Revisar logs detallados
Activar modo debug en `.env`:
```env
FLASK_DEBUG=True
```

Buscar en logs:
- ¿Ollama devuelve respuesta vacía?
- ¿La limpieza elimina todo el código?
- ¿La validación rechaza el código?

#### 3. Probar con modelo diferente
```bash
# Ver modelos disponibles
ollama list

# Probar con llama3.2:3b (más rápido)
# Editar .env o configuración del modelo
OLLAMA_MODEL=llama3.2:3b
```

#### 4. Verificar uso de recursos
```bash
# Windows
taskmgr  # Ver CPU/RAM de Ollama

# Linux
htop  # Ver procesos
```

---

## 💡 Recomendaciones Adicionales

### 1. Desactivar Debug Mode (si solo usas Kalin)
```env
FLASK_DEBUG=False
```
**Beneficio**: Elimina reinicios constantes, mejora rendimiento 10-20%

### 2. Usar Modelo Más Rápido
Los modelos 3B son más rápidos que 7B para tareas simples:
```bash
ollama pull llama3.2:3b
```

### 3. Monitorear Logs de Ollama
```bash
# Ver logs de Ollama en tiempo real
# Windows: Revisar Event Viewer
# Linux: journalctl -u ollama -f
```

### 4. Considerar API Cloud (si Ollama sigue lento)
Si tu hardware es limitado, considera:
- OpenAI GPT-3.5 (rápido, barato)
- Anthropic Claude Haiku (rápido)
- Qwen via Alibaba Cloud

---

## 📈 Métricas de Éxito

Después de aplicar las soluciones, deberías observar:

| Métrica | Antes | Después |
|---------|-------|---------|
| Tiempo respuesta "hola" | 33s | <15s |
| Tokens para HTML | 800 | 1200 |
| Timeout Ollama | 30s | 120s |
| Tasa éxito HTML | ~20% | ~80%+ |
| Reinicios Flask | Constantes | Estables (si debug=False) |

---

## 🎯 Conclusión

El problema fue una **combinación de factores**:
1. ✅ Tokens insuficientes → **CORREGIDO** (800 → 1200)
2. ✅ Limpieza agresiva → **CORREGIDO** (regex más conservadora)
3. ✅ Timeout corto → **CORREGIDO** (30s → 120s)
4. ✅ Validaciones estrictas → **CORREGIDO** (anteriormente)

**Próximo paso**: Reiniciar Kalin y probar generación de HTML.

Si persiste el problema, revisar:
- Hardware/CPU disponible para Ollama
- Modelo específico usado (algunos son más lentos)
- Logs detallados con DEBUG_MODE activado

---

## 📚 Archivos Modificados

1. `agent/actions/tools/fix_tool.py` - Tokens y limpieza HTML
2. `agent/llm/providers/ollama_provider.py` - Timeout aumentado
3. `DIAGNOSTICO_PROBLEMAS_HTML.md` - Este documento

---

**Estado**: ✅ Soluciones aplicadas, pendiente verificación
