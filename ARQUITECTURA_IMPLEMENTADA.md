"""
INTEGRACIÓN ARQUITECTÓNICA - GUÍA COMPLETA
===========================================

Tu agente ahora tiene 4 capas nuevas que trabajan juntas:

1. STATE MANAGER (Persistencia mínima)
   - Archivos: agent/core/state_manager.py
   - Qué hace: Guarda ruta, último archivo, último fix en .agent_state.json
   - Ventaja: No pierde contexto entre requests
   - API:
     * state.set_ruta(ruta)                    → Configura proyecto
     * state.get_ruta()                        → Obtiene ruta actual
     * state.set_ultimo_fix(ruta, orig, nuevo) → Guarda fix pendiente
     * state.get_ultimo_fix()                  → Recupera fix para /apply
     * state.registrar_exito() / registrar_fallo() → Métricas internas

2. RETRY ENGINE (Reintentos progresivos)
   - Archivo: agent/core/retry_engine.py
   - Qué hace: Si LLM falla, prueba estrategias más agresivas
   - Niveles (en orden de intento):
     1. CONSERVATIVE  → Prompt estricto, pocos tokens
     2. SMART         → Balance (default)
     3. AGGRESSIVE    → Prompt directo, muchos tokens
     4. HEURISTIC     → Fixes locales (regex, imports)
     5. EMERGENCY     → Retorna original con warning
   - API:
     * retry.ejecutar(codigo, objetivo, estrategia, max_tokens)
     * Retorna: código reparado o None

3. PROJECT ANALYZER (Mapeo inteligente)
   - Archivo: agent/core/project_analyzer.py
   - Qué hace: Mapea toda la estructura del proyecto
   - Beneficios:
     * Búsqueda de archivos rápida (no camina todo el FS)
     * Detecta tipo de proyecto (Python, Flutter, etc)
     * Extrae imports para contexto
   - API:
     * analyzer.get_archivos_por_tipo(tipo)
     * analyzer.get_tipo_proyecto()
     * analyzer.buscar_archivo(nombre)
     * analyzer.get_resumen()

4. STRATEGIES (Especialización por tipo)
   - Archivos: agent/actions/strategies/
     * base_strategy.py      → Clase abstracta
     * python_strategy.py    → Para .py
     * project_strategy.py   → Para proyectos enteros
   - Diseño: Patrón Strategy (fácil de extender)
   - API:
     * estrategia.analizar(codigo)        → Análisis
     * estrategia.reparar(codigo, analisis)
     * estrategia.mejorar(codigo)

FLUJO ACTUAL (SIN ROMPER LO EXISTENTE):
=====================================

/setpath <ruta>
  ↓
  Executor.ejecutar() 
    → state_manager.set_ruta(ruta)  [✓ Persistido]
    → project_analyzer = ProjectAnalyzer(ruta)  [✓ Mapeo]

/fix <archivo>
  ↓
  Executor.ejecutar()
    → Busca con project_analyzer (más rápido)
    → Lee archivo
    → state_manager.set_ultimo_archivo()  [✓ Registrado]
    → Detecta tipo (.py → python)
    → Carga estrategia adecuada
    → Estrategia.reparar()
      → analiza(codigo)
      → retry_engine.ejecutar()  [✓ Reintentos progresivos]
        → si falla: prueba estrategias más agresivas
        → si aún falla: heurística local
        → si todo falla: emergencia
    → state_manager.set_ultimo_fix()  [✓ Para /apply]
    → Retorna preview + diff

/apply
  ↓
  Executor.ejecutar()
    → state_manager.get_ultimo_fix()
    → Valida código
    → Guarda backup (.bak)
    → Escribe archivo
    → state_manager.clear_ultimo_fix()
    → state_manager.registrar_exito()

CAMBIOS EN executor.py (MÍNIMOS):
================================

✅ Agregué imports de nuevos módulos
✅ __init__: Inicializa StateManager, RetryEngine, ProjectAnalyzer
✅ setpath: Ahora usa state_manager en lugar de contexto["estado"]
✅ apply: Usa state_manager.get_ultimo_fix()
✅ fix: 
   - Usa ProjectAnalyzer para búsqueda
   - Detecta tipo de archivo
   - Carga estrategia correspondiente
   - Usa RetryEngine dentro de la estrategia
✅ Agregué métodos auxiliares:
   - _get_strategy(tipo) → Cache de estrategias
   - _detectar_tipo_archivo(ruta) → Extensión

CÓMO ESCALA ESTO:
=================

Nuevo tipo de archivo? Fácil:

1. Crea: agent/actions/strategies/kotlin_strategy.py
   class KotlinStrategy(BaseStrategy):
       def analizar(self, codigo):
           ...
       def reparar(self, codigo, analisis):
           ...

2. En executor._get_strategy():
   elif tipo == "kotlin":
       estrategia = KotlinStrategy(self.retry_engine)

3. Listo. Sin modificar /fix, sin romper nada.

ESTADO PERSISTENTE (.agent_state.json):
======================================

Contenido:
{
  "ruta_proyecto": "/path/to/project",
  "ultimo_archivo": {
    "ruta": "/path/to/file.py",
    "primeras_lineas": "import ... código..."
  },
  "ultimo_fix": {
    "ruta": "/path/to/file.py",
    "codigo_original": "...",
    "codigo_nuevo": "..."
  },
  "estrategia_activa": "smart",
  "contador_fallos": 0,
  "contador_exitos": 5
}

Actualiza automáticamente cada acción.
Se mantiene incluso entre reinicios.

MÉTRICAS INTERNAS:
==================

contador_exitos ↑   → Si muchos éxitos, estrategia se mantiene en "smart"
contador_fallos ↑ 3 → Cambia a "aggressive" automáticamente
Se resetea con /setpath

Para debug: GET /debug/state (próximo)

TESTING:
========

Ejecuta: python test_new_architecture.py
Valida:
  ✅ Todos los imports
  ✅ Instanciación de clases
  ✅ Métodos básicos
  ✅ Backward compatibility

PRÓXIMAS MEJORAS (OPCIONALMENTE):
================================

1. Endpoint /debug/state → Estado actual + métricas
2. Endpoint /design <requerimiento> → Usa ProjectStrategy
3. Almacenamiento git: agent/git_fix.py integrado en state
4. Cache de análisis para archivos no modificados
5. Logging estructurado de cada intento

TODO INTEGRADO Y FUNCIONANDO SIN ROMPER:
========================================

✅ /setpath sigue funcionando (ahora persiste estado)
✅ /fix sigue funcionando (ahora con strategies + retry)
✅ /apply sigue funcionando (ahora con state_manager)
✅ /scan sigue igual
✅ /analyze sigue igual
✅ /create sigue igual
✅ /refactor sigue igual

Arquitectura escalable lista para nivel 2:
➜ Multi-archivo (ProjectStrategy)
➜ Generación de UI (Flutter)
➜ Diseño full-stack
"""
