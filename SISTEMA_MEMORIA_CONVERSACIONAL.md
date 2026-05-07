# 🧠 Sistema de Memoria Conversacional Avanzado - Kalin

## Visión General

Kalin ahora cuenta con un **sistema avanzado de memoria conversacional** que permite mantener contexto inteligente entre interacciones, inferir referencias implícitas y proporcionar respuestas más naturales y contextualizadas.

---

## ¿Qué es la Memoria Conversacional?

Es un sistema que registra y gestiona el contexto de las conversaciones con Kalin, permitiendo:

- ✅ **Seguimiento de archivos**: Recuerda qué archivos has analizado, corregido o creado
- ✅ **Inferencia inteligente**: Detecta referencias como "el archivo", "corrígelo", "analízalo"
- ✅ **Contexto de proyecto**: Mantiene información sobre el proyecto actual
- ✅ **Historial persistente**: Las sesiones se guardan y recuperan automáticamente
- ✅ **Métricas conversacionales**: Rastrea patrones de uso e interacciones frecuentes
- ✅ **Integración completa**: Trabaja junto con Experience Memory para aprendizaje continuo

---

## Arquitectura del Sistema

### Componentes Principales

#### 1. **ConversationMemory** (`agent/core/conversation_memory.py`)
Sistema central que gestiona:
- Historial de conversaciones (últimas 20 interacciones por defecto)
- Contexto de archivos (analizados, corregidos, creados)
- Contexto de proyecto (ruta, tipo, configuración)
- Preferencias del usuario detectadas
- Métricas de uso y patrones

#### 2. **ConversationManager** (`agent/core/conversation_manager.py`)
Gestión de sesiones completas:
- Mensajes completos (usuario + asistente)
- Tareas en progreso
- Variables de contexto
- Persistencia en `sessions/`

#### 3. **Integration Layer** (`agent/actions/executor.py`)
Puntos de integración automática:
- `/setpath` → Registra proyecto actual
- `/analyze` → Guarda archivo analizado
- `/fix` → Registra corrección aplicada
- `/create` → Almacena código generado
- Inferencia automática de contexto faltante

---

## Características Clave

### 1. Inferencia Inteligente de Contexto

El sistema detecta automáticamente cuando haces referencia a archivos o acciones anteriores:

```python
# Ejemplo de uso natural:
Usuario: "analiza main.py"
Kalin: [Analiza main.py]

Usuario: "ahora corrígelo"
# El sistema infiere que "lo" = main.py automáticamente
Kalin: [Corrige main.py sin que lo especifiques]
```

**Patrones detectados:**
- Referencias directas: "el archivo", "ese código", "este archivo"
- Pronombres: "arréglalo", "corrígelo", "analízalo", "revísalo"
- Referencias temporales: "lo anterior", "lo de antes", "el anterior"
- Referencias a proyecto: "mi proyecto", "el proyecto", "este proyecto"

### 2. Seguimiento de Archivos

El sistema mantiene registro de:
- Último archivo analizado
- Último archivo corregido
- Último archivo creado
- Archivos más utilizados (top 20)
- Problemas detectados en análisis

```python
# Estructura interna:
file_context = {
    "last_analyzed_file": "main.py",
    "last_analyzed_time": "2026-05-07T18:30:00",
    "last_fixed_file": "utils.py",
    "last_created_file": "test_main.py",
    "last_successful_fix": {...}
}
```

### 3. Detección Automática de Tipo de Proyecto

Cuando configuras la ruta con `/setpath`, Kalin detecta automáticamente el tipo de proyecto:

**Indicadores soportados:**
- **Flutter**: `pubspec.yaml`, `lib/main.dart`
- **Android**: `build.gradle`, `AndroidManifest.xml`
- **Python**: `requirements.txt`, `setup.py`, `pyproject.toml`
- **Node.js**: `package.json`, `node_modules`
- **React**: `package.json`, `src/App.js`
- **Vue**: `package.json`, `vue.config.js`
- **Django**: `manage.py`, `settings.py`
- **Flask**: `app.py`, `flask_app.py`

### 4. Extracción de Archivos desde Mensajes

El sistema puede detectar nombres de archivo mencionados en mensajes naturales:

```python
# Patrones soportados:
"revisa main.py"           → extrae "main.py"
"analiza app.js"           → extrae "app.js"
"corrige styles.css"       → extrae "styles.css"
"abre config.json"         → extrae "config.json"
```

**Extensiones soportadas:** `.py`, `.java`, `.dart`, `.js`, `.ts`, `.html`, `.css`, `.json`, `.yaml`, `.yml`, `.xml`, `.txt`

### 5. Métricas Conversacionales

El sistema rastrea automáticamente:
- Total de interacciones
- Conteo por tipo de intención (fix, analyze, create, etc.)
- Archivos más utilizados
- Tiempo promedio de respuesta
- Inicio de sesión

```python
metrics = {
    'total_interactions': 45,
    'intention_counts': {
        'fix': 20,
        'analyze': 15,
        'create': 10
    },
    'most_used_files': [
        {'file': 'main.py', 'count': 8, 'last_action': 'fixed'},
        {'file': 'utils.py', 'count': 5, 'last_action': 'analyzed'}
    ]
}
```

### 6. Persistencia Automática

- **Auto-guardado**: Cada 5 interacciones se guarda automáticamente
- **Carga automática**: Al iniciar, carga la sesión previa si existe
- **Almacenamiento**: Archivos JSON en carpeta `sessions/`
- **Formato**: `session_{timestamp}.json`

---

## Flujo de Uso

### Escenario 1: Conversación Natural con Archivos

```
Usuario: "analiza main.py"
→ conversation_memory.update_context("analyze", {"arg": "main.py"})

Usuario: "¿qué problemas encontraste?"
→ No necesita especificar archivo (contexto inferido)

Usuario: "corrígelo"
→ infer_missing_context() detecta referencia implícita
→ Usa last_analyzed_file = "main.py"
→ conversation_memory.update_context("fix", {"arg": "main.py"})

Usuario: "ahora crea un test para ese archivo"
→ Inferencia: "ese archivo" = main.py
→ conversation_memory.update_context("create", ...)
```

### Escenario 2: Cambio de Proyecto

```
Usuario: "/setpath /home/user/proyecto_flutter"
→ Detecta pubspec.yaml → project_type = "flutter"
→ conversation_memory.update_context("setpath", ...)

Usuario: "escanea el proyecto"
→ Usa project_context["current_project_path"]
→ Analiza estructura Flutter específica
```

### Escenario 3: Múltiples Archivos

```
Usuario: "analiza main.py"
→ file_context["last_analyzed_file"] = "main.py"

Usuario: "ahora analiza utils.py"
→ file_context["last_analyzed_file"] = "utils.py"
→ _track_file_usage("utils.py", "analyzed")

Usuario: "corrige el primero"
→ get_recent_files() retorna ["utils.py", "main.py"]
→ Usa main.py (primero mencionado recientemente)
```

---

## Integración con Otros Sistemas

### 1. Experience Memory

La memoria conversacional trabaja junto con Experience Memory:

```python
# Conversation Memory: Contexto inmediato
conversation_memory.update_context(
    intention="fix",
    args={"arg": "main.py"},
    result=codigo_corregido
)

# Experience Memory: Aprendizaje a largo plazo
experience_memory.record_experience(
    task_type='fix',
    problem_description="Fixed errors in main.py",
    file_type='python',
    success=True,
    confidence_score=0.8
)
```

**Diferencia clave:**
- **Conversation Memory**: Contexto de conversación actual (corto plazo)
- **Experience Memory**: Aprendizaje de patrones y estrategias (largo plazo)

### 2. Orchestrator

El orchestrator inicializa ambos sistemas:

```python
class Orchestrator:
    def __init__(self):
        self.conversation_manager = ConversationManager(session_id)
        self.conversation_memory = ConvMem(session_id, max_history=20)
        self.experience_memory = get_experience_memory()
```

### 3. Executor

Cada acción ejecutada actualiza la memoria:

```python
# En executor.ejecutar():
def ejecutar(self, contexto, utils):
    # 1. Inferir contexto faltante
    improved_args = self.conversation_memory.infer_missing_context(...)
    
    # 2. Ejecutar acción...
    
    # 3. Actualizar memoria conversacional
    self.conversation_memory.update_context(
        intention=intencion,
        args=args,
        result=resultado,
        metadata={...}
    )
```

---

## API de la Clase ConversationMemory

### Métodos Públicos

#### `update_context(intention, args, result, metadata)`
Actualiza el contexto después de una acción.

```python
conversation_memory.update_context(
    intention="analyze",
    args={"arg": "main.py"},
    result="Análisis completado...",
    metadata={"duration": 2.5, "file_type": "python"}
)
```

#### `infer_missing_context(mensaje, detected_intention, args)`
Infiere contexto faltante basado en conversación previa.

```python
improved_args = conversation_memory.infer_missing_context(
    mensaje="corrígelo",
    detected_intention="fix",
    args={}
)
# Retorna: {"arg": "main.py", "inferred_from_reference": True}
```

#### `get_last_analyzed_file()`
Obtiene el último archivo analizado.

```python
last_file = conversation_memory.get_last_analyzed_file()
# Retorna: "main.py" o None
```

#### `get_last_fixed_file()`
Obtiene el último archivo corregido.

```python
last_file = conversation_memory.get_last_fixed_file()
# Retorna: "utils.py" o None
```

#### `get_recent_files(limit=3)`
Obtiene los archivos mencionados recientemente.

```python
recent = conversation_memory.get_recent_files(limit=3)
# Retorna: ["main.py", "utils.py", "test.py"]
```

#### `get_conversation_summary()`
Obtiene resumen completo del estado conversacional.

```python
summary = conversation_memory.get_conversation_summary()
# Retorna dict con session_id, contexts, metrics, etc.
```

#### `save_to_file(filepath=None)`
Guarda la memoria en disco.

```python
conversation_memory.save_to_file()
# Guarda en sessions/session_{id}.json
```

#### `clear_history()`
Limpia el historial pero mantiene preferencias.

```python
conversation_memory.clear_history()
```

---

## Configuración

### Parámetros de Inicialización

```python
conversation_memory = ConversationMemory(
    max_history=20,          # Número máximo de entradas en historial
    session_id="session_123", # ID de sesión (auto-generado si None)
    storage_dir="sessions/"   # Directorio de almacenamiento
)
```

### Variables de Entorno

No requiere variables de entorno específicas. Usa la configuración general de Kalin.

---

## Ejemplos Prácticos

### Ejemplo 1: Corrección Sin Especificar Archivo

```python
# Usuario configura proyecto
Usuario: "/setpath /home/user/myproject"
→ conversation_memory.project_context["current_project_path"] = "/home/user/myproject"

# Usuario analiza archivo
Usuario: "analiza main.py"
→ conversation_memory.file_context["last_analyzed_file"] = "main.py"

# Usuario pide corrección sin especificar
Usuario: "hay errores, corrígelo"
→ infer_missing_context() detecta "corrígelo"
→ Usa last_analyzed_file = "main.py"
→ Ejecuta fix en main.py automáticamente
```

### Ejemplo 2: Referencia a Proyecto

```python
# Usuario configura proyecto
Usuario: "/setpath /home/user/flutter_app"
→ Detecta pubspec.yaml → project_type = "flutter"

# Usuario habla del proyecto
Usuario: "escanea mi proyecto"
→ Detecta "mi proyecto"
→ Usa project_context["current_project_path"]
→ Ejecuta scan en flutter_app
```

### Ejemplo 3: Múltiples Archivos en Conversación

```python
# Primera acción
Usuario: "analiza database.py"
→ file_context["last_analyzed_file"] = "database.py"

# Segunda acción
Usuario: "ahora revisa api.py"
→ file_context["last_analyzed_file"] = "api.py"
→ _track_file_usage("database.py", "analyzed")
→ _track_file_usage("api.py", "analyzed")

# Tercera acción con referencia temporal
Usuario: "corrige el primero"
→ get_recent_files() = ["api.py", "database.py"]
→ Usa database.py (primero en lista reciente)
```

---

## Beneficios del Sistema

### Para el Usuario:
✅ **Conversación natural**: No necesita repetir nombres de archivos  
✅ **Referencias implícitas**: Entiende "el archivo", "corrígelo", "lo anterior"  
✅ **Menos comandos**: Reduce necesidad de especificar todo explícitamente  
✅ **Contexto preservado**: Recuerda archivos y proyectos entre mensajes  

### Para el Sistema:
✅ **Mejor UX**: Interacción más fluida y humana  
✅ **Reducción de errores**: Menos malentendidos por contexto faltante  
✅ **Datos estructurados**: Historial organizado para análisis futuro  
✅ **Escalabilidad**: Base para features avanzadas (predicción, personalización)  

---

## Limitaciones Actuales

⚠️ **Historial limitado**: Solo últimas 20 interacciones (configurable)  
⚠️ **Una sesión activa**: No soporta múltiples sesiones simultáneas  
⚠️ **Inferencia básica**: No entiende referencias complejas o ambiguas  
⚠️ **Sin NLP avanzado**: Detección basada en patrones simples, no ML  

---

## Futuras Mejoras

🚀 **Roadmap:**

1. **NLP Avanzado**: Usar spaCy o transformers para entender referencias complejas
2. **Múltiples Sesiones**: Soporte para cambiar entre sesiones activas
3. **Predicción de Intención**: Predecir siguiente acción basada en historial
4. **Personalización**: Aprender preferencias individuales del usuario
5. **Búsqueda Semántica**: Buscar en historial por significado, no solo keywords
6. **Visualización**: Dashboard de historial conversacional
7. **Exportación**: Exportar conversaciones completas a formatos legibles
8. **Compresión Inteligente**: Resumir conversaciones antiguas para ahorrar espacio

---

## Troubleshooting

### Problema: La memoria no se carga al reiniciar

**Solución:**
- Verificar que la carpeta `sessions/` exista
- Comprobar permisos de escritura
- Revisar logs en `logs/kalin.log`

### Problema: Inferencia no funciona

**Solución:**
- Asegurar que hay historial previo (al menos una acción)
- Verificar que el archivo fue analizado/corregido recientemente
- Revisar que el mensaje contenga referencias reconocidas

### Problema: Archivos no se rastrean

**Solución:**
- Confirmar que las acciones usan `update_context()`
- Verificar que `max_history` no sea demasiado bajo
- Revisar logs para errores de persistencia

---

## Conclusión

El **Sistema de Memoria Conversacional Avanzado** transforma la experiencia de usar Kalin de interacciones aisladas a **conversaciones continuas y contextuales**, haciendo que el agente sea más inteligente, proactivo y fácil de usar.

**¡Empieza a usar referencias naturales y observa cómo Kalin entiende el contexto!**
