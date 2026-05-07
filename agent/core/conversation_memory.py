# agent/core/conversation_memory.py
"""
Sistema de Memoria Conversacional Avanzado para Kalin

Integra gestión de contexto conversacional con:
- Historial persistente de conversaciones
- Contexto de archivos (analizados, modificados, creados)
- Inferencia inteligente de referencias implícitas
- Gestión de estado por sesión
- Integración con Experience Memory
- Persistencia automática en disco
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import os
import hashlib
from agent.core.logger import get_logger

logger = get_logger('kalin.conversation_memory')


class ConversationMemory:
    """
    Gestiona la memoria conversacional avanzada de Kalin
    
    Características:
    - Seguimiento de contexto de archivos y proyectos
    - Historial conversacional con límites configurables
    - Inferencia inteligente de referencias implícitas
    - Integración con prompts dinámicos
    - Persistencia automática entre sesiones
    - Métricas de uso y patrones conversacionales
    """
    
    def __init__(self, max_history=20, session_id=None, storage_dir=None):
        self.max_history = max_history
        self.session_id = session_id or f"session_{int(datetime.now().timestamp())}"
        
        # Configurar directorio de almacenamiento
        if storage_dir is None:
            storage_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'sessions'
            )
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Estado de la memoria
        self.current_context = {}
        self.conversation_history = []
        self.file_context = {}  # Contexto por archivo
        self.project_context = {}  # Contexto del proyecto actual
        self.user_preferences = {}  # Preferencias detectadas del usuario
        
        # Métricas conversacionales
        self.metrics = {
            'total_interactions': 0,
            'intention_counts': {},
            'most_used_files': [],
            'average_response_time': 0.0,
            'session_start': datetime.now().isoformat()
        }
        
        # Cargar memoria previa si existe
        self._load_session()
        
        logger.info(f"ConversationMemory initialized: session={self.session_id}")
        
    def update_context(self, intention: str, args: Dict[str, Any], result: Any = None, metadata: Dict[str, Any] = None):
        """
        Actualiza el contexto basado en la acción ejecutada
        
        Args:
            intention: Intención ejecutada (analyze, fix, create, etc.)
            args: Argumentos de la acción
            result: Resultado de la acción (opcional)
            metadata: Metadatos adicionales (tiempo, tokens, etc.)
        """
        timestamp = datetime.now().isoformat()
        
        # Guardar en historial con metadatos completos
        entry = {
            "timestamp": timestamp,
            "intention": intention,
            "args": args,
            "result_summary": self._summarize_result(result) if result else None,
            "metadata": metadata or {},
            "context_snapshot": self._get_context_snapshot()
        }
        
        self.conversation_history.append(entry)
        
        # Limitar historial al tamaño máximo
        if len(self.conversation_history) > self.max_history:
            removed = self.conversation_history[:-self.max_history]
            self.conversation_history = self.conversation_history[-self.max_history:]
            logger.debug(f"History trimmed: removed {len(removed)} entries")
        
        # Actualizar métricas
        self._update_metrics(intention, args)
        
        # Actualizar contexto específico según intención
        if intention == "analyze":
            self._update_analyze_context(args, result)
        elif intention == "fix":
            self._update_fix_context(args, result)
        elif intention == "create":
            self._update_create_context(args, result)
        elif intention == "scan":
            self._update_scan_context(args, result)
        elif intention == "setpath":
            self._update_project_context(args, result)
        
        # Actualizar contexto general
        self.current_context.update({
            "last_intention": intention,
            "last_timestamp": timestamp,
            "last_args": args,
            "interaction_count": self.metrics['total_interactions']
        })
        
        # Auto-guardar cada 5 interacciones
        if self.metrics['total_interactions'] % 5 == 0:
            self.save_to_file()
    
    def _update_analyze_context(self, args: Dict, result: Any):
        """Actualiza contexto después de analizar un archivo"""
        file_path = args.get("arg")
        if file_path:
            # Normalizar ruta
            file_key = os.path.basename(file_path)
            
            self.file_context["last_analyzed_file"] = file_path
            self.file_context["last_analyzed_time"] = datetime.now().isoformat()
            
            # Registrar en archivos más usados
            self._track_file_usage(file_path, "analyzed")
            
            # Extraer información relevante del resultado si es posible
            if result and isinstance(result, dict):
                self.file_context["last_analysis_summary"] = self._summarize_result(result)
            elif result and isinstance(result, str):
                # Detectar problemas mencionados en el análisis
                problems = self._extract_problems_from_text(result)
                if problems:
                    self.file_context["last_analysis_problems"] = problems
    
    def _update_fix_context(self, args: Dict, result: Any):
        """Actualiza contexto después de corregir un archivo"""
        file_path = args.get("arg")
        if file_path:
            file_key = os.path.basename(file_path)
            
            self.file_context["last_fixed_file"] = file_path
            self.file_context["last_fixed_time"] = datetime.now().isoformat()
            
            # Registrar en archivos más usados
            self._track_file_usage(file_path, "fixed")
            
            # Si el fix fue exitoso, guardar patrón
            if result and isinstance(result, str):
                success_indicators = ["corregido", "fixed", "resuelto", "solucionado"]
                if any(indicator in result.lower() for indicator in success_indicators):
                    self.file_context["last_successful_fix"] = {
                        "file": file_path,
                        "time": datetime.now().isoformat(),
                        "summary": self._summarize_result(result)
                    }
    
    def _update_create_context(self, args: Dict, result: Any):
        """Actualiza contexto después de crear un archivo o código"""
        file_path = args.get("file_path") or args.get("arg")
        if file_path:
            self.file_context["last_created_file"] = file_path
            self.file_context["last_created_time"] = datetime.now().isoformat()
            self._track_file_usage(file_path, "created")
            
            # Guardar tipo de archivo creado
            ext = os.path.splitext(file_path)[1].lower()
            if ext:
                self.current_context["last_created_type"] = ext
    
    def _update_scan_context(self, args: Dict, result: Any):
        """Actualiza contexto después de escanear proyecto"""
        if result and isinstance(result, dict):
            self.project_context["last_scan_result"] = {
                "total_archivos": result.get("total_archivos", 0),
                "tipo_principal": result.get("tipo_principal", "unknown"),
                "lenguajes_detectados": result.get("lenguajes", []),
                "timestamp": datetime.now().isoformat()
            }
    
    def _update_project_context(self, args: Dict, result: Any):
        """Actualiza contexto del proyecto actual"""
        project_path = args.get("arg") or args.get("path")
        if project_path:
            self.project_context["current_project_path"] = project_path
            self.project_context["project_set_time"] = datetime.now().isoformat()
            
            # Detectar tipo de proyecto
            project_type = self._detect_project_type(project_path)
            if project_type:
                self.project_context["project_type"] = project_type
                logger.info(f"Project type detected: {project_type}")
    
    def get_last_analyzed_file(self) -> Optional[str]:
        """Obtiene el último archivo analizado"""
        return self.file_context.get("last_analyzed_file")
    
    def get_last_fixed_file(self) -> Optional[str]:
        """Obtiene el último archivo corregido"""
        return self.file_context.get("last_fixed_file")
    
    def get_recent_files(self, limit=3) -> List[str]:
        """Obtiene los archivos mencionados recientemente"""
        files = []
        
        # Buscar en historial reciente
        for entry in reversed(self.conversation_history[-limit:]):
            args = entry.get("args", {})
            if "arg" in args and args["arg"]:
                files.append(args["arg"])
        
        return list(dict.fromkeys(files))  # Eliminar duplicados manteniendo orden
    
    def infer_missing_context(self, mensaje: str, detected_intention: str, args: Dict) -> Dict:
        """
        Infiere contexto faltante basado en conversación previa
        
        Esta función es CRÍTICA para permitir conversaciones naturales donde
        el usuario hace referencias implícitas a archivos o acciones anteriores.
        
        Args:
            mensaje: Mensaje original del usuario
            detected_intention: Intención detectada
            args: Argumentos extraídos
        
        Returns:
            Argumentos mejorados con contexto inferido
        """
        improved_args = args.copy()
        mensaje_lower = mensaje.lower()
        
        # CASO 1: Intención requiere archivo pero no se especificó
        if detected_intention in ["fix", "analyze", "refactor", "enhance"] and not improved_args.get("arg"):
            # Prioridad 1: Usar último archivo mencionado en el mensaje
            mentioned_file = self._extract_file_from_message(mensaje)
            if mentioned_file:
                improved_args["arg"] = mentioned_file
                improved_args["inferred_from_message"] = True
                logger.info(f"Inferred file from message: {mentioned_file}")
            else:
                # Prioridad 2: Usar último archivo analizado/corregido
                last_file = self.get_last_analyzed_file() or self.get_last_fixed_file()
                if last_file:
                    improved_args["arg"] = last_file
                    improved_args["inferred_from_context"] = True
                    logger.info(f"Inferred file from context: {last_file}")
        
        # CASO 2: Detectar referencias implícitas
        implicit_references = [
            "el archivo", "ese archivo", "este archivo",
            "el código", "ese código", "este código",
            "lo anterior", "lo de antes", "el anterior",
            "las dependencias", "los errores", "los problemas",
            "arréglalo", "corrígelo", "analízalo", "revísalo"
        ]
        
        if any(ref in mensaje_lower for ref in implicit_references):
            last_file = self.get_last_analyzed_file() or self.get_last_fixed_file()
            if last_file and not improved_args.get("arg"):
                improved_args["arg"] = last_file
                improved_args["inferred_from_reference"] = True
                logger.info(f"Inferred file from reference: {last_file}")
        
        # CASO 3: Referencias a proyecto
        project_references = ["mi proyecto", "el proyecto", "este proyecto"]
        if any(ref in mensaje_lower for ref in project_references):
            current_project = self.project_context.get("current_project_path")
            if current_project:
                improved_args["project_path"] = current_project
                improved_args["inferred_project"] = True
        
        return improved_args
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen completo del estado conversacional actual"""
        return {
            "session_id": self.session_id,
            "current_context": self.current_context,
            "file_context": self.file_context,
            "project_context": self.project_context,
            "recent_history_count": len(self.conversation_history),
            "total_interactions": self.metrics['total_interactions'],
            "last_interaction": self.conversation_history[-1] if self.conversation_history else None,
            "metrics": self.metrics
        }
    
    def clear_history(self):
        """Limpia el historial conversacional pero mantiene preferencias"""
        self.conversation_history.clear()
        self.current_context.clear()
        self.file_context.clear()
        self.project_context.clear()
        # Mantener user_preferences y métricas básicas
        self.metrics = {
            'total_interactions': 0,
            'intention_counts': {},
            'most_used_files': [],
            'average_response_time': 0.0,
            'session_start': datetime.now().isoformat()
        }
        logger.info("Conversation history cleared")
    
    def save_to_file(self, filepath: str = None):
        """Guarda la memoria completa en disco"""
        if filepath is None:
            filepath = os.path.join(self.storage_dir, f"{self.session_id}.json")
        
        try:
            data = {
                "session_id": self.session_id,
                "current_context": self.current_context,
                "file_context": self.file_context,
                "project_context": self.project_context,
                "user_preferences": self.user_preferences,
                "conversation_history": self.conversation_history,
                "metrics": self.metrics,
                "saved_at": datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Memory saved to {filepath}")
                
        except Exception as e:
            logger.error(f"Error saving conversation memory: {e}")
    
    def load_from_file(self, filepath: str = None) -> bool:
        """Carga la memoria desde disco"""
        if filepath is None:
            filepath = os.path.join(self.storage_dir, f"{self.session_id}.json")
        
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.session_id = data.get("session_id", self.session_id)
                self.current_context = data.get("current_context", {})
                self.file_context = data.get("file_context", {})
                self.project_context = data.get("project_context", {})
                self.user_preferences = data.get("user_preferences", {})
                self.conversation_history = data.get("conversation_history", [])
                self.metrics = data.get("metrics", self.metrics)
                
                logger.info(f"Memory loaded from {filepath}: {len(self.conversation_history)} entries")
                return True
            else:
                logger.info(f"No previous session found at {filepath}")
        except Exception as e:
            logger.error(f"Error loading conversation memory: {e}")
        
        return False
    
    def _load_session(self):
        """Carga automáticamente la sesión al inicializar"""
        filepath = os.path.join(self.storage_dir, f"{self.session_id}.json")
        self.load_from_file(filepath)
    
    def _summarize_result(self, result: Any) -> str:
        """Crea un resumen breve del resultado"""
        if isinstance(result, str):
            # Truncar strings largos
            return result[:200] + "..." if len(result) > 200 else result
        elif isinstance(result, dict):
            # Resumir diccionarios
            return f"Dict con {len(result)} claves"
        else:
            return str(result)[:100]
    
    def _update_metrics(self, intention: str, args: Dict[str, Any]):
        """Actualiza métricas conversacionales"""
        self.metrics['total_interactions'] += 1
        
        # Contar intenciones
        if intention not in self.metrics['intention_counts']:
            self.metrics['intention_counts'][intention] = 0
        self.metrics['intention_counts'][intention] += 1
    
    def _track_file_usage(self, file_path: str, action: str):
        """Rastrea uso de archivos para detectar patrones"""
        file_key = os.path.basename(file_path)
        
        # Actualizar lista de archivos más usados
        for entry in self.metrics['most_used_files']:
            if entry['file'] == file_key:
                entry['count'] += 1
                entry['last_action'] = action
                entry['last_time'] = datetime.now().isoformat()
                return
        
        # Si no existe, agregar nuevo
        if len(self.metrics['most_used_files']) < 20:  # Mantener top 20
            self.metrics['most_used_files'].append({
                'file': file_key,
                'path': file_path,
                'count': 1,
                'last_action': action,
                'last_time': datetime.now().isoformat()
            })
    
    def _extract_problems_from_text(self, text: str) -> List[str]:
        """Extrae problemas mencionados en texto de análisis"""
        problems = []
        problem_keywords = [
            'error', 'bug', 'problema', 'fallo', 'issue',
            'warning', 'advertencia', 'deprecated'
        ]
        
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in problem_keywords):
                problems.append(line.strip())
        
        return problems[:5]  # Máximo 5 problemas
    
    def _extract_file_from_message(self, message: str) -> Optional[str]:
        """Extrae nombre de archivo mencionado en mensaje"""
        import re
        
        # Patrones comunes de archivos
        patterns = [
            r'([\w-]+\.py)',      # Python
            r'([\w-]+\.java)',    # Java
            r'([\w-]+\.dart)',    # Dart/Flutter
            r'([\w-]+\.js)',      # JavaScript
            r'([\w-]+\.ts)',      # TypeScript
            r'([\w-]+\.html)',    # HTML
            r'([\w-]+\.css)',     # CSS
            r'([\w-]+\.json)',    # JSON
            r'([\w-]+\.yaml)',    # YAML
            r'([\w-]+\.yml)',     # YML
            r'([\w-]+\.xml)',     # XML
            r'([\w-]+\.txt)',     # TXT
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _detect_project_type(self, project_path: str) -> Optional[str]:
        """Detecta tipo de proyecto basado en archivos presentes"""
        if not os.path.exists(project_path):
            return None
        
        # Indicadores de tipo de proyecto
        indicators = {
            'flutter': ['pubspec.yaml', 'lib/main.dart'],
            'android': ['build.gradle', 'AndroidManifest.xml'],
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml'],
            'nodejs': ['package.json', 'node_modules'],
            'react': ['package.json', 'src/App.js', 'src/App.jsx'],
            'vue': ['package.json', 'vue.config.js'],
            'django': ['manage.py', 'settings.py'],
            'flask': ['app.py', 'flask_app.py'],
        }
        
        for project_type, files in indicators.items():
            for file_indicator in files:
                full_path = os.path.join(project_path, file_indicator)
                if os.path.exists(full_path):
                    return project_type
        
        return 'generic'
    
    def _get_context_snapshot(self) -> Dict[str, Any]:
        """Captura snapshot del contexto actual para historial"""
        return {
            'current_file': self.file_context.get('last_analyzed_file'),
            'project_type': self.project_context.get('project_type'),
            'interaction_count': self.metrics['total_interactions']
        }


# Instancia global singleton
conversation_memory = ConversationMemory()
