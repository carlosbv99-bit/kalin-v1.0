# 📘 Kalin AI - Documentación Técnica para Especialistas

**Versión**: 3.0  
**Fecha**: Mayo 2026  
**Audiencia**: Desarrolladores, arquitectos de software, contribuidores técnicos

---

## 📋 Tabla de Contenidos

1. [Visión General del Sistema](#visión-general-del-sistema)
2. [Arquitectura Técnica](#arquitectura-técnica)
3. [Componentes Core](#componentes-core)
4. [Flujos de Trabajo Críticos](#flujos-de-trabajo-críticos)
5. [API Reference](#api-reference)
6. [Sistema de Extensiones](#sistema-de-extensiones)
7. [Seguridad y Sandbox](#seguridad-y-sandbox)
8. [Performance y Optimización](#performance-y-optimización)
9. [Testing Strategy](#testing-strategy)
10. [Deployment y DevOps](#deployment-y-devops)
11. [Troubleshooting Avanzado](#troubleshooting-avanzado)

---

## Visión General del Sistema

Kalin AI es un **IDE inteligente basado en web** que integra múltiples proveedores LLM en una arquitectura modular con agents especializados, sistema de tools seguro, y preview sandboxed en tiempo real.

### Propuesta de Valor Técnica

- **Multi-LLM Abstraction**: 7+ proveedores con interfaz unificada (`BaseLLMProvider`)
- **Agent Specialization**: Frontend, Backend, QA agents con prompts dinámicos
- **Tool Security**: Sandbox execution con validación estricta de parámetros
- **Incremental Patching**: Sistema de parches con versionado y rollback
- **Contextual Memory**: Memoria conversacional persistente con compresión inteligente
- **Live Preview**: WebContainers + iframe sandboxed con CSP estricta

### Stack Tecnológico

| Capa | Tecnología | Versión | Propósito |
|------|-----------|---------|-----------|
| **Backend** | Python + Flask | 3.10+ / 3.0+ | Servidor API REST |
| **Frontend** | Vanilla JS | ES6+ | UI sin dependencias |
| **LLM Runtime** | Ollama | Latest | Modelos locales |
| **Sandbox** | WebContainers | 1.3+ | Ejecución Node.js browser |
| **Persistence** | JSON + LocalStorage | - | Sesiones y preferencias |

---

## Arquitectura Técnica

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE (Browser)                         │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Chat UI  │  │ Code     │  │ Preview  │  │ Settings │   │
│  │          │  │ Editor   │  │ Sandbox  │  │ Panel    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│         │              │              │             │       │
│         └──────────────┴──────────────┴─────────────┘       │
│                            │                                 │
│                   HTTP REST API                             │
└────────────────────────────┼────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                 SERVIDOR (Flask - web.py)                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Orchestration Layer                         │   │
│  │  • Intent detection (create/fix/analyze/chat)        │   │
│  │  • Agent selection (Frontend/Backend/QA)             │   │
│  │  • Tool orchestration                                │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────┼───────────────────────────────────┐   │
│  │        Agent System (agent/core/)                     │   │
│  │  • FrontendAgent: HTML/CSS/JS generation             │   │
│  │  • BackendAgent: Server logic, APIs                  │   │
│  │  • QAAgent: Testing, code quality                    │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────┼───────────────────────────────────┐   │
│  │        Tool Manager                                   │   │
│  │  • read_file  • write_file  • analyze_code           │   │
│  │  • generate_with_llm  • apply_patch  • search_files  │   │
│  │  • Sandbox execution con validación                  │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────┼───────────────────────────────────┐   │
│  │     LLM Provider Manager (Singleton)                  │   │
│  │  ┌────────┐ ┌────────┐ ┌──────┐ ┌──────┐            │   │
│  │  │Ollama  │ │OpenAI  │ │Groq  │ │Gemini│ ...        │   │
│  │  └────────┘ └────────┘ └──────┘ └──────┘            │   │
│  │  • Dynamic model loading from .env                   │   │
│  │  • Provider switching sin restart                    │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────┼───────────────────────────────────┐   │
│  │     Supporting Systems                                │   │
│  │  • Event Bus (pub/sub)                               │   │
│  │  • Memory Manager (context persistence)              │   │
│  │  • Patch System (versioning + rollback)              │   │
│  │  • Session Manager (multi-user)                      │   │
│  │  • Logger (structured, multi-level)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
         │ Ollama  │   │ Cloud   │   │ File    │
         │ Local   │   │ LLMs    │   │ System  │
         └─────────┘   └─────────┘   └─────────┘
```

### Patrones de Diseño Implementados

| Patrón | Ubicación | Propósito |
|--------|-----------|-----------|
| **Singleton** | `ProviderManager` | Única instancia de gestión LLM |
| **Strategy** | `Agents`, `LLMProviders` | Intercambio dinámico de estrategias |
| **Factory** | `ToolManager` | Creación de tools según contexto |
| **Observer** | `EventBus` | Pub/sub desacoplado |
| **Command** | `Tools` | Encapsulación de operaciones |
| **Template Method** | `BaseLLMProvider` | Estructura común providers |
| **Adapter** | `Provider implementations` | Unificación interfaces LLM |

---

## Componentes Core

### 1. Orchestration Layer

**Archivo**: `agent/core/orchestration_layer.py`

**Responsabilidad**: Routing inteligente de requests, selección de agent, coordinación de tools.

**Flujo de Procesamiento**:

```python
def process_request(user_message: str, context: dict) -> dict:
    """
    Procesa request de usuario completo.
    
    Args:
        user_message: Mensaje del usuario
        context: Contexto actual (código, historial, etc.)
    
    Returns:
        Dict con respuesta procesada
    """
    # 1. Detectar intención
    intention = self._detect_intention(user_message)
    
    # 2. Detectar lenguaje (si aplica)
    language = self._detect_language(user_message, context)
    
    # 3. Seleccionar agent especializado
    agent = self._select_agent(intention, language)
    
    # 4. Construir prompt dinámico
    prompt = agent.build_prompt(user_message, context)
    
    # 5. Ejecutar via Tool Manager
    result = tool_manager.run('generate_with_llm', prompt=prompt)
    
    # 6. Aplicar patch si hay código existente
    if context.get('existing_code'):
        result = patch_system.apply_incremental(result, context['existing_code'])
    
    # 7. Retornar respuesta estructurada
    return {
        'response': result.text,
        'type': language or 'text',
        'patch_applied': True
    }
```

**Detección de Intención**:

```python
INTENTION_PATTERNS = {
    'create': [
        r'\b(crea|genera|haz|construye|diseña)\b',
        r'\b(create|generate|make|build|design)\b'
    ],
    'fix': [
        r'\b(arregla|corrige|soluciona|repara)\b',
        r'\b(fix|correct|solve|repair)\b'
    ],
    'analyze': [
        r'\b(analiza|revisa|examina|evalúa)\b',
        r'\b(analyze|review|examine|evaluate)\b'
    ],
    'chat': ['default']  # Fallback
}
```

---

### 2. Agent System

**Archivos**: `agent/core/frontend_agent.py`, `backend_agent.py`, `qa_agent.py`

**Clase Base**:

```python
class Agent:
    """Clase base para todos los agents."""
    
    def __init__(self, name: str, specialization: str):
        self.name = name
        self.specialization = specialization
        self.temperature = 0.7
        self.max_tokens = 2048
    
    def build_prompt(self, user_message: str, context: dict) -> str:
        """Construye prompt dinámico basado en template."""
        template = self._load_template()
        return template.format(
            user_message=user_message,
            context=context,
            examples=self._get_examples()
        )
    
    def process(self, task: str, context: dict) -> LLMResponse:
        """Procesa tarea específica del dominio."""
        raise NotImplementedError
```

**FrontendAgent** (ejemplo):

```python
class FrontendAgent(Agent):
    """Especializado en generación HTML/CSS/JS."""
    
    def __init__(self):
        super().__init__('frontend_agent', 'web_development')
        self.supported_languages = ['html', 'css', 'javascript']
        self.temperature = 0.8  # Más creativo
    
    def build_prompt(self, user_message: str, context: dict) -> str:
        """Prompt específico para frontend."""
        return f"""
Eres un experto desarrollador frontend especializado en HTML5, CSS3 y JavaScript moderno.

REGLAS CRÍTICAS:
1. Genera SOLO código limpio, sin explicaciones ni texto adicional
2. Usa HTML5 semántico
3. CSS inline o en <style> tag
4. JavaScript vanilla, sin frameworks
5. Código responsive y accesible
6. SIN comentarios en el código generado

CONTEXTO ACTUAL:
{context.get('existing_code', 'Ninguno')}

SOLICITUD DEL USUARIO:
{user_message}

Genera el código HTML completo:
"""
```

---

### 3. Tool Manager

**Archivo**: `agent/core/tool_manager.py`

**Registro de Tools**:

```python
class ToolManager:
    """Gestor central de tools con sandbox."""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self.sandbox = ToolSandbox()
        self._register_system_tools()
    
    def _register_system_tools(self):
        """Registra tools del sistema."""
        
        self.registry.register(
            name="read_file",
            func=self._read_file_wrapper,
            description="Lee contenido de archivo",
            category="file_ops",
            params={
                'path': {'type': 'string', 'required': True},
                'max_lines': {'type': 'integer', 'default': 1000}
            }
        )
        
        self.registry.register(
            name="write_file",
            func=self._write_file_wrapper,
            description="Escribe contenido en archivo",
            category="file_ops",
            params={
                'path': {'type': 'string', 'required': True},
                'content': {'type': 'string', 'required': True},
                'mode': {'type': 'string', 'default': 'w'}
            },
            security_level='high'  # Requiere validación extra
        )
        
        self.registry.register(
            name="generate_with_llm",
            func=self._generate_wrapper,
            description="Genera contenido usando LLM activo",
            category="llm_ops",
            params={
                'prompt': {'type': 'string', 'required': True},
                'temperature': {'type': 'float', 'default': 0.7},
                'max_tokens': {'type': 'integer', 'default': 2048}
            }
        )
    
    def run(self, tool_name: str, **kwargs) -> Any:
        """
        Ejecuta tool en sandbox con validación.
        
        Args:
            tool_name: Nombre de la tool registrada
            **kwargs: Parámetros de la tool
        
        Returns:
            Resultado de la ejecución
        
        Raises:
            ToolNotFoundError: Si tool no existe
            ValidationError: Si parámetros inválidos
            SecurityError: Si violación de seguridad
        """
        # 1. Validar existencia
        tool = self.registry.get(tool_name)
        if not tool:
            raise ToolNotFoundError(f"Tool '{tool_name}' no encontrada")
        
        # 2. Validar parámetros
        self._validate_params(tool, kwargs)
        
        # 3. Verificar permisos de seguridad
        self._check_security_level(tool, kwargs)
        
        # 4. Ejecutar en sandbox
        try:
            result = self.sandbox.execute(tool.func, **kwargs)
            logger.info(f"Tool '{tool_name}' ejecutada exitosamente")
            return result
        except Exception as e:
            logger.error(f"Error ejecutando tool '{tool_name}': {e}")
            raise
```

**Sandbox Execution**:

```python
class ToolSandbox:
    """Ejecución segura de tools."""
    
    def execute(self, func: Callable, **kwargs) -> Any:
        """
        Ejecuta función en entorno controlado.
        
        - Timeout configurable
        - Resource limits
        - Exception isolation
        """
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Tool execution timeout")
        
        # Set timeout (30 segundos default)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)
        
        try:
            result = func(**kwargs)
            signal.alarm(0)  # Cancel timeout
            return result
        except TimeoutError:
            raise SecurityError("Tool execution exceeded time limit")
        finally:
            signal.alarm(0)  # Ensure cleanup
```

---

### 4. LLM Provider Manager

**Archivo**: `agent/llm/provider_manager.py`

**Patrón Singleton**:

```python
class ProviderManager:
    """
    Gestor singleton de proveedores LLM.
    
    - Carga dinámica desde .env
    - Switching sin restart
    - Modelo leído dinámicamente por OllamaProvider
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.providers = {}
        self.active_provider = None
        self._load_providers()
        self._set_active_provider()
        ProviderManager._initialized = True
    
    def _load_providers(self):
        """Carga todos los proveedores disponibles."""
        from dotenv import load_dotenv
        load_dotenv()
        
        # Ollama (local)
        from agent.llm.providers.ollama_provider import OllamaProvider
        self.providers['ollama'] = OllamaProvider({
            'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
            'model': os.getenv('OLLAMA_MODEL', 'llama3.2:1b')  # Lee dinámicamente
        })
        
        # OpenAI
        if os.getenv('OPENAI_API_KEY'):
            from agent.llm.providers.openai_provider import OpenAIProvider
            self.providers['openai'] = OpenAIProvider({
                'api_key': os.getenv('OPENAI_API_KEY'),
                'model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
            })
        
        # Groq
        if os.getenv('GROQ_API_KEY'):
            from agent.llm.providers.groq_provider import GroqProvider
            self.providers['groq'] = GroqProvider({
                'api_key': os.getenv('GROQ_API_KEY'),
                'model': os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile')
            })
        
        # Gemini, Mistral, MiMo... (similar)
    
    def get_active_provider(self) -> BaseLLMProvider:
        """Retorna proveedor activo."""
        if not self.active_provider:
            raise ProviderError("No active provider configured")
        return self.providers[self.active_provider]
    
    def switch_provider(self, provider_name: str, model: str = None):
        """
        Cambia proveedor activo.
        
        Args:
            provider_name: Nombre del proveedor (ollama, openai, etc.)
            model: Modelo específico (opcional)
        """
        if provider_name not in self.providers:
            raise ProviderNotFoundError(f"Provider '{provider_name}' not found")
        
        self.active_provider = provider_name
        
        if model:
            self.providers[provider_name].set_model(model)
        
        logger.info(f"Provider switched to: {provider_name} ({model or 'default'})")
    
    @classmethod
    def reset_instance(cls):
        """Reseta singleton (útil para testing o cambio de config)."""
        cls._instance = None
        cls._initialized = False
```

**Base Provider Interface**:

```python
class BaseLLMProvider(ABC):
    """Interfaz base para todos los proveedores LLM."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Genera respuesta del LLM.
        
        Args:
            prompt: Prompt enviado al modelo
            **kwargs: Parámetros adicionales (temperature, max_tokens, etc.)
        
        Returns:
            LLMResponse con texto generado y metadatos
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Lista modelos disponibles."""
        pass
    
    def set_model(self, model_name: str):
        """Cambia modelo activo."""
        self.model = model_name
        logger.info(f"Model changed to: {model_name}")
```

**OllamaProvider Implementation**:

```python
class OllamaProvider(BaseLLMProvider):
    """Proveedor para Ollama (modelos locales)."""
    
    def __init__(self, config: dict):
        self.base_url = config['base_url']
        self.model = config['model']  # Se lee de .env dinámicamente
        self.timeout = 120  # 2 minutos
    
    def generate(self, prompt: str, temperature: float = 0.7, 
                 max_tokens: int = 2048) -> LLMResponse:
        """Genera usando Ollama API."""
        import requests
        
        url = f"{self.base_url}/api/generate"
        payload = {
            'model': self.model,  # Lee valor actual de .env
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return LLMResponse(
                text=data['response'],
                provider='ollama',
                model=self.model,
                tokens_used=data.get('eval_count', 0),
                duration=data.get('total_duration', 0)
            )
        
        except requests.exceptions.Timeout:
            raise LLMTimeoutError(f"Ollama request timeout ({self.timeout}s)")
        except requests.exceptions.ConnectionError:
            raise LLMConnectionError("Cannot connect to Ollama. Is it running?")
```

---

### 5. Patch System

**Archivo**: `agent/core/patch_system.py`

**Versionado de Cambios**:

```python
class PatchSystem:
    """
    Sistema de parches incrementales con versionado y rollback.
    
    Permite aplicar cambios parciales sin regenerar código completo.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.patch_history = []
        self.snapshots = {}
        self._load_history()
    
    def apply_incremental(self, new_fragment: str, existing_code: str,
                          insertion_point: str = 'before </body>') -> str:
        """
        Aplica fragmento nuevo al código existente.
        
        Args:
            new_fragment: Código nuevo a insertar
            existing_code: Código actual
            insertion_point: Dónde insertar (regex o posición)
        
        Returns:
            Código combinado
        """
        # 1. Crear snapshot pre-cambio
        snapshot_id = self._create_snapshot(existing_code)
        
        # 2. Determinar ubicación de inserción
        insert_pos = self._find_insertion_point(existing_code, insertion_point)
        
        # 3. Aplicar parche
        combined_code = (
            existing_code[:insert_pos] +
            new_fragment +
            existing_code[insert_pos:]
        )
        
        # 4. Registrar en historial
        patch_record = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'snapshot_id': snapshot_id,
            'fragment': new_fragment,
            'insertion_point': insertion_point,
            'combined_code_length': len(combined_code)
        }
        self.patch_history.append(patch_record)
        self._save_history()
        
        logger.info(f"Patch applied: {patch_record['id']}")
        return combined_code
    
    def undo_last_patch(self) -> Optional[str]:
        """
        Revierte último parche aplicado.
        
        Returns:
            Código restaurado o None si no hay patches
        """
        if not self.patch_history:
            return None
        
        last_patch = self.patch_history.pop()
        snapshot_id = last_patch['snapshot_id']
        
        restored_code = self.snapshots.get(snapshot_id)
        if restored_code:
            logger.info(f"Patch undone: {last_patch['id']}")
            return restored_code
        
        return None
    
    def _create_snapshot(self, code: str) -> str:
        """Crea snapshot del código actual."""
        snapshot_id = str(uuid.uuid4())
        self.snapshots[snapshot_id] = code
        
        # Persistir en disco (sessions/{session_id}/snapshots/)
        snapshot_path = f"sessions/{self.session_id}/snapshots/{snapshot_id}.json"
        with open(snapshot_path, 'w') as f:
            json.dump({'code': code, 'timestamp': datetime.now().isoformat()}, f)
        
        return snapshot_id
```

---

### 6. Memory Manager

**Archivo**: `agent/core/memory_manager.py`

**Persistencia Contextual**:

```python
class MemoryManager:
    """
    Gestor de memoria conversacional contextual.
    
    - Historial persistente en JSON
    - Compresión automática (>50 mensajes)
    - Contexto relevante por sesión
    """
    
    def __init__(self, session_id: str, max_history: int = 50):
        self.session_id = session_id
        self.max_history = max_history
        self.history_file = f"sessions/{session_id}/memory.json"
        self.messages = []
        self._load_history()
    
    def add_message(self, role: str, content: str, metadata: dict = None):
        """
        Agrega mensaje al historial.
        
        Args:
            role: 'user' o 'assistant'
            content: Contenido del mensaje
            metadata: Info adicional (timestamp, tokens, etc.)
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.messages.append(message)
        
        # Auto-comprimir si excede límite
        if len(self.messages) > self.max_history * 1.2:
            self._compress_history()
        
        self._save_history()
    
    def get_context_window(self, window_size: int = 10) -> List[dict]:
        """
        Obtiene ventana de contexto reciente.
        
        Args:
            window_size: Número de mensajes recientes
        
        Returns:
            Lista de mensajes (últimos window_size)
        """
        return self.messages[-window_size:]
    
    def _compress_history(self):
        """
        Comprime historial manteniendo contexto esencial.
        
        Estrategia:
        1. Mantener primeros 5 mensajes (contexto inicial)
        2. Mantener últimos 20 mensajes (recientes)
        3. Resumir mensajes intermedios
        """
        if len(self.messages) <= self.max_history:
            return
        
        # Mantener inicio y fin
        initial_messages = self.messages[:5]
        recent_messages = self.messages[-20:]
        
        # Resumir medio (placeholder para implementación futura con LLM)
        middle_messages = self.messages[5:-20]
        summary = {
            'role': 'system',
            'content': f"[Resumen de {len(middle_messages)} mensajes intermedios]",
            'timestamp': datetime.now().isoformat(),
            'metadata': {'compressed': True, 'original_count': len(middle_messages)}
        }
        
        # Reconstruir historial comprimido
        self.messages = initial_messages + [summary] + recent_messages
        
        logger.info(f"History compressed: {len(self.messages)} messages")
        self._save_history()
    
    def _save_history(self):
        """Persiste historial en disco."""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.messages, f, indent=2)
    
    def _load_history(self):
        """Carga historial desde disco."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.messages = json.load(f)
```

---

## Flujos de Trabajo Críticos

### Flujo 1: Generación de Código Completo

```
Usuario: "Crea un botón rojo en HTML"
    ↓
[Frontend] chat.js → POST /chat {message: "...", session_id: "..."}
    ↓
[Backend] web.py → orchestration_layer.process_request()
    ↓
[Orchestrator] _detect_intention() → 'create'
[Orchestrator] _detect_language() → 'html'
[Orchestrator] _select_agent() → FrontendAgent()
    ↓
[FrontendAgent] build_prompt(user_message, context)
    ↓
[FrontendAgent] tool_manager.run('generate_with_llm', prompt=...)
    ↓
[ToolManager] _validate_params() ✓
[ToolManager] sandbox.execute(generate_wrapper)
    ↓
[generate_wrapper] provider_manager.get_active_provider()
[generate_wrapper] provider.generate(prompt, temperature=0.8)
    ↓
[OllamaProvider] POST http://localhost:11434/api/generate
    ↓
[Ollama] Procesa prompt → retorna texto
    ↓
[OllamaProvider] LLMResponse(text="<button style='background:red'>...", ...)
    ↓
[ToolManager] valida resultado → retorna texto
    ↓
[Orchestrator] ¿Hay código existente? NO → retorna directo
    ↓
[Backend] {response: "<button...>", type: "html"}
    ↓
[Frontend] code-editor.js muestra código
[Frontend] preview.js renderiza en iframe sandboxed
```

**Tiempo estimado**: 2-5 segundos (Ollama local)

---

### Flujo 2: Modificación Incremental (Patch)

```
Usuario: "Agrega un círculo rojo al HTML existente"
    ↓
[Orchestrator] Detecta: intención='create', hay código existente
    ↓
[FrontendAgent] Genera SOLO fragmento: `<circle cx="100" cy="100" r="50" fill="red"/>`
    ↓
[PatchSystem] _create_snapshot(código_actual) → snapshot_id
    ↓
[PatchSystem] _find_insertion_point(código, 'before </svg>') → pos=245
    ↓
[PatchSystem] Inserta fragmento en posición 245
    ↓
[PatchSystem] Registra patch en historial:
    {
        'id': 'uuid...',
        'snapshot_id': 'uuid...',
        'fragment': '<circle.../>',
        'timestamp': '2026-05-12T...'
    }
    ↓
[Backend] Retorna código combinado
    ↓
[Frontend] Muestra código actualizado + preview
    ↓
[Si usuario rechaza] PATCH_SYSTEM.undo_last_patch() → restaura snapshot
```

**Ventaja**: No regenera HTML completo, solo inserta fragmento nuevo.

---

### Flujo 3: Cambio de Modelo Dinámico

```
Usuario: Selecciona "deepseek-coder:latest" en menú configuración
    ↓
[Frontend] menu-functions.js → activateLocalModel('deepseek-coder:latest')
    ↓
[Frontend] POST /set-model {model: 'deepseek-coder:latest', provider: 'ollama'}
    ↓
[Backend] web.py:
    1. Actualiza .env: OLLAMA_MODEL=deepseek-coder:latest
    2. ProviderManager.reset_instance()  # Destruye singleton
    3. Retorna {status: 'success'}
    ↓
[Frontend] Recarga página o notifica cambio
    ↓
[Próximo request] ProviderManager se recrea:
    - Lee OLLAMA_MODEL actualizado de .env
    - OllamaProvider inicializa con nuevo modelo
    - Sin restart del servidor
```

**Clave**: OllamaProvider lee modelo dinámicamente de `.env` en cada inicialización.

---

### Flujo 4: Descarga de Modelo Ollama

```
Usuario: Clic en modelo no instalado (⬇️ icono)
    ↓
[Frontend] downloadLocalModel(modelName)
[Frontend] showModelDownloadIndicator(modelName) → Muestra spinner en header
    ↓
[Frontend] POST /system/check-model {model: modelName}
    ↓
[Backend] check_model():
    result = subprocess.run(['ollama', 'list'], capture_output=True)
    installed = modelName in result.stdout
    Retorna {installed: false}
    ↓
[Frontend] Modal confirmación: "¿Descargar {modelName}?"
[Usuario] Acepta
    ↓
[Frontend] POST /system/download-model {model: modelName}
    ↓
[Backend] download_single_model():
    1. Verifica si ya instalado (ollama list)
    2. Ejecuta: ollama pull modelName (timeout: 10 min)
    3. Refresca ProviderManager models list
    4. Retorna {status: 'success'}
    ↓
[Frontend] hideModelDownloadIndicator() → Oculta spinner
[Frontend] Modal éxito: "✅ Modelo descargado. ¿Activar ahora?"
```

**Indicador visual**: Spinner animado en header del chat durante descarga.

---

## API Reference

### Endpoints Principales

#### POST /chat

**Propósito**: Procesar mensaje de usuario y generar respuesta.

**Request**:
```json
{
  "message": "Crea un botón rojo",
  "session_id": "abc123",
  "context": {
    "current_code": "<html>...</html>",
    "language": "html",
    "history": [...]
  }
}
```

**Response**:
```json
{
  "response": "<button style='background:red'>Click</button>",
  "type": "html",
  "patch_applied": false,
  "tokens_used": 150,
  "duration_ms": 2340
}
```

**Errores**:
- `400`: Mensaje vacío
- `500`: Error LLM provider
- `504`: Timeout generación

---

#### POST /set-model

**Propósito**: Cambiar modelo activo dinámicamente.

**Request**:
```json
{
  "model": "deepseek-coder:latest",
  "provider": "ollama"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Modelo cambiado a deepseek-coder:latest"
}
```

**Efecto**: Actualiza `.env` y resetea ProviderManager singleton.

---

#### GET /api/ollama/models

**Propósito**: Obtener lista de modelos Ollama disponibles e instalados.

**Response**:
```json
{
  "available": [
    {"name": "llama3.2:1b", "size": "1.3GB", "installed": true},
    {"name": "mistral:7b", "size": "4.1GB", "installed": false},
    {"name": "deepseek-coder:latest", "size": "3.8GB", "installed": false}
  ],
  "installed_count": 1,
  "total_available": 3
}
```

---

#### POST /system/check-model

**Propósito**: Verificar si modelo específico está instalado.

**Request**:
```json
{
  "model": "mistral:7b"
}
```

**Response**:
```json
{
  "status": "success",
  "installed": false,
  "model": "mistral:7b"
}
```

---

#### POST /system/download-model

**Propósito**: Descargar modelo Ollama.

**Request**:
```json
{
  "model": "mistral:7b"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "✅ mistral:7b descargado correctamente"
}
```

**Timeout**: 10 minutos (600 segundos)

---

## Sistema de Extensiones

### Agregar Nuevo Proveedor LLM

**Paso 1**: Crear provider class

```python
# agent/llm/providers/nuevo_provider.py
from agent.llm.base_provider import BaseLLMProvider

class NuevoProvider(BaseLLMProvider):
    def __init__(self, config: dict):
        self.api_key = config['api_key']
        self.base_url = config.get('base_url', 'https://api.nuevo.com/v1')
        self.model = config.get('model', 'default-model')
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        import requests
        
        headers = {'Authorization': f'Bearer {self.api_key}'}
        payload = {'model': self.model, 'prompt': prompt}
        
        response = requests.post(
            f"{self.base_url}/generate",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        return LLMResponse(
            text=response.json()['text'],
            provider='nuevo',
            model=self.model
        )
    
    def get_available_models(self) -> List[str]:
        # Implementar lógica para listar modelos
        return ['modelo-1', 'modelo-2']
```

**Paso 2**: Registrar en ProviderManager

```python
# agent/llm/provider_manager.py
def _load_providers(self):
    # ... providers existentes ...
    
    if os.getenv('NUEVO_API_KEY'):
        from agent.llm.providers.nuevo_provider import NuevoProvider
        self.providers['nuevo'] = NuevoProvider({
            'api_key': os.getenv('NUEVO_API_KEY'),
            'model': os.getenv('NUEVO_MODEL', 'modelo-1')
        })
```

**Paso 3**: Agregar a `.env.example`

```bash
# Nuevo Provider
NUEVO_API_KEY=your-api-key-here
NUEVO_MODEL=modelo-1
```

---

### Agregar Nueva Tool

**Paso 1**: Implementar wrapper

```python
# agent/core/tool_manager.py
def _register_system_tools(self):
    # ... tools existentes ...
    
    self.registry.register(
        name="nueva_tool",
        func=self._nueva_tool_wrapper,
        description="Descripción clara de funcionalidad",
        category="custom",
        params={
            'param1': {'type': 'string', 'required': True},
            'param2': {'type': 'integer', 'default': 10}
        },
        security_level='medium'
    )

def _nueva_tool_wrapper(self, param1: str, param2: int = 10, **kwargs) -> Any:
    """
    Implementación de nueva tool.
    
    Args:
        param1: Descripción
        param2: Descripción
    
    Returns:
        Resultado procesado
    """
    # Validaciones
    if not param1:
        raise ValueError("param1 es requerido")
    
    # Lógica principal
    result = hacer_algo(param1, param2)
    
    return result
```

**Paso 2**: Usar en Agent

```python
# agent/core/frontend_agent.py
def process(self, task: str, context: dict) -> LLMResponse:
    # ... lógica existente ...
    
    result = tool_manager.run('nueva_tool', param1='valor', param2=20)
    
    return result
```

---

### Agregar Plugin

**Paso 1**: Crear plugin class

```python
# plugins/mi_plugin.py
class MiPlugin:
    def __init__(self):
        self.name = "mi_plugin"
        self.version = "1.0.0"
    
    def on_event(self, event_name: str, data: dict):
        """Maneja eventos del EventBus."""
        if event_name == 'message.received':
            print(f"Mensaje recibido: {data['message']}")
        elif event_name == 'code.generated':
            print(f"Código generado: {len(data['code'])} chars")
    
    def register_hooks(self, event_bus):
        """Registra listeners."""
        event_bus.subscribe('message.received', self.on_event)
        event_bus.subscribe('code.generated', self.on_event)
```

**Paso 2**: Cargar en web.py

```python
# web.py
from plugins.mi_plugin import MiPlugin

plugin = MiPlugin()
plugin.register_hooks(event_bus)
```

---

## Seguridad y Sandbox

### Content Security Policy (CSP)

**Implementación en preview.js**:

```javascript
const sandboxAttributes = {
    sandbox: 'allow-scripts allow-forms', // SIN allow-same-origin
    csp: "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline';"
};

iframe.setAttribute('sandbox', sandboxAttributes.sandbox);
iframe.setAttribute('csp', sandboxAttributes.csp);
```

**Restricciones**:
- ❌ No acceso a DOM padre
- ❌ No cookies/storage compartido
- ❌ No requests a dominios externos (sin allow-same-origin)
- ✅ Scripts inline permitidos (para HTML generado)
- ✅ Estilos inline permitidos

---

### Tool Validation

**Validación de parámetros**:

```python
def _validate_params(self, tool: Tool, params: dict):
    """Valida parámetros contra schema registrado."""
    for param_name, schema in tool.params.items():
        if schema.get('required') and param_name not in params:
            raise ValidationError(f"Parámetro requerido faltante: {param_name}")
        
        if param_name in params:
            value = params[param_name]
            expected_type = schema['type']
            
            if not isinstance(value, eval(expected_type)):
                raise ValidationError(
                    f"Tipo inválido para {param_name}: esperado {expected_type}, "
                    f"obtenido {type(value).__name__}"
                )
```

**Path Traversal Prevention**:

```python
def _sanitize_path(self, path: str) -> str:
    """Previene path traversal attacks."""
    # Resolver ruta absoluta
    abs_path = os.path.abspath(path)
    
    # Verificar que está dentro de directorio permitido
    allowed_dir = os.path.abspath('./workspace')
    if not abs_path.startswith(allowed_dir):
        raise SecurityError(f"Access denied: {path} outside workspace")
    
    return abs_path
```

---

### Input Sanitization

**HTML Generation**:

```python
def sanitize_generated_html(html: str) -> str:
    """
    Sanitiza HTML generado por LLM.
    
    Remueve:
    - Scripts maliciosos (event handlers)
    - Iframes externos
    - Objects/embeds
    """
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remover event handlers
    for tag in soup.find_all(True):
        attrs_to_remove = [
            attr for attr in tag.attrs
            if attr.startswith('on')  # onclick, onload, etc.
        ]
        for attr in attrs_to_remove:
            del tag[attr]
    
    # Remover tags peligrosos
    for tag in soup.find_all(['script', 'iframe', 'object', 'embed']):
        tag.decompose()
    
    return str(soup)
```

---

## Performance y Optimización

### Métricas Clave

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| **Latencia generación** | <5s (local), <2s (cloud) | ~3s (Ollama) |
| **Throughput requests** | 10 req/min | ~8 req/min |
| **Memory usage** | <512MB | ~380MB |
| **Preview render time** | <500ms | ~200ms |
| **File I/O ops** | <100ms | ~50ms |

---

### Optimizaciones Implementadas

#### 1. Lazy Loading de Providers

```python
class ProviderManager:
    def _load_providers(self):
        """Carga providers on-demand, no todos al inicio."""
        # Solo carga providers con API keys configuradas
        if os.getenv('OPENAI_API_KEY'):
            # Carga OpenAI
        # Si no hay API key, no carga (ahorra memoria)
```

#### 2. Connection Pooling

```python
import requests

session = requests.Session()
session.mount('http://', requests.adapters.HTTPAdapter(
    pool_connections=10,
    pool_maxsize=10,
    max_retries=3
))

# Reutiliza conexiones HTTP
response = session.post(url, json=payload)
```

#### 3. Response Streaming (futuro)

```python
# Implementación pendiente para reducir TTFB
def generate_stream(self, prompt: str):
    """Stream tokens conforme se generan."""
    for chunk in ollama_stream_api(prompt):
        yield chunk['response']
```

#### 4. Cache de Prompts

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def build_cached_prompt(template: str, context_hash: str) -> str:
    """Cachea prompts frecuentes."""
    return template.format(context=context_hash)
```

---

### Profiling

**Herramientas recomendadas**:

```bash
# CPU profiling
python -m cProfile -o profile.stats web.py

# Visualizar
snakeviz profile.stats

# Memory profiling
pip install memory-profiler
python -m memory_profiler web.py
```

---

## Testing Strategy

### Estructura de Tests

```
tests/
├── unit/
│   ├── test_llm_providers.py      # Providers individuales
│   ├── test_tool_manager.py       # Tools validation
│   ├── test_orchestration.py      # Intent detection
│   ├── test_patch_system.py       # Patch apply/undo
│   └── test_memory_manager.py     # History compression
├── integration/
│   ├── test_chat_flow.py          # Flujo completo /chat
│   ├── test_model_switching.py    # Cambio de modelo
│   └── test_file_operations.py    # Read/write files
└── e2e/
    ├── test_code_generation.py    # Generación + preview
    └── test_user_interactions.py  # Selenium/Playwright
```

---

### Test Example: Provider

```python
import pytest
from unittest.mock import patch, MagicMock
from agent.llm.providers.ollama_provider import OllamaProvider

class TestOllamaProvider:
    
    @pytest.fixture
    def provider(self):
        return OllamaProvider({
            'base_url': 'http://localhost:11434',
            'model': 'llama3.2:1b'
        })
    
    @patch('requests.post')
    def test_generate_success(self, mock_post, provider):
        """Test generación exitosa."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'response': 'Hola mundo',
            'eval_count': 50,
            'total_duration': 2000000000  # 2s en nanosegundos
        }
        mock_post.return_value = mock_response
        
        # Ejecutar
        result = provider.generate("Di hola")
        
        # Verificar
        assert result.text == 'Hola mundo'
        assert result.provider == 'ollama'
        assert result.tokens_used == 50
        mock_post.assert_called_once()
    
    def test_generate_timeout(self, provider):
        """Test timeout handling."""
        with patch('requests.post', side_effect=requests.exceptions.Timeout):
            with pytest.raises(LLMTimeoutError):
                provider.generate("test")
```

---

### Coverage Goals

| Módulo | Cobertura Actual | Objetivo Q2 | Objetivo Q4 |
|--------|------------------|-------------|-------------|
| **LLM Providers** | 80% | 90% | 95% |
| **Tool Manager** | 75% | 85% | 90% |
| **Orchestration** | 70% | 80% | 90% |
| **Patch System** | 65% | 75% | 85% |
| **Memory Manager** | 60% | 70% | 80% |
| **TOTAL** | **70%** | **80%** | **88%** |

---

## Deployment y DevOps

### Docker Deployment

**Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Ejecutar
CMD ["python", "web.py"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  kalin:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./sessions:/app/sessions
      - ./logs:/app/logs
      - ./.env:/app/.env
    environment:
      - ACTIVE_PROVIDER=ollama
    depends_on:
      - ollama
  
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

**Deploy**:

```bash
docker-compose up -d
docker-compose logs -f kalin
```

---

### CI/CD Pipeline (GitHub Actions)

**.github/workflows/ci.yml**:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/unit/ -v --cov=agent --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
  
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Lint Python
      run: |
        pip install flake8 black
        flake8 agent/ --max-line-length=88
        black --check agent/
```

---

### Monitoring

**Health Check Endpoint**:

```python
@app.route('/health')
def health_check():
    """Endpoint para health checks."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_provider': provider_manager.active_provider,
        'uptime_seconds': (datetime.now() - start_time).total_seconds()
    })
```

**Metrics Collection** (futuro):

```python
from prometheus_client import Counter, Histogram

REQUEST_COUNTER = Counter('kalin_requests_total', 'Total requests', ['endpoint'])
LATENCY_HISTOGRAM = Histogram('kalin_request_latency', 'Request latency')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - request.start_time
    LATENCY_HISTOGRAM.observe(latency)
    REQUEST_COUNTER.labels(endpoint=request.endpoint).inc()
    return response
```

---

## Troubleshooting Avanzado

### Problema 1: Ollama Connection Error

**Síntoma**: `Cannot connect to Ollama. Is it running?`

**Diagnóstico**:

```bash
# Verificar servicio
ollama list

# Verificar puerto
netstat -an | grep 11434

# Ver logs
tail -f ~/.ollama/logs/server.log
```

**Solución**:

```bash
# Reiniciar Ollama
ollama serve

# O en Windows
Restart-Service Ollama
```

---

### Problema 2: Provider Switching No Funciona

**Síntoma**: Cambio de modelo no se refleja en siguiente request.

**Causa**: ProviderManager singleton no se reseteó.

**Solución**:

```python
# En web.py endpoint /set-model
from agent.llm.provider_manager import ProviderManager

ProviderManager.reset_instance()  # Destruye singleton
# Próximo request recreará con nueva config
```

---

### Problema 3: Preview No Renderiza

**Síntoma**: Código generado pero preview en blanco.

**Diagnóstico**:

```javascript
// Abrir DevTools → Console
// Ver errores CSP

// Verificar iframe attributes
console.log(iframe.getAttribute('sandbox'));
console.log(iframe.getAttribute('srcdoc'));
```

**Solución**:

```javascript
// Asegurar CSP permite inline scripts
iframe.setAttribute('sandbox', 'allow-scripts');
iframe.setAttribute('csp', "script-src 'unsafe-inline';");
```

---

### Problema 4: Memory Leak en Sesiones Largas

**Síntoma**: Uso de memoria crece indefinidamente.

**Causa**: Historial no se comprime correctamente.

**Solución**:

```python
# Verificar compress_history se llama
def add_message(self, role, content):
    self.messages.append({...})
    
    if len(self.messages) > self.max_history * 1.2:
        self._compress_history()  # ¿Se ejecuta?
```

**Debug**:

```python
import tracemalloc
tracemalloc.start()

# Después de varias iteraciones
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[:10]:
    print(stat)
```

---

### Problema 5: Patch Application Corrompe HTML

**Síntoma**: HTML inválido después de aplicar patch.

**Causa**: Inserción en posición incorrecta.

**Solución**:

```python
def _find_insertion_point(self, html: str, point: str) -> int:
    """Usar regex más robusto."""
    import re
    
    # Buscar antes de </body> o </html>
    match = re.search(r'</body>|</html>', html, re.IGNORECASE)
    if match:
        return match.start()
    
    # Fallback: final del documento
    return len(html)
```

---

## Conclusión

Esta documentación proporciona una visión técnica completa del sistema Kalin AI para especialistas que deseen:

1. **Entender la arquitectura**: Componentes, patrones, flujos
2. **Extender funcionalidad**: Agregar providers, tools, plugins
3. **Optimizar performance**: Profiling, caching, pooling
4. **Garantizar seguridad**: CSP, sandbox, validation
5. **Debuggear problemas**: Troubleshooting avanzado
6. **Contribuir efectivamente**: Testing, CI/CD, standards

**Próximos pasos sugeridos**:
- Revisar código fuente de componentes core
- Ejecutar tests unitarios para entender comportamiento
- Experimentar con extensión (agregar provider simple)
- Profilear aplicación para identificar bottlenecks

---

**Mantenido por**: CarlosBV99 y colaboradores  
**Última actualización**: Mayo 2026  
**Versión**: 3.0
