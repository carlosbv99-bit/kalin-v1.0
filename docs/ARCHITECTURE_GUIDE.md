# 🏗️ Guía de Arquitectura - Kalin AI

**Versión**: 3.0 | **Fecha**: Mayo 2026 | **Nivel**: Intermedio-Avanzado

---

## 📋 Resumen Ejecutivo

Kalin AI es un IDE inteligente multi-LLM con arquitectura modular basada en agents especializados, sistema de tools seguro, y preview sandboxed. Soporta 7+ proveedores LLM con switching dinámico sin restart.

### Stack Tecnológico
- **Backend**: Python 3.10+ / Flask 3.0+
- **Frontend**: Vanilla JS ES6+ (sin frameworks)
- **LLM Runtime**: Ollama (local), Cloud APIs (OpenAI, Groq, Gemini, etc.)
- **Sandbox**: WebContainers + iframe CSP

---

## 🎯 Principios Arquitectónicos

1. **Modularidad Extrema**: Cada componente es intercambiable
2. **Provider Agnostic**: Código no depende de proveedor específico
3. **Security First**: Sandbox execution, CSP estricta, validación de inputs
4. **Incremental Changes**: Patch system evita regeneración completa
5. **Context Persistence**: Memoria conversacional con compresión automática
6. **Zero Downtime Switching**: Cambio de modelo sin restart servidor

---

## 🏛️ Capas Arquitectónicas

```
┌─────────────────────────────────────────┐
│         PRESENTATION LAYER              │  ← Frontend (JS modules)
├─────────────────────────────────────────┤
│         ORCHESTRATION LAYER             │  ← Intent detection, routing
├─────────────────────────────────────────┤
│         AGENT LAYER                     │  ← Specialized agents
├─────────────────────────────────────────┤
│         TOOL LAYER                      │  ← Secure tool execution
├─────────────────────────────────────────┤
│         PROVIDER LAYER                  │  ← LLM abstraction
├─────────────────────────────────────────┤
│         INFRASTRUCTURE LAYER            │  ← Memory, patches, sessions
└─────────────────────────────────────────┘
```

---

## 🔑 Componentes Clave

### 1. Orchestration Layer (`agent/core/orchestration_layer.py`)

**Responsabilidad**: Routing inteligente basado en intención y contexto.

```python
# Flujo simplificado
def process_request(message, context):
    intention = detect_intention(message)      # create/fix/analyze/chat
    language = detect_language(message)         # html/python/js/etc
    agent = select_agent(intention, language)   # Frontend/Backend/QA
    prompt = agent.build_prompt(message, context)
    result = tool_manager.run('generate_with_llm', prompt)
    return apply_patch_if_needed(result, context)
```

**Patrones**: Strategy (agent selection), Template Method (prompt building)

---

### 2. Agent System (`agent/core/*_agent.py`)

**Agents Disponibles**:
- `FrontendAgent`: HTML/CSS/JS generation (temperature: 0.8)
- `BackendAgent`: Server logic, APIs (temperature: 0.7)
- `QAAgent`: Testing, code review (temperature: 0.5)

**Clase Base**:
```python
class Agent:
    def build_prompt(self, message, context): ...
    def process(self, task, context): ...
```

**Patrón**: Strategy pattern, intercambiables según dominio

---

### 3. Tool Manager (`agent/core/tool_manager.py`)

**Tools Registradas**:
- `read_file`, `write_file` - File operations
- `analyze_code` - Static analysis
- `generate_with_llm` - LLM generation
- `apply_patch` - Incremental updates
- `search_files` - File search

**Seguridad**:
```python
def run(tool_name, **kwargs):
    validate_params(tool_name, kwargs)     # Type checking
    check_security_level(tool_name)        # Permission validation
    return sandbox.execute(tool_func, **kwargs)  # Timeout, isolation
```

**Patrón**: Command pattern, registry

---

### 4. Provider Manager (`agent/llm/provider_manager.py`)

**Características**:
- Singleton pattern (una instancia global)
- Dynamic loading from `.env`
- Zero-downtime switching
- Ollama lee modelo dinámicamente

```python
# Cambio de modelo
POST /set-model {model: 'deepseek-coder:latest'}
→ Actualiza .env
→ ProviderManager.reset_instance()
→ Próximo request usa nuevo modelo
```

**Proveedores**: Ollama, OpenAI, Groq, Gemini, Mistral, MiMo, Anthropic

**Patrón**: Adapter (unifica interfaces LLM), Singleton

---

### 5. Patch System (`agent/core/patch_system.py`)

**Propósito**: Aplicar cambios incrementales sin regenerar código completo.

```python
# Aplicar parche
snapshot_id = create_snapshot(existing_code)
insertion_point = find_location(existing_code, '</body>')
combined = insert_fragment(existing_code, new_fragment, insertion_point)
record_patch(snapshot_id, fragment, timestamp)

# Rollback
restored = undo_last_patch()  # Restaura desde snapshot
```

**Ventaja**: 10x más rápido que regeneración completa

---

### 6. Memory Manager (`agent/core/memory_manager.py`)

**Funcionalidades**:
- Persistencia JSON por sesión
- Auto-compresión (>50 mensajes)
- Context window retrieval

```python
# Compresión estrategia
if len(messages) > 60:
    keep first 5      # Contexto inicial
    keep last 20      # Recientes
    summarize middle  # Placeholder para LLM summarization
```

---

## 🔄 Flujos Críticos

### Flujo Generación Código

```
User → Chat UI → POST /chat → Orchestrator
  → Detect intention (create) → Select FrontendAgent
  → Build prompt → Tool Manager → generate_with_llm
  → Provider.generate() → LLM Response
  → Apply patch? → Return to frontend
  → Code Editor + Preview
```

**Tiempo**: 2-5s (Ollama local), 1-2s (cloud)

---

### Flujo Cambio Modelo

```
User → Settings → Select model → POST /set-model
  → Update .env file → Reset ProviderManager singleton
  → Next request → ProviderManager recreates
  → Reads new model from .env → Uses new model
```

**Clave**: No requiere restart servidor

---

### Flujo Descarga Modelo

```
User → Click download icon → Show spinner in chat header
  → POST /system/check-model → ollama list
  → Confirm modal → POST /system/download-model
  → ollama pull (timeout: 10min) → Refresh model list
  → Hide spinner → Success modal
```

**UI Feedback**: Indicador de progreso visible durante descarga

---

## 🔌 Puntos de Extensión

### Agregar Provider

1. Crear class heredando `BaseLLMProvider`
2. Implementar `generate()` y `get_available_models()`
3. Registrar en `ProviderManager._load_providers()`
4. Agregar config a `.env.example`

**Tiempo estimado**: 2-4 horas

---

### Agregar Tool

1. Implementar wrapper function en `ToolManager`
2. Registrar con `registry.register()`
3. Definir schema de parámetros
4. Usar en agents via `tool_manager.run()`

**Tiempo estimado**: 1-2 horas

---

### Agregar Agent

1. Crear class heredando `Agent`
2. Implementar `build_prompt()` específico del dominio
3. Integrar en `OrchestrationLayer._select_agent()`
4. Agregar templates de prompts

**Tiempo estimado**: 3-5 horas

---

## 🛡️ Seguridad

### Content Security Policy

```javascript
iframe.setAttribute('sandbox', 'allow-scripts');
iframe.setAttribute('csp', "default-src 'none'; script-src 'unsafe-inline';");
```

**Restricciones**:
- ❌ No DOM padre access
- ❌ No external requests
- ✅ Inline scripts/styles allowed

---

### Tool Validation

```python
# Path traversal prevention
abs_path = os.path.abspath(user_path)
if not abs_path.startswith(allowed_dir):
    raise SecurityError("Access denied")

# Parameter validation
validate_type(param, expected_type)
validate_required_params(params, schema)
```

---

### Input Sanitization

```python
# Remove dangerous HTML
for tag in soup.find_all(['script', 'iframe', 'object']):
    tag.decompose()

# Remove event handlers
for attr in tag.attrs:
    if attr.startswith('on'):  # onclick, onload
        del tag[attr]
```

---

## 📊 Performance

### Métricas Actuales

| Métrica | Valor | Objetivo |
|---------|-------|----------|
| Latencia generación | 3s (local) | <2s |
| Throughput | 8 req/min | 10 req/min |
| Memory usage | 380MB | <512MB |
| Preview render | 200ms | <500ms |

---

### Optimizaciones

1. **Lazy Loading**: Providers solo si API key configurada
2. **Connection Pooling**: Reutiliza HTTP connections
3. **Prompt Caching**: LRU cache para prompts frecuentes
4. **Response Streaming**: Pendiente (reducir TTFB)

---

## 🧪 Testing

### Estructura

```
tests/
├── unit/          # Components individuales
├── integration/   # Flujos completos
└── e2e/          # Browser automation
```

### Coverage

- **Actual**: 70%
- **Objetivo Q2**: 80%
- **Objetivo Q4**: 88%

### Ejemplo Test

```python
@patch('requests.post')
def test_generate(mock_post, provider):
    mock_post.return_value.json.return_value = {
        'response': 'Hola',
        'eval_count': 50
    }
    
    result = provider.generate("Di hola")
    
    assert result.text == 'Hola'
    assert result.tokens_used == 50
```

---

## 🚀 Deployment

### Docker

```bash
docker-compose up -d
# Services: kalin (Flask) + ollama (LLM runtime)
```

### CI/CD

```yaml
# GitHub Actions
on: [push, pull_request]
jobs:
  test: pytest --cov=agent
  lint: flake8 + black
```

---

## 🐛 Troubleshooting

### Ollama Connection Error

```bash
ollama list  # Verificar servicio
netstat -an | grep 11434  # Verificar puerto
Restart-Service Ollama  # Reiniciar
```

---

### Provider Switch Not Working

```python
ProviderManager.reset_instance()  # Forzar recreación
```

---

### Preview Not Rendering

```javascript
// Check DevTools Console for CSP errors
console.log(iframe.getAttribute('sandbox'));
```

---

## 📚 Recursos

- **Documentación Completa**: `docs/TECHNICAL_REFERENCE.md`
- **API Reference**: Ver sección en TECHNICAL_REFERENCE
- **Contributing Guide**: `CONTRIBUTING.md`
- **Onboarding**: `ONBOARDING_COLABORADORES.md`

---

**Última actualización**: Mayo 2026  
**Mantenido por**: CarlosBV99 y colaboradores
