# 🚀 Guía de Onboarding para Colaboradores

**Bienvenido al proyecto Kalin!** Esta guía te ayudará a comenzar a contribuir efectivamente.

---

## 📋 Tabla de Contenidos

1. [Primeros Pasos](#primeros-pasos)
2. [Configuración del Entorno](#configuración-del-entorno)
3. [Entendiendo la Arquitectura](#entendiendo-la-arquitectura)
4. [Tu Primera Contribución](#tu-primera-contribución)
5. [Flujo de Trabajo Git](#flujo-de-trabajo-git)
6. [Estándares de Código](#estándares-de-código)
7. [Testing](#testing)
8. [Comunicación](#comunicación)
9. [Recursos de Aprendizaje](#recursos-de-aprendizaje)

---

## Primeros Pasos

### 1. Lee la Documentación Esencial

**Tiempo estimado**: 2-3 horas

```
✅ README.md - Overview del proyecto, instalación básica
✅ ARQUITECTURA_PROYECTO.md - Arquitectura técnica detallada
✅ CONTRIBUTING.md - Guía de contribución, estándares
✅ INFORME_ESTADO_PROYECTO.md - Estado actual, roadmap
✅ CHANGELOG.md - Historial de cambios recientes
```

### 2. Configura Tu Entorno de Desarrollo

**Tiempo estimado**: 30-60 minutos

Ver sección [Configuración del Entorno](#configuración-del-entorno)

### 3. Explora el Código

**Tiempo estimado**: 2-4 horas

```bash
# Clona el repositorio
git clone https://github.com/carlosbv99/kalin.git
cd kalin

# Abre en tu IDE favorito
code .  # VS Code
# o
pycharm .  # PyCharm
```

**Archivos clave para estudiar** (en orden):
1. `web.py` - Entry point, API endpoints
2. `agent/core/orchestration_layer.py` - Corazón del sistema
3. `agent/llm/provider_manager.py` - Gestión multi-LLM
4. `agent/core/tool_manager.py` - Sistema de tools
5. `static/js/app.js` - Coordinador frontend

### 4. Ejecuta el Proyecto

**Tiempo estimado**: 15 minutos

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env si tienes API keys

# Iniciar servidor
python web.py

# Abrir navegador
# http://127.0.0.1:5000
```

---

## Configuración del Entorno

### Requisitos Previos

- **Python**: 3.10+ ([descargar](https://www.python.org/downloads/))
- **Git**: 2.30+ ([descargar](https://git-scm.com/))
- **IDE**: VS Code recomendado ([descargar](https://code.visualstudio.com/))
- **Ollama** (opcional, para modelos locales): [descargar](https://ollama.com/)

### Paso a Paso

#### 1. Clonar Repositorio

```bash
git clone https://github.com/carlosbv99/kalin.git
cd kalin
```

#### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales**:
- Flask 3.0+ (servidor web)
- python-dotenv (variables de entorno)
- requests (HTTP client)
- watchdog (file monitoring)

#### 4. Configurar Variables de Entorno

```bash
cp .env.example .env
```

Editar `.env`:

```env
# Modelo activo por defecto
OLLAMA_MODEL=llama3.2:1b

# API Keys (solo si usas proveedores cloud)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIza...
MISTRAL_API_KEY=...
MIMO_API_KEY=...

# Configuración general
DEBUG=False
LOG_LEVEL=INFO
```

**Nota**: Solo configura las API keys de los proveedores que planeas usar.

#### 5. (Opcional) Instalar Ollama

Para usar modelos locales gratis:

```bash
# Windows (PowerShell)
winget install Ollama.Ollama

# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Descargar modelo ligero para testing
ollama pull llama3.2:1b

# Verificar instalación
ollama list
```

#### 6. Ejecutar Servidor

```bash
python web.py
```

Deberías ver:
```
 * Running on http://127.0.0.1:5000
```

Abrir navegador en `http://127.0.0.1:5000`

#### 7. Verificar Funcionamiento

1. Escribe "Hola" en el chat
2. Deberías recibir respuesta del LLM
3. Prueba generar código: "Crea un botón rojo en HTML"
4. Verifica que aparece en editor y preview

---

## Entendiendo la Arquitectura

### Visión General de Alto Nivel

```
Usuario → Frontend (JS) → Backend (Flask) → Agents → Tools → LLM Providers
```

### Componentes Clave

#### 1. Frontend (`static/js/`)

**Responsabilidad**: UI/UX, comunicación con backend

**Módulos principales**:
- `app.js` - Coordinador, inicialización
- `chat.js` - Mensajes, streaming
- `code-editor.js` - Editor de código
- `preview.js` - Renderizado sandboxed
- `ui-manager.js` - UI components (modales, menús)
- `menu-functions.js` - Menú configuración

**Patrón**: Vanilla JS modular, sin frameworks

#### 2. Backend (`web.py`)

**Responsabilidad**: API REST, routing, middleware

**Endpoints principales**:
- `POST /chat` - Procesar mensaje usuario
- `POST /set-model` - Cambiar modelo activo
- `GET /system/list-models` - Lista modelos disponibles
- `POST /system/download-model` - Descargar modelo Ollama
- `POST /api/ollama/models` - Modelos instalados

**Framework**: Flask 3.0+

#### 3. Orchestration Layer (`agent/core/orchestration_layer.py`)

**Responsabilidad**: Routing inteligente, selección de agent

**Flujo**:
```
Request → Detectar intención → Seleccionar Agent → Ejecutar Tools → Retornar respuesta
```

**Intenciones soportadas**:
- `create` - Generar código nuevo
- `fix` - Corregir errores
- `analyze` - Analizar código
- `chat` - Conversación general

#### 4. Agents (`agent/core/`)

**Responsabilidad**: Lógica especializada por dominio

**Agents disponibles**:
- `FrontendAgent` - HTML/CSS/JS generation
- `BackendAgent` - Server-side logic, APIs
- `QAAgent` - Testing, code quality

**Patrón**: Strategy pattern, intercambiables

#### 5. Tool Manager (`agent/core/tool_manager.py`)

**Responsabilidad**: Ejecución segura de operaciones

**Tools disponibles**:
- `read_file` - Leer archivo
- `write_file` - Escribir archivo
- `analyze_code` - Análisis estático
- `generate_with_llm` - Generación via LLM
- `apply_patch` - Aplicar parche
- `search_files` - Búsqueda de archivos

**Seguridad**: Sandbox execution, validación de parámetros

#### 6. LLM Providers (`agent/llm/`)

**Responsabilidad**: Abstracción de proveedores LLM

**Proveedores**:
- `OllamaProvider` - Modelos locales
- `OpenAIProvider` - GPT-3.5/4
- `AnthropicProvider` - Claude 3
- `GroqProvider` - Llama/Mixtral rápido
- `GeminiProvider` - Google Gemini
- `MistralProvider` - Mistral AI
- `MimoProvider` - Xiaomi MiMo

**Patrón**: Provider pattern, interfaz común `BaseLLMProvider`

### Diagrama de Flujo de Request

```
1. Usuario escribe: "Crea un botón"
         ↓
2. Frontend: POST /chat {message: "Crea un botón"}
         ↓
3. web.py: orchestration_layer.process_request()
         ↓
4. Orchestrator: detect_intention() → 'create'
         ↓
5. Orchestrator: select_agent('create', 'html') → FrontendAgent
         ↓
6. FrontendAgent: build_prompt(user_message, context)
         ↓
7. FrontendAgent: tool_manager.run('generate_with_llm', prompt)
         ↓
8. ToolManager: execute_in_sandbox(generate_with_llm)
         ↓
9. generate_with_llm: provider_manager.generate(prompt)
         ↓
10. ProviderManager: get_active_provider() → OllamaProvider
         ↓
11. OllamaProvider: POST http://localhost:11434/api/generate
         ↓
12. Ollama: Procesa prompt → retorna texto
         ↓
13. OllamaProvider: retorna LLMResponse(text="<button...>")
         ↓
14. ToolManager: valida resultado → retorna texto
         ↓
15. FrontendAgent: procesa respuesta
         ↓
16. Orchestrator: aplica patch si hay código existente
         ↓
17. web.py: retorna JSON {respuesta: "<button...>", tipo: "html"}
         ↓
18. Frontend: muestra en editor + preview
```

---

## Tu Primera Contribución

### Opción 1: Bug Fix (Recomendado para empezar)

**Tiempo**: 2-4 horas

1. **Encuentra un issue**: [github.com/carlosbv99/kalin/issues](https://github.com/carlosbv99/kalin/issues)
   - Busca etiquetas: `good first issue`, `bug`, `help wanted`

2. **Comenta en el issue**: "Me gustaría trabajar en esto"

3. **Crea branch**:
   ```bash
   git checkout -b fix/descripcion-corta
   ```

4. **Implementa fix**:
   - Sigue estándares de código
   - Agrega tests si aplica
   - Commit messages claros

5. **Testea localmente**:
   ```bash
   pytest tests/ -v
   python web.py  # Test manual
   ```

6. **Push y PR**:
   ```bash
   git add .
   git commit -m "fix: descripción clara del fix"
   git push origin fix/descripcion-corta
   ```
   
   Crea Pull Request en GitHub

### Opción 2: Agregar Test

**Tiempo**: 1-2 horas

1. **Elige módulo sin tests suficientes**:
   ```bash
   pytest --cov=agent tests/
   # Revisa cobertura por archivo
   ```

2. **Crea test file**: `tests/test_nombre_modulo.py`

3. **Escribe tests**:
   ```python
   import pytest
   from agent.core.nombre_modulo import NombreClase
   
   def test_funcionalidad_especifica():
       # Arrange
       obj = NombreClase()
       
       # Act
       result = obj.metodo()
       
       # Assert
       assert result == esperado
   ```

4. **Ejecuta tests**:
   ```bash
   pytest tests/test_nombre_modulo.py -v
   ```

5. **Commit y PR**

### Opción 3: Mejorar Documentación

**Tiempo**: 1-3 horas

1. **Identifica área a mejorar**:
   - Docs desactualizadas
   - Falta ejemplos
   - Typos, gramática
   - Traducciones

2. **Edita archivo `.md`**

3. **Preview local** (si es README):
   ```bash
   # Usa preview de Markdown en VS Code
   # O GitHub renderiza automáticamente
   ```

4. **Commit y PR**:
   ```bash
   git commit -m "docs: mejora en sección X"
   ```

### Opción 4: Agregar Feature Pequeña

**Tiempo**: 4-8 horas

1. **Discute feature primero**: Crea issue o discussion

2. **Diseña solución**: Describe approach en issue

3. **Implementa**:
   - Sigue arquitectura existente
   - Agrega tests
   - Actualiza docs

4. **Testea exhaustivamente**

5. **PR con descripción detallada**

---

## Flujo de Trabajo Git

### Branch Naming

```
feature/nombre-feature      # Nueva funcionalidad
fix/descripcion-bug         # Corrección de bug
docs/descripcion-cambio     # Cambios documentación
refactor/descripcion        # Refactorización código
test/descripcion            # Agregar/modificar tests
```

### Commit Messages

**Formato**: `tipo(alcance): descripción corta`

```bash
# Ejemplos buenos
git commit -m "feat(llm): agregar soporte para Cohere"
git commit -m "fix(preview): corregir CSP para inline scripts"
git commit -m "docs(readme): actualizar sección instalación"
git commit -m "refactor(orchestrator): simplificar selección agent"
git commit -m "test(tool_manager): agregar tests write_file"

# Tipos: feat, fix, docs, style, refactor, test, chore
```

**Descripción larga** (opcional):
```bash
git commit -m "feat(llm): agregar soporte para Cohere

- Implementar CohereProvider heredando BaseLLMProvider
- Agregar configuración en .env.example
- Registrar en ProviderManager
- Agregar tests unitarios básicos

Closes #123"
```

### Pull Request Process

1. **Antes de crear PR**:
   - [ ] Tests pasan localmente
   - [ ] Código sigue estándares
   - [ ] Docs actualizadas si aplica
   - [ ] Rebase con main reciente

2. **Crear PR**:
   - Título claro y descriptivo
   - Descripción detallada del cambio
   - Referenciar issues relacionados (`Closes #123`)
   - Screenshots si es cambio UI

3. **Code Review**:
   - Responde comentarios promptly
   - Haz cambios solicitados
   - Mantén conversación profesional

4. **Merge**:
   - Maintainer aprueba y mergea
   - Borra branch después de merge

---

## Estándares de Código

### Python

#### Style Guide

- **PEP 8** compliant
- **Line length**: 88 chars (Black default)
- **Indentation**: 4 spaces
- **Imports**: Ordenados (stdlib, third-party, local)

#### Type Hints

**Obligatorios** en funciones públicas:

```python
def generar_codigo(prompt: str, temperature: float = 0.7) -> str:
    """Genera código basado en prompt."""
    pass
```

#### Docstrings

**Google style** obligatorio:

```python
def calcular_costo(tokens: int, modelo: str) -> float:
    """
    Calcula costo estimado de generación.
    
    Args:
        tokens: Número de tokens generados
        modelo: Nombre del modelo (ej: 'gpt-4')
    
    Returns:
        Costo estimado en USD
    
    Raises:
        ValueError: Si modelo no tiene pricing configurado
    """
    pass
```

#### Error Handling

**Específico**, no bare except:

```python
# ✅ Bueno
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    logger.error(f"HTTP error: {e}")
    raise LLMProviderError(f"API error: {e}")
except requests.exceptions.Timeout:
    logger.warning("Request timeout")
    raise LLMTimeoutError("Request timed out")

# ❌ Malo
try:
    response = requests.post(url, json=data)
except:
    pass
```

#### Logging

Usar logger, **no print**:

```python
from agent.core.logger import get_logger
logger = get_logger('kalin.mi_modulo')

logger.debug("Detalle técnico")
logger.info("Información general")
logger.warning("Advertencia recuperable")
logger.error("Error que requiere atención")
```

### JavaScript

#### Style Guide

- **ES6+** features
- **const/let**, nunca var
- **Async/await**, no .then() chaining excesivo
- **Semicolons**: Opcionales (consistente)

#### JSDoc

```javascript
/**
 * Envía mensaje al backend
 * @param {string} message - Mensaje del usuario
 * @param {string} sessionId - ID de sesión
 * @returns {Promise<Object>} Respuesta del servidor
 */
async function sendMessage(message, sessionId) {
    // Implementation
}
```

#### Error Handling

```javascript
// ✅ Bueno
try {
    const response = await fetch('/chat', {
        method: 'POST',
        body: JSON.stringify({message})
    });
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
} catch (error) {
    console.error('Error sending message:', error);
    showError('No se pudo enviar el mensaje');
}

// ❌ Malo
fetch('/chat').then(r => r.json()).catch(e => {});
```

---

## Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/test_llm_providers.py -v

# Con cobertura
pytest --cov=agent tests/

# Coverage report HTML
pytest --cov=agent --cov-report=html tests/
# Abrir htmlcov/index.html
```

### Escribir Tests

#### Unit Test Example

```python
import pytest
from agent.llm.providers.ollama_provider import OllamaProvider

class TestOllamaProvider:
    
    def setup_method(self):
        """Setup antes de cada test."""
        self.config = {
            'model': 'llama3.2:1b',
            'base_url': 'http://localhost:11434'
        }
        self.provider = OllamaProvider(self.config)
    
    def test_generate_returns_response(self):
        """Test que generate retorna respuesta válida."""
        response = self.provider.generate("Di hola")
        
        assert response is not None
        assert response.text is not None
        assert len(response.text) > 0
        assert response.provider == 'ollama'
    
    def test_generate_with_invalid_model(self):
        """Test que genera error con modelo inválido."""
        self.config['model'] = 'modelo-inexistente'
        provider = OllamaProvider(self.config)
        
        with pytest.raises(LLMProviderError):
            provider.generate("test")
```

#### Mocking External Services

```python
from unittest.mock import patch, MagicMock

def test_openai_provider_with_mock():
    """Test OpenAI provider sin llamar API real."""
    with patch('requests.post') as mock_post:
        # Configurar mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Hola'}}]
        }
        mock_post.return_value = mock_response
        
        # Ejecutar test
        provider = OpenAIProvider({'api_key': 'test-key'})
        result = provider.generate("Saluda")
        
        # Verificar
        assert result.text == 'Hola'
        mock_post.assert_called_once()
```

### Coverage Goals

- **Mínimo aceptable**: 60%
- **Objetivo Q2 2026**: 75%
- **Objetivo largo plazo**: 85%+

**Prioridad de tests**:
1. Crítico: LLM providers, Tool Manager, Orchestrator
2. Alto: Patch System, Memory Manager, Event Bus
3. Medio: Session Manager, Logger, Config
4. Bajo: Utils helpers, CLI tools

---

## Comunicación

### Canales

1. **GitHub Issues**: Bugs, feature requests
   - [github.com/carlosbv99/kalin/issues](https://github.com/carlosbv99/kalin/issues)

2. **GitHub Discussions**: Preguntas generales, ideas
   - [github.com/carlosbv99/kalin/discussions](https://github.com/carlosbv99/kalin/discussions)

3. **Pull Requests**: Code review, discusiones técnicas

### Etiquetado de Issues

- `bug`: Algo no funciona correctamente
- `enhancement`: Nueva feature o mejora
- `documentation`: Mejoras en docs
- `good first issue`: Para newcomers
- `help wanted`: Se necesita ayuda
- `question`: Pregunta, no bug

### Code Review Guidelines

#### Para Authors

- **Responde promptly** (< 24 horas ideal)
- **Agradece feedback**, incluso crítico
- **Explica decisiones** si discrepas
- **Haz cambios solicitados** o justifica por qué no

#### Para Reviewers

- **Sé constructivo**, no destructivo
- **Explica el porqué**, no solo el qué
- **Sugiere alternativas**, no solo critiques
- **Aprueba cuando esté listo**, no perfectionismo

---

## Recursos de Aprendizaje

### Documentación del Proyecto

- [ARQUITECTURA_PROYECTO.md](ARQUITECTURA_PROYECTO.md) - Arquitectura técnica
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guía contribución
- [INFORME_ESTADO_PROYECTO.md](INFORME_ESTADO_PROYECTO.md) - Estado actual

### Tecnologías Clave

#### Python/Flask
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Real Python - Flask Tutorial](https://realpython.com/tutorials/flask/)

#### JavaScript
- [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [JavaScript.info](https://javascript.info/)

#### LLMs
- [Ollama Documentation](https://ollama.com/docs)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [LangChain Concepts](https://docs.langchain.com/docs/) (patrones similares)

### Patrones de Diseño

- [Refactoring Guru - Design Patterns](https://refactoring.guru/design-patterns)
- Singleton (ProviderManager)
- Strategy (Agents)
- Observer (Event Bus)
- Factory (Tool creation)

### Testing

- [pytest Documentation](https://docs.pytest.org/)
- [Real Python - Testing](https://realpython.com/python-testing/)

---

## Checklist de Onboarding

Marca conforme completas:

- [ ] Leí README.md completo
- [ ] Leí ARQUITECTURA_PROYECTO.md
- [ ] Leí CONTRIBUTING.md
- [ ] Cloné repositorio localmente
- [ ] Configuré entorno de desarrollo
- [ ] Ejecuté proyecto exitosamente
- [ ] Exploré estructura de código
- [ ] Entiendo flujo request/response
- [ ] Identifiqué área de interés para contribuir
- [ ] Me presenté en Discussions o Issue
- [ ] Hice primera contribución (bug fix, test, docs)

---

## ¿Necesitas Ayuda?

1. **Busca en docs primero**: Probablemente ya está respondido
2. **Busca en issues cerrados**: Alguien pudo tener misma pregunta
3. **Crea Discussion**: Para preguntas generales
4. **Crea Issue**: Para bugs o feature requests específicos

**No tengas miedo de preguntar!** Mejor preguntar que asumir incorrectamente.

---

**¡Bienvenido a bordo! 🎉**

Estamos emocionados de tenerte como colaborador. Tu contribución, por pequeña que sea, hace diferencia.
