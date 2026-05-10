# 🚀 Guía Completa: Configuración de Proveedores LLM en Kalin

## Proveedores Soportados

Kalin ahora soporta múltiples proveedores de modelos LLM, tanto locales como en la nube.

---

## 📍 Proveedores Locales (Gratis)

### 1. **Ollama** ✅ (Recomendado para desarrollo)
- **Estado:** Ya configurado
- **Modelos:** qwen2.5-coder, deepseek-coder, llama3, mistral, etc.
- **Costo:** Gratis (local)
- **Configuración:** Ya está en `.env`

```env
OLLAMA_ENDPOINT=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5-coder:7b
```

---

## ☁️ Proveedores en la Nube (Gratuitos/Económicos)

### 2. **Groq** ⚡ (Ultra-rápido, GRATIS)
- **Velocidad:** ¡El más rápido!
- **Modelos:** Llama 3.3 70B, Mixtral 8x7B, Gemma 9B
- **Límite gratuito:** Muy generoso
- **Obtener API Key:** https://console.groq.com/keys

**Configuración en `.env`:**
```env
GROQ_API_KEY=tu_api_key_aqui
GROQ_MODEL=llama-3.1-8b-instant
```

**Modelos disponibles:**
- `llama-3.3-70b-versatile` (más potente)
- `llama-3.1-8b-instant` (más rápido)
- `mixtral-8x7b-32768`
- `gemma2-9b-it`

---

### 3. **Google Gemini** 🌟 (Gratis con límites)
- **Modelos:** Gemini 1.5 Pro, Gemini 1.5 Flash
- **Límite gratuito:** 60 requests/min, 1500 requests/día
- **Obtener API Key:** https://makersuite.google.com/app/apikey

**Configuración en `.env`:**
```env
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-1.5-flash
```

**Modelos disponibles:**
- `gemini-1.5-pro` (más potente)
- `gemini-1.5-flash` (más rápido)
- `gemini-1.0-pro`

---

### 4. **Mistral AI** 🎯 (Económico)
- **Modelos:** Mistral Large, Mixtral, Codestral
- **Costo:** Muy barato (~$0.002/1K tokens)
- **Crédito inicial:** ~$2-5 gratis
- **Obtener API Key:** https://console.mistral.ai/

**Configuración en `.env`:**
```env
MISTRAL_API_KEY=tu_api_key_aqui
MISTRAL_MODEL=mistral-small-latest
```

**Modelos disponibles:**
- `mistral-large-latest` (más potente)
- `mistral-small-latest` (equilibrado)
- `codestral-latest` (especializado en código)
- `open-mixtral-8x7b`

---

### 5. **OpenAI** 💎 (Premium)
- **Modelos:** GPT-4 Turbo, GPT-3.5 Turbo
- **Costo:** $0.03/1K tokens
- **Obtener API Key:** https://platform.openai.com/api-keys

**Configuración en `.env`:**
```env
OPENAI_API_KEY=tu_api_key_aqui
OPENAI_MODEL=gpt-4-turbo
```

---

### 6. **Anthropic Claude** 🧠 (Premium)
- **Modelos:** Claude 3.5 Sonnet, Claude 3 Opus
- **Costo:** $0.015/1K tokens
- **Obtener API Key:** https://console.anthropic.com/

**Configuración en `.env`:**
```env
ANTHROPIC_API_KEY=tu_api_key_aqui
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

---

## 🔧 Cómo Cambiar de Proveedor

### Opción 1: Desde el Menú Lateral (Próximamente)
1. Menú lateral → "Configuración"
2. Seleccionar proveedor
3. Seleccionar modelo
4. Guardar

### Opción 2: Editando `.env` (Actual)
1. Abre el archivo `.env`
2. Modifica las variables del proveedor deseado
3. Reinicia Kalin (`python run.py`)

### Opción 3: Modo Automático (Hybrid)
Configura el modo en `.env`:
```env
KALIN_MODE=hybrid
```

Esto usará Ollama como principal y hará fallback a cloud si falla.

---

## 📊 Comparativa de Proveedores

| Proveedor | Velocidad | Calidad | Costo | Límite Gratis |
|-----------|-----------|---------|-------|---------------|
| **Groq** | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Gratis | Muy alto |
| **Gemini** | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Gratis | Medio |
| **Ollama** | ⚡⚡⚡ | ⭐⭐⭐⭐ | Gratis | Ilimitado |
| **Mistral** | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | $ | Bajo |
| **OpenAI** | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | $$ | Ninguno |
| **Claude** | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | $$ | Ninguno |

---

## 🎯 Recomendaciones

### Para Desarrollo Local (Gratis):
1. **Ollama** con `qwen2.5-coder:7b` ✅ (Ya lo tienes)
2. **Groq** con `llama-3.1-8b-instant` (si quieres velocidad)

### Para Producción (Calidad):
1. **Gemini 1.5 Pro** (mejor relación calidad/precio)
2. **Claude 3.5 Sonnet** (mejor para código complejo)
3. **GPT-4 Turbo** (más versátil)

### Para Testing Rápido:
1. **Groq** (respuesta en <1 segundo)
2. **Gemini 1.5 Flash** (muy rápido)

---

## 🚀 Pasos para Empezar

### 1. Obtener API Keys (5 minutos)
- Groq: https://console.groq.com/keys (gratis)
- Gemini: https://makersuite.google.com/app/apikey (gratis)
- Mistral: https://console.mistral.ai/ ($2-5 crédito)

### 2. Configurar `.env`
Agrega las API keys que obtuviste:
```env
# Groq (recomendado - gratis y rápido)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant

# Gemini (recomendado - gratis con buen límite)
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash
```

### 3. Reiniciar Kalin
```bash
python run.py
```

### 4. Seleccionar Modelo
Menú lateral → "Seleccionar Modelo Activo" → Elige tu modelo preferido

---

## ❓ Preguntas Frecuentes

### ¿Puedo usar múltiples proveedores a la vez?
Sí! Kalin soporta fallback automático. Si un proveedor falla, prueba el siguiente.

### ¿Cuál es el más barato?
Groq y Gemini son gratuitos actualmente. Mistral es muy económico.

### ¿Necesito internet para Ollama?
No, Ollama funciona 100% local. Los proveedores cloud sí necesitan internet.

### ¿Cómo sé qué proveedor estoy usando?
El indicador en la parte superior muestra el modelo activo. Ej: "🤖 qwen2.5-coder:7b"

### ¿Puedo cambiar de proveedor sin reiniciar?
Próximamente sí. Por ahora necesitas reiniciar Kalin después de cambiar `.env`.

---

## 📝 Notas Importantes

1. **NUNCA compartas tus API keys** públicamente
2. Las API keys están en `.env` (excluido de Git)
3. Kalin prioriza Ollama por defecto (local-first)
4. Puedes mezclar proveedores según el tipo de tarea

---

**Última actualización:** Mayo 2026  
**Versión:** Kalin v3.0+
