"""
Task Identity System
Sistema de identidad para tareas con tracking completo

Cada acción recibe identificadores únicos para:
- Trazabilidad completa
- Debugging preciso
- Escalabilidad multi-agente futura
- Auditoría y métricas
"""

import uuid
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from agent.core.logger import get_logger

logger = get_logger('kalin.task_identity')


class TaskIdentity:
    """
    Identidad única de una tarea
    
    Estructura:
    {
        "task_id": "uuid",           # ID único de la tarea
        "session_id": "uuid",        # ID de sesión del usuario
        "agent_id": "agent_name",    # ID del agente ejecutor
        "timestamp": float,          # Timestamp de creación
        "context": {}                # Contexto adicional
    }
    """
    
    def __init__(
        self,
        task_id: str = None,
        session_id: str = None,
        agent_id: str = "kalin_main",
        timestamp: float = None,
        context: Dict[str, Any] = None
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.session_id = session_id or f"session_{int(time.time())}"
        self.agent_id = agent_id
        self.timestamp = timestamp or time.time()
        self.context = context or {}
        
        # Metadata automática
        self.created_at = datetime.fromtimestamp(self.timestamp).isoformat()
        self.status = "pending"  # pending, running, completed, failed
        self.duration: Optional[float] = None
        self.error: Optional[str] = None
    
    def start(self):
        """Marca la tarea como iniciada"""
        self.status = "running"
        self.start_time = time.time()
        logger.debug(f"Task started: {self.task_id}")
    
    def complete(self, duration: float = None):
        """Marca la tarea como completada"""
        self.status = "completed"
        self.duration = duration or (time.time() - self.start_time if hasattr(self, 'start_time') else 0)
        logger.debug(f"Task completed: {self.task_id} ({self.duration:.3f}s)")
    
    def fail(self, error: str, duration: float = None):
        """Marca la tarea como fallida"""
        self.status = "failed"
        self.error = error
        self.duration = duration or (time.time() - self.start_time if hasattr(self, 'start_time') else 0)
        logger.error(f"Task failed: {self.task_id} - {error}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'task_id': self.task_id,
            'session_id': self.session_id,
            'agent_id': self.agent_id,
            'timestamp': self.timestamp,
            'created_at': self.created_at,
            'status': self.status,
            'duration': self.duration,
            'error': self.error,
            'context': self.context
        }
    
    def to_log_string(self) -> str:
        """Formato para logging"""
        return f"[Task:{self.task_id[:8]}] [Session:{self.session_id[:8]}] [Agent:{self.agent_id}]"
    
    def __repr__(self):
        return f"TaskIdentity(task_id={self.task_id[:8]}, status={self.status})"


class TaskManager:
    """
    Gestor de identidades de tareas
    
    Uso:
        task_mgr = TaskManager()
        task_id = task_mgr.create_task(session_id, agent_id)
        task_mgr.start_task(task_id)
        task_mgr.complete_task(task_id)
    """
    
    def __init__(self):
        self.tasks: Dict[str, TaskIdentity] = {}
        self.active_tasks: Dict[str, TaskIdentity] = {}
        self.completed_tasks: List[TaskIdentity] = []
        self.max_completed = 1000
        
        # Estadísticas
        self.stats = {
            'total_created': 0,
            'total_completed': 0,
            'total_failed': 0,
            'avg_duration': 0.0
        }
        
        logger.info("TaskManager initialized")
    
    def create_task(
        self,
        session_id: str,
        agent_id: str = "kalin_main",
        context: Dict[str, Any] = None
    ) -> str:
        """
        Crea una nueva tarea con identidad única
        
        Args:
            session_id: ID de sesión del usuario
            agent_id: ID del agente ejecutor
            context: Contexto adicional
        
        Returns:
            task_id único
        """
        task = TaskIdentity(
            session_id=session_id,
            agent_id=agent_id,
            context=context
        )
        
        self.tasks[task.task_id] = task
        self.active_tasks[task.task_id] = task
        self.stats['total_created'] += 1
        
        logger.info(f"Task created: {task.to_log_string()}")
        return task.task_id
    
    def start_task(self, task_id: str):
        """Inicia una tarea"""
        task = self.tasks.get(task_id)
        if task:
            task.start()
        else:
            logger.warning(f"Task not found: {task_id}")
    
    def complete_task(self, task_id: str, duration: float = None):
        """Completa una tarea exitosamente"""
        task = self.tasks.get(task_id)
        if task:
            task.complete(duration)
            
            # Mover a completadas
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            self.completed_tasks.append(task)
            self.stats['total_completed'] += 1
            
            # Limitar historial
            if len(self.completed_tasks) > self.max_completed:
                removed = self.completed_tasks[:-self.max_completed]
                self.completed_tasks = self.completed_tasks[-self.max_completed:]
                
                # Limpiar tasks dict también
                for old_task in removed:
                    if old_task.task_id in self.tasks:
                        del self.tasks[old_task.task_id]
            
            # Actualizar promedio
            self._update_avg_duration()
            
            logger.info(f"Task completed: {task.to_log_string()} ({task.duration:.3f}s)")
        else:
            logger.warning(f"Task not found: {task_id}")
    
    def fail_task(self, task_id: str, error: str, duration: float = None):
        """Marca una tarea como fallida"""
        task = self.tasks.get(task_id)
        if task:
            task.fail(error, duration)
            
            # Mover a completadas (aunque falló)
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            self.completed_tasks.append(task)
            self.stats['total_failed'] += 1
            
            logger.error(f"Task failed: {task.to_log_string()} - {error}")
        else:
            logger.warning(f"Task not found: {task_id}")
    
    def get_task(self, task_id: str) -> Optional[TaskIdentity]:
        """Obtiene una tarea por ID"""
        return self.tasks.get(task_id)
    
    def get_active_tasks(self, session_id: str = None) -> List[TaskIdentity]:
        """Obtiene tareas activas, opcionalmente filtradas por sesión"""
        if session_id:
            return [t for t in self.active_tasks.values() if t.session_id == session_id]
        return list(self.active_tasks.values())
    
    def get_session_tasks(self, session_id: str, limit: int = None) -> List[Dict]:
        """Obtiene todas las tareas de una sesión"""
        session_tasks = [
            t.to_dict() for t in self.tasks.values()
            if t.session_id == session_id
        ]
        
        if limit:
            session_tasks = session_tasks[-limit:]
        
        return session_tasks
    
    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del task manager"""
        return {
            **self.stats,
            'active_tasks': len(self.active_tasks),
            'total_tracked': len(self.tasks),
            'avg_duration': round(self.stats['avg_duration'], 3)
        }
    
    def _update_avg_duration(self):
        """Actualiza duración promedio"""
        completed_with_duration = [
            t for t in self.completed_tasks
            if t.duration is not None
        ]
        
        if completed_with_duration:
            total_duration = sum(t.duration for t in completed_with_duration)
            self.stats['avg_duration'] = total_duration / len(completed_with_duration)
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Limpia tareas antiguas"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            age = current_time - task.timestamp
            if age > max_age_seconds and task.status in ['completed', 'failed']:
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            if task_id in self.tasks:
                del self.tasks[task_id]
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
        
        if tasks_to_remove:
            logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")
    
    def reset(self):
        """Reinicia el task manager"""
        self.tasks.clear()
        self.active_tasks.clear()
        self.completed_tasks.clear()
        self.stats = {
            'total_created': 0,
            'total_completed': 0,
            'total_failed': 0,
            'avg_duration': 0.0
        }
        logger.info("TaskManager reset")


# Singleton global
_task_manager = None


def get_task_manager() -> TaskManager:
    """Obtiene instancia singleton del TaskManager"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager


def create_task_identity(
    session_id: str,
    agent_id: str = "kalin_main",
    context: Dict[str, Any] = None
) -> str:
    """Función helper para crear tarea rápidamente"""
    task_mgr = get_task_manager()
    return task_mgr.create_task(session_id, agent_id, context)
