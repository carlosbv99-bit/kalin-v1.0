"""
EJEMPLOS PRÁCTICOS DE USO
=========================

Esta sección tiene ejemplos reales de cómo usar la nueva arquitectura.
"""

# ==============================================================================
# EJEMPLO 1: StateManager - Persistencia de estado
# ==============================================================================

from agent.core.state_manager import StateManager

# Inicializa (carga .agent_state.json si existe)
state = StateManager()

# Configura proyecto
state.set_ruta("/home/usuario/mi_proyecto")

# Ahora, incluso si reinicia la app, la ruta se recuerda:
print(state.get_ruta())  # → /home/usuario/mi_proyecto

# Registra último archivo procesado
state.set_ultimo_archivo("/home/usuario/mi_proyecto/main.py", "def hello():\n    print('hi')")

# Guarda un fix pendiente (para /apply)
state.set_ultimo_fix(
    ruta="/home/usuario/mi_proyecto/main.py",
    original="def hello():\n    print(x)  # Error: x no definida",
    nuevo="def hello():\n    x = 'hi'\n    print(x)"
)

# Recupera el fix
fix_pendiente = state.get_ultimo_fix()
print(fix_pendiente)
# {
#     "ruta": "...",
#     "codigo_original": "...",
#     "codigo_nuevo": "..."
# }

# Registra métricas
state.registrar_exito()      # Éxito
state.registrar_fallo()       # Fallo

estado = state.get_estado()
print(f"Éxitos: {estado['contador_exitos']}, Fallos: {estado['contador_fallos']}")


# ==============================================================================
# EJEMPLO 2: RetryEngine - Reintentos progresivos
# ==============================================================================

from agent.core.retry_engine import RetryEngine

retry_engine = RetryEngine()

codigo_problematico = """
import psycopg2

def conectar_db():
    conn = psycopg2.connect(
        host="localhost",
        user=DB_USER,  # ❌ DB_USER no definida
        password=DB_PASSWORD,  # ❌ DB_PASSWORD no definida
    )
    return conn
"""

# Sin LLM (offline): Usa heurística
resultado_heuristica = retry_engine._heuristic(codigo_problematico, "fix", 1000)
print("=== ESTRATEGIA HEURÍSTICA (LOCAL) ===")
print(resultado_heuristica)
# Retorna el código sin cambios mayores (las heurísticas son básicas)

# Con LLM (online): Usa estrategia completa con fallbacks
# (Requiere Ollama corriendo)
resultado = retry_engine.ejecutar(
    codigo=codigo_problematico,
    objetivo="fix",
    estrategia="smart",
    max_tokens=1200
)

# Internamente hace:
# 1. Intenta estrategia SMART
# 2. Si falla → intenta AGGRESSIVE
# 3. Si falla → intenta HEURISTIC
# 4. Si falla → EMERGENCY
# Retorna el primer resultado válido


# ==============================================================================
# EJEMPLO 3: ProjectAnalyzer - Mapeo de proyecto
# ==============================================================================

from agent.core.project_analyzer import ProjectAnalyzer

proyecto = ProjectAnalyzer("/home/usuario/mi_proyecto")

# Obtén resumen del proyecto
resumen = proyecto.get_resumen()
print(resumen)
# {
#     "ruta": "/home/usuario/mi_proyecto",
#     "tipo_principal": "python",
#     "total_archivos": 42,
#     "tipos": {
#         "python": 30,
#         "html": 5,
#         "css": 3,
#         "js": 4
#     },
#     "archivos": [lista de primeros 20 archivos]
# }

# Busca archivos de tipo específico
archivos_python = proyecto.get_archivos_por_tipo("python")
print(archivos_python)
# ['main.py', 'utils/helpers.py', 'config/settings.py', ...]

# Busca un archivo por nombre
ruta_archivo = proyecto.buscar_archivo("helpers.py")
print(ruta_archivo)
# 'utils/helpers.py'

# Detecta tipo de proyecto
tipo = proyecto.get_tipo_proyecto()
print(tipo)  # 'python', 'django', 'flutter', etc.

# Extrae todos los imports (para context)
imports = proyecto.get_imports_proyecto()
print(imports)
# {'import numpy as np', 'from flask import Flask', ...}


# ==============================================================================
# EJEMPLO 4: Strategies - Especialización por tipo
# ==============================================================================

from agent.core.retry_engine import RetryEngine
from agent.actions.strategies import PythonStrategy

retry_engine = RetryEngine()
strategy = PythonStrategy(retry_engine)

codigo_python = """
def calcular_promedio(numeros):
    return sum(numeros) / len(numeros)  # ❌ ZeroDivisionError si lista vacía
"""

# Analiza el código
analisis = strategy.analizar(codigo_python)
print("=== ANÁLISIS ===")
print(analisis)

# Repara basándose en el análisis
codigo_reparado = strategy.reparar(codigo_python, analisis)
print("=== CÓDIGO REPARADO ===")
print(codigo_reparado)

# Mejora (sin necesidad de análisis previo)
codigo_mejorado = strategy.mejorar(codigo_python)
print("=== CÓDIGO MEJORADO ===")
print(codigo_mejorado)

# Valida sintaxis básica
es_valido = strategy.validar(codigo_reparado)
print(f"¿Sintaxis válida? {es_valido}")  # True


# ==============================================================================
# EJEMPLO 5: ProjectStrategy - Diseño de proyectos
# ==============================================================================

from agent.actions.strategies import ProjectStrategy

retry_engine = RetryEngine()
strategy_proyecto = ProjectStrategy(retry_engine, "/home/usuario/nuevo_proyecto")

# Obtiene contexto del proyecto
contexto = strategy_proyecto.get_contexto_proyecto()
print(contexto)
# {
#     "tipo": "python_project",
#     "total_archivos": 5,
#     "tipos": {"python": 5},
#     "imports_detectados": ["import os", "import sys"],
#     "resumen": {...}
# }

# Analiza todo el proyecto
analisis_proyecto = strategy_proyecto.analizar("código del proyecto")
print(analisis_proyecto)

# Diseña mejoras
proyecto_mejorado = strategy_proyecto.mejorar("código actual")
print(proyecto_mejorado)


# ==============================================================================
# EJEMPLO 6: Flujo completo en API
# ==============================================================================

"""
Usuario hace:
    POST /chat
    {"mensaje": "/setpath /home/usuario/proyecto"}

Backend:
    1. Executor.ejecutar(contexto, utils)
    2. intencion = "setpath"
    3. state_manager.set_ruta("/home/usuario/proyecto")
    4. project_analyzer = ProjectAnalyzer("/home/usuario/proyecto")
    5. Retorna: "Ruta configurada: /home/usuario/proyecto"
    6. .agent_state.json se actualiza automáticamente

---

Usuario hace:
    POST /chat
    {"mensaje": "/fix main.py"}

Backend:
    1. Executor.ejecutar(contexto, utils)
    2. intencion = "fix"
    3. ruta = project_analyzer.buscar_archivo("main.py")  [Rápido]
    4. codigo = leer_archivo(ruta)
    5. state_manager.set_ultimo_archivo(ruta, codigo)
    6. tipo = _detectar_tipo_archivo(ruta)  # ".py" → "python"
    7. estrategia = _get_strategy("python")
    8. nuevo = estrategia.reparar(codigo, estrategia.analizar(codigo))
       ↓
       Internamente:
       - retry_engine.ejecutar() con reintentos progresivos
       - Si LLM falla → intenta estrategias más agresivas
       - Si todo falla → heurística local
    9. state_manager.set_ultimo_fix(ruta, codigo, nuevo)
    10. state_manager.registrar_exito() o registrar_fallo()
    11. Retorna: preview + diff

---

Usuario hace:
    POST /chat
    {"mensaje": "/apply"}

Backend:
    1. Executor.ejecutar(contexto, utils)
    2. intencion = "apply"
    3. fix = state_manager.get_ultimo_fix()
    4. guardar_backup(ruta, codigo_original)
    5. escribir_archivo(ruta, codigo_nuevo)
    6. state_manager.clear_ultimo_fix()
    7. state_manager.registrar_exito()
    8. Retorna: "✅ Cambios aplicados"
    9. .agent_state.json se actualiza
"""


# ==============================================================================
# EJEMPLO 7: Agregar nueva estrategia (Flutter)
# ==============================================================================

"""
Para soportar Flutter en el futuro:

1. Crea: agent/actions/strategies/flutter_strategy.py

class FlutterStrategy(BaseStrategy):
    def analizar(self, codigo):
        prompt = '''Eres experto en Flutter/Dart.
        Analiza este código:
        ...
        '''
        return generate(prompt)
    
    def reparar(self, codigo, analisis):
        return self.retry_engine.ejecutar(
            codigo=codigo,
            objetivo="fix",
            estrategia="smart"
        )

2. En executor._get_strategy():

elif tipo == "dart":
    estrategia = FlutterStrategy(self.retry_engine)

3. Listo. /fix archivo.dart funcionará automáticamente.
"""


# ==============================================================================
# EJEMPLO 8: Debug - Ver estado interno
# ==============================================================================

state = StateManager()
estado_completo = state.get_estado()

print("""
=== ESTADO DEL AGENTE ===
Ruta del proyecto: {ruta_proyecto}
Último archivo: {ultimo_archivo}
Último fix: {ultimo_fix}
Estrategia activa: {estrategia_activa}
Éxitos totales: {contador_exitos}
Fallos totales: {contador_fallos}
""".format(**estado_completo))
