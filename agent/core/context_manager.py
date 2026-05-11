"""
Context Manager Modular
Divide el contexto en módulos independientes para evitar "prompt gigante"

Estructura:
- system_context: Reglas del sistema, instrucciones maestras
- conversation_context: Historial reciente de la conversación
- project_context: Información del proyecto actual
- file_context: Archivos relevantes (analizados, modificados)
- memory_context: Experiencias y patrones aprendidos
- execution_context: Estado actual de ejecución (tools usadas, resultados)
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from agent.core.logger import get_logger

logger = get_logger('kalin.context_manager')


class SystemContext:
    """
    Contexto del sistema - Reglas e instrucciones maestras
    
    Se mantiene constante durante toda la sesión
    """
    
    def __init__(self):
        self.role = "Kalin - Asistente de programación autónomo"
        self.capabilities = [
            "Generar código en múltiples lenguajes",
            "Analizar y corregir errores",
            "Refactorizar código existente",
            "Crear archivos y proyectos",
            "Responder preguntas técnicas"
        ]
        self.rules = [
            "Genera SOLO código cuando se solicite creación/corrección",
            "NO incluyas explicaciones a menos que se pidan explícitamente",
            "NO uses markdown (```) en las respuestas de código",
            "Prioriza código limpio y funcional",
            "Si hay ambigüedad, pregunta antes de actuar"
        ]
        self.format_instructions = {
            "code_only": True,
            "no_markdown": True,
            "no_explanations": True,
            "language_detection": "auto"
        }
    
    def build(self) -> str:
        """Construye el prompt del sistema"""
        return f"""
# ROL
{self.role}

# CAPACIDADES
{chr(10).join(f'- {cap}' for cap in self.capabilities)}

# REGLAS
{chr(10).join(f'- {rule}' for rule in self.rules)}

# FORMATO DE RESPUESTA
- Código puro: {self.format_instructions['code_only']}
- Sin markdown: {self.format_instructions['no_markdown']}
- Sin explicaciones: {self.format_instructions['no_explanations']}
- Detección de lenguaje: {self.format_instructions['language_detection']}
""".strip()


class ConversationContext:
    """
    Contexto conversacional - Historial reciente
    
    Se actualiza con cada mensaje
    """
    
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self.history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """Agrega un mensaje al historial"""
        self.history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Limitar historial
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-(self.max_turns * 2):]
    
    def get_recent(self, turns: int = None) -> List[Dict]:
        """Obtiene los últimos N turnos"""
        turns = turns or self.max_turns
        return self.history[-(turns * 2):]
    
    def build(self) -> str:
        """Construye el contexto conversacional"""
        if not self.history:
            return "# CONVERSACIÓN\nSin historial previo."
        
        lines = ["# CONVERSACIÓN RECIENTE"]
        for msg in self.history[-(self.max_turns * 2):]:
            role = msg['role'].upper()
            content = msg['content'][:200]  # Truncar mensajes largos
            lines.append(f"{role}: {content}")
        
        return "\n".join(lines)
    
    def clear(self):
        """Limpia el historial"""
        self.history = []


class ProjectContext:
    """
    Contexto del proyecto - Información estructural
    
    Se actualiza cuando cambia el proyecto o se escanea
    """
    
    def __init__(self):
        self.project_path: str = ""
        self.project_type: str = "unknown"
        self.languages: List[str] = []
        self.structure: Dict[str, Any] = {}
        self.dependencies: List[str] = []
        self.last_scan: Optional[str] = None
    
    def update(self, path: str, structure: Dict = None, languages: List[str] = None):
        """Actualiza información del proyecto"""
        self.project_path = path
        self.last_scan = datetime.now().isoformat()
        
        if structure:
            self.structure = structure
        
        if languages:
            self.languages = languages
        
        # Detectar tipo de proyecto
        self._detect_project_type()
    
    def _detect_project_type(self):
        """Detecta el tipo de proyecto basado en archivos"""
        if not self.project_path or not os.path.exists(self.project_path):
            return
        
        indicators = {
            'requirements.txt': 'python',
            'package.json': 'nodejs',
            'pom.xml': 'java-maven',
            'build.gradle': 'java-gradle',
            'Cargo.toml': 'rust',
            'go.mod': 'go',
            'pubspec.yaml': 'flutter'
        }
        
        for filename, proj_type in indicators.items():
            if os.path.exists(os.path.join(self.project_path, filename)):
                self.project_type = proj_type
                break
    
    def build(self) -> str:
        """Construye el contexto del proyecto"""
        if not self.project_path:
            return "# PROYECTO\nNo hay proyecto seleccionado."
        
        return f"""
# PROYECTO ACTUAL
Ruta: {self.project_path}
Tipo: {self.project_type}
Lenguajes: {', '.join(self.languages) if self.languages else 'No detectado'}
Último escaneo: {self.last_scan or 'Nunca'}

# ESTRUCTURA
{self._format_structure()}
""".strip()
    
    def _format_structure(self) -> str:
        """Formatea la estructura del proyecto"""
        if not self.structure:
            return "Estructura no disponible"
        
        # Mostrar solo primeros niveles
        lines = []
        for key, value in list(self.structure.items())[:10]:
            if isinstance(value, list):
                lines.append(f"- {key}/ ({len(value)} archivos)")
            else:
                lines.append(f"- {key}")
        
        return "\n".join(lines) if lines else "Estructura vacía"


class FileContext:
    """
    Contexto de archivos - Archivos relevantes para la tarea actual
    
    Se actualiza cuando se lee/analiza/modifica un archivo
    """
    
    def __init__(self, max_files: int = 3):
        self.max_files = max_files
        self.recent_files: List[Dict[str, Any]] = []
        self.current_file: Optional[str] = None
        self.file_contents: Dict[str, str] = {}
    
    def add_file(self, path: str, content: str = None, action: str = "read"):
        """Registra un archivo como relevante"""
        entry = {
            'path': path,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'size': len(content) if content else 0
        }
        
        self.recent_files.append(entry)
        
        # Guardar contenido si se proporciona
        if content:
            self.file_contents[path] = content[:5000]  # Limitar tamaño
        
        # Mantener current_file actualizado
        self.current_file = path
        
        # Limitar lista
        if len(self.recent_files) > self.max_files:
            self.recent_files = self.recent_files[-self.max_files:]
    
    def get_file_content(self, path: str) -> Optional[str]:
        """Obtiene contenido almacenado de un archivo"""
        return self.file_contents.get(path)
    
    def build(self) -> str:
        """Construye el contexto de archivos"""
        if not self.recent_files:
            return "# ARCHIVOS\nNo hay archivos en contexto."
        
        lines = ["# ARCHIVOS RELEVANTES"]
        
        for i, file_info in enumerate(self.recent_files[-self.max_files:], 1):
            path = file_info['path']
            action = file_info['action']
            size = file_info['size']
            
            lines.append(f"\n## Archivo {i}: {os.path.basename(path)}")
            lines.append(f"Ruta: {path}")
            lines.append(f"Acción: {action}")
            lines.append(f"Tamaño: {size} chars")
            
            # Incluir contenido si está disponible y es pequeño
            if path in self.file_contents and len(self.file_contents[path]) < 1000:
                lines.append(f"Contenido:\n{self.file_contents[path]}")
        
        return "\n".join(lines)


class MemoryContext:
    """
    Contexto de memoria - Experiencias y patrones aprendidos
    
    Se alimenta del ExperienceMemory
    """
    
    def __init__(self, max_patterns: int = 5):
        self.max_patterns = max_patterns
        self.relevant_patterns: List[Dict[str, Any]] = []
        self.past_solutions: List[Dict[str, Any]] = []
    
    def add_pattern(self, pattern: Dict[str, Any]):
        """Agrega un patrón relevante"""
        self.relevant_patterns.append(pattern)
        
        if len(self.relevant_patterns) > self.max_patterns:
            self.relevant_patterns = self.relevant_patterns[-self.max_patterns:]
    
    def add_past_solution(self, solution: Dict[str, Any]):
        """Agrega una solución pasada similar"""
        self.past_solutions.append(solution)
        
        if len(self.past_solutions) > self.max_patterns:
            self.past_solutions = self.past_solutions[-self.max_patterns:]
    
    def build(self) -> str:
        """Construye el contexto de memoria"""
        lines = ["# MEMORIA Y EXPERIENCIA"]
        
        if self.relevant_patterns:
            lines.append("\n## Patrones Relevantes")
            for pattern in self.relevant_patterns[-self.max_patterns:]:
                description = pattern.get('description', 'Sin descripción')
                success_rate = pattern.get('success_rate', 0)
                lines.append(f"- {description} (éxito: {success_rate:.0%})")
        
        if self.past_solutions:
            lines.append("\n## Soluciones Pasadas Similares")
            for solution in self.past_solutions[-self.max_patterns:]:
                problem = solution.get('problem', 'Desconocido')
                approach = solution.get('approach', 'Desconocido')
                lines.append(f"- Problema: {problem[:100]}")
                lines.append(f"  Enfoque: {approach[:100]}")
        
        if not self.relevant_patterns and not self.past_solutions:
            lines.append("Sin experiencias previas relevantes.")
        
        return "\n".join(lines)


class ExecutionContext:
    """
    Contexto de ejecución - Estado actual de la tarea
    
    Se actualiza durante la ejecución del plan
    """
    
    def __init__(self):
        self.current_step: int = 0
        self.total_steps: int = 0
        self.tools_used: List[Dict[str, Any]] = []
        self.intermediate_results: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.start_time: Optional[float] = None
    
    def start_execution(self, total_steps: int):
        """Inicia la ejecución"""
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = datetime.now().timestamp()
    
    def record_tool_use(self, tool_name: str, params: Dict, result: Any, success: bool):
        """Registra uso de una tool"""
        self.tools_used.append({
            'tool': tool_name,
            'params': params,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
        
        if success:
            self.intermediate_results.append({
                'step': self.current_step,
                'tool': tool_name,
                'result': str(result)[:500] if result else None
            })
        
        self.current_step += 1
    
    def record_error(self, error: str):
        """Registra un error"""
        self.errors.append(error)
    
    def build(self) -> str:
        """Construye el contexto de ejecución"""
        lines = ["# ESTADO DE EJECUCIÓN"]
        
        if self.start_time:
            elapsed = datetime.now().timestamp() - self.start_time
            lines.append(f"Paso: {self.current_step}/{self.total_steps}")
            lines.append(f"Tiempo transcurrido: {elapsed:.1f}s")
        
        if self.tools_used:
            lines.append(f"\n## Tools Usadas: {len(self.tools_used)}")
            for tool_info in self.tools_used[-5:]:  # Últimas 5
                status = "✓" if tool_info['success'] else "✗"
                lines.append(f"- {status} {tool_info['tool']}")
        
        if self.errors:
            lines.append(f"\n## Errores: {len(self.errors)}")
            for error in self.errors[-3:]:  # Últimos 3
                lines.append(f"- {error[:100]}")
        
        if not self.tools_used and not self.errors:
            lines.append("Ejecución no iniciada.")
        
        return "\n".join(lines)


class ContextManager:
    """
    Gestor central de contextos modulares
    
    Uso:
        context_mgr = ContextManager()
        full_prompt = context_mgr.build_full_prompt()
    """
    
    def __init__(self):
        self.system = SystemContext()
        self.conversation = ConversationContext(max_turns=5)
        self.project = ProjectContext()
        self.files = FileContext(max_files=3)
        self.memory = MemoryContext(max_patterns=5)
        self.execution = ExecutionContext()
        
        logger.info("ContextManager initialized with modular contexts")
    
    def update_conversation(self, role: str, content: str):
        """Actualiza contexto conversacional"""
        self.conversation.add_message(role, content)
    
    def update_project(self, path: str, **kwargs):
        """Actualiza contexto de proyecto"""
        self.project.update(path, **kwargs)
    
    def update_file(self, path: str, content: str = None, action: str = "read"):
        """Actualiza contexto de archivos"""
        self.files.add_file(path, content, action)
    
    def update_memory(self, patterns: List[Dict], solutions: List[Dict]):
        """Actualiza contexto de memoria"""
        for pattern in patterns:
            self.memory.add_pattern(pattern)
        for solution in solutions:
            self.memory.add_past_solution(solution)
    
    def start_execution(self, total_steps: int):
        """Inicia contexto de ejecución"""
        self.execution.start_execution(total_steps)
    
    def record_tool_result(self, tool: str, params: Dict, result: Any, success: bool):
        """Registra resultado de tool"""
        self.execution.record_tool_use(tool, params, result, success)
    
    def build_full_prompt(self, user_query: str) -> str:
        """
        Construye el prompt completo combinando todos los contextos
        
        Args:
            user_query: Consulta actual del usuario
        
        Returns:
            Prompt completo y modular
        """
        sections = [
            self.system.build(),
            self.project.build(),
            self.files.build(),
            self.memory.build(),
            self.conversation.build(),
            self.execution.build(),
            f"# CONSULTA ACTUAL\n{user_query}"
        ]
        
        return "\n\n".join(sections)
    
    def build_lightweight_prompt(self, user_query: str) -> str:
        """
        Construye prompt ligero (solo contextos esenciales)
        
        Para tareas simples que no necesitan todo el contexto
        """
        sections = [
            self.system.build(),
            self.conversation.build(),
            f"# CONSULTA\n{user_query}"
        ]
        
        return "\n\n".join(sections)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Resumen del estado de todos los contextos"""
        return {
            'system_rules': len(self.system.rules),
            'conversation_turns': len(self.conversation.history) // 2,
            'project_loaded': bool(self.project.project_path),
            'files_in_context': len(self.files.recent_files),
            'memory_patterns': len(self.memory.relevant_patterns),
            'execution_step': f"{self.execution.current_step}/{self.execution.total_steps}"
        }
    
    def reset_conversation(self):
        """Reinicia solo el contexto conversacional"""
        self.conversation.clear()
        logger.info("Conversation context reset")
    
    def reset_all(self):
        """Reinicia todos los contextos excepto system"""
        self.conversation.clear()
        self.project = ProjectContext()
        self.files = FileContext()
        self.memory = MemoryContext()
        self.execution = ExecutionContext()
        logger.info("All contexts reset (except system)")


# Singleton global
_context_manager = None


def get_context_manager() -> ContextManager:
    """Obtiene instancia singleton del ContextManager"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
