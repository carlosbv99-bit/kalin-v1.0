"""
Event Bus Interno
Sistema de eventos desacoplado para comunicación entre módulos

Reemplaza llamadas directas entre módulos por un sistema de eventos pub/sub.

Ventajas:
- Desacoplamiento total entre módulos
- Fácil agregar nuevos listeners sin modificar emisores
- Debugging centralizado de flujo de eventos
- Escalabilidad a múltiples agentes
"""

import time
import traceback
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime
from agent.core.logger import get_logger

logger = get_logger('kalin.event_bus')


class Event:
    """Representa un evento en el sistema"""
    
    def __init__(
        self,
        name: str,
        data: Dict[str, Any] = None,
        source: str = "system",
        timestamp: float = None
    ):
        self.name = name
        self.data = data or {}
        self.source = source
        self.timestamp = timestamp or time.time()
        self.id = f"{name}_{self.timestamp}_{id(self)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para logging/serialización"""
        return {
            'id': self.id,
            'name': self.name,
            'data': self.data,
            'source': self.source,
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat()
        }
    
    def __repr__(self):
        return f"Event(name='{self.name}', source='{self.source}')"


class EventHandler:
    """Wrapper para handlers de eventos con metadata"""
    
    def __init__(
        self,
        handler: Callable,
        priority: int = 0,
        once: bool = False,
        description: str = ""
    ):
        self.handler = handler
        self.priority = priority  # Mayor prioridad se ejecuta primero
        self.once = once  # Ejecutar solo una vez
        self.description = description
        self.call_count = 0
        self.last_called: Optional[float] = None
        self.total_execution_time = 0.0
    
    def execute(self, event: Event) -> Any:
        """Ejecuta el handler con manejo de errores"""
        start_time = time.time()
        
        try:
            result = self.handler(event)
            
            # Actualizar estadísticas
            self.call_count += 1
            self.last_called = time.time()
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            
            logger.debug(f"Handler executed: {self.description or self.handler.__name__} ({execution_time:.3f}s)")
            
            return result
        
        except Exception as e:
            logger.error(f"Handler error in {self.description or self.handler.__name__}: {e}")
            logger.debug(traceback.format_exc())
            return None
    
    @property
    def avg_execution_time(self) -> float:
        """Tiempo promedio de ejecución"""
        if self.call_count == 0:
            return 0.0
        return self.total_execution_time / self.call_count


class EventBus:
    """
    Event Bus centralizado para comunicación desacoplada
    
    Uso:
        bus = EventBus()
        
        # Suscribirse a evento
        bus.on('file.changed', handle_file_change)
        
        # Emitir evento
        bus.emit('file.changed', {'path': 'main.py', 'action': 'modified'})
        
        # Suscribirse una sola vez
        bus.once('project.loaded', handle_initial_load)
    """
    
    def __init__(self):
        self.listeners: Dict[str, List[EventHandler]] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000
        
        # Estadísticas globales
        self.stats = {
            'total_events': 0,
            'total_listeners': 0,
            'errors': 0
        }
        
        logger.info("EventBus initialized")
    
    def on(self, event_name: str, handler: Callable, priority: int = 0, description: str = ""):
        """
        Suscribe un handler a un evento
        
        Args:
            event_name: Nombre del evento (soporta wildcards: 'file.*')
            handler: Función a ejecutar
            priority: Prioridad (mayor = primero)
            description: Descripción del handler
        """
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        
        event_handler = EventHandler(
            handler=handler,
            priority=priority,
            once=False,
            description=description
        )
        
        self.listeners[event_name].append(event_handler)
        
        # Ordenar por prioridad (descendente)
        self.listeners[event_name].sort(key=lambda h: h.priority, reverse=True)
        
        self.stats['total_listeners'] += 1
        
        logger.debug(f"Listener registered: {event_name} -> {description or handler.__name__}")
    
    def once(self, event_name: str, handler: Callable, priority: int = 0, description: str = ""):
        """Suscribe un handler que se ejecutará solo una vez"""
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        
        event_handler = EventHandler(
            handler=handler,
            priority=priority,
            once=True,
            description=description
        )
        
        self.listeners[event_name].append(event_handler)
        self.listeners[event_name].sort(key=lambda h: h.priority, reverse=True)
        
        self.stats['total_listeners'] += 1
    
    def off(self, event_name: str, handler: Callable = None):
        """
        Remueve listeners
        
        Args:
            event_name: Nombre del evento
            handler: Handler específico (None = remover todos)
        """
        if event_name not in self.listeners:
            return
        
        if handler:
            # Remover handler específico
            self.listeners[event_name] = [
                h for h in self.listeners[event_name]
                if h.handler != handler
            ]
        else:
            # Remover todos los handlers
            removed = len(self.listeners[event_name])
            self.listeners[event_name] = []
            self.stats['total_listeners'] -= removed
        
        logger.debug(f"Listener(s) removed: {event_name}")
    
    def emit(self, event_name: str, data: Dict[str, Any] = None, source: str = "system") -> List[Any]:
        """
        Emite un evento a todos los listeners
        
        Args:
            event_name: Nombre del evento
            data: Datos del evento
            source: Fuente del evento
        
        Returns:
            Lista de resultados de los handlers
        """
        event = Event(name=event_name, data=data, source=source)
        
        # Registrar en historial
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        self.stats['total_events'] += 1
        
        logger.debug(f"Event emitted: {event}")
        
        # Encontrar listeners relevantes (incluye wildcards)
        relevant_handlers = self._get_relevant_handlers(event_name)
        
        if not relevant_handlers:
            logger.debug(f"No listeners for event: {event_name}")
            return []
        
        # Ejecutar handlers
        results = []
        for handler_wrapper in relevant_handlers:
            result = handler_wrapper.execute(event)
            results.append(result)
            
            # Remover handlers 'once' después de ejecutar
            if handler_wrapper.once:
                self._remove_handler(event_name, handler_wrapper)
        
        return results
    
    def emit_sync(self, event_name: str, data: Dict[str, Any] = None, source: str = "system"):
        """Alias para emit (compatibilidad)"""
        return self.emit(event_name, data, source)
    
    def _get_relevant_handlers(self, event_name: str) -> List[EventHandler]:
        """Obtiene handlers relevantes incluyendo wildcards"""
        handlers = []
        
        # Handlers exactos
        if event_name in self.listeners:
            handlers.extend(self.listeners[event_name])
        
        # Handlers con wildcard (ej: 'file.*' matchea 'file.changed')
        for pattern, pattern_handlers in self.listeners.items():
            if '*' in pattern:
                # Convertir patrón a regex simple
                regex_pattern = pattern.replace('*', '.*')
                import re
                if re.match(f"^{regex_pattern}$", event_name):
                    handlers.extend(pattern_handlers)
        
        # Ordenar por prioridad
        handlers.sort(key=lambda h: h.priority, reverse=True)
        
        return handlers
    
    def _remove_handler(self, event_name: str, handler_wrapper: EventHandler):
        """Remueve un handler específico"""
        if event_name in self.listeners:
            self.listeners[event_name] = [
                h for h in self.listeners[event_name]
                if h != handler_wrapper
            ]
    
    def get_event_history(self, limit: int = None, event_name: str = None) -> List[Dict]:
        """
        Obtiene historial de eventos
        
        Args:
            limit: Límite de eventos
            event_name: Filtrar por nombre
        
        Returns:
            Lista de eventos en formato dict
        """
        history = self.event_history
        
        if event_name:
            history = [e for e in history if e.name == event_name]
        
        if limit:
            history = history[-limit:]
        
        return [e.to_dict() for e in history]
    
    def clear_history(self):
        """Limpia el historial de eventos"""
        self.event_history = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del event bus"""
        return {
            **self.stats,
            'registered_events': len(self.listeners),
            'events_in_history': len(self.event_history),
            'listener_details': {
                event_name: len(handlers)
                for event_name, handlers in self.listeners.items()
            }
        }
    
    def reset(self):
        """Reinicia el event bus"""
        self.listeners.clear()
        self.event_history.clear()
        self.stats = {
            'total_events': 0,
            'total_listeners': 0,
            'errors': 0
        }
        logger.info("EventBus reset")


# Singleton global
_event_bus = None


def get_event_bus() -> EventBus:
    """Obtiene instancia singleton del EventBus"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


# ====================
# EVENTOS PREDEFINIDOS
# ====================

# Eventos del sistema
EVENT_SYSTEM_START = "system.start"
EVENT_SYSTEM_STOP = "system.stop"
EVENT_SYSTEM_ERROR = "system.error"

# Eventos de proyecto
EVENT_PROJECT_LOADED = "project.loaded"
EVENT_PROJECT_SCANNED = "project.scanned"
EVENT_PROJECT_CHANGED = "project.changed"

# Eventos de archivos
EVENT_FILE_CREATED = "file.created"
EVENT_FILE_MODIFIED = "file.modified"
EVENT_FILE_DELETED = "file.deleted"
EVENT_FILE_READ = "file.read"

# Eventos de patching
EVENT_PATCH_CREATED = "patch.created"
EVENT_PATCH_APPLIED = "patch.applied"
EVENT_PATCH_UNDONE = "patch.undone"

# Eventos de LLM
EVENT_LLM_REQUEST = "llm.request"
EVENT_LLM_RESPONSE = "llm.response"
EVENT_LLM_ERROR = "llm.error"

# Eventos de herramientas
EVENT_TOOL_EXECUTED = "tool.executed"
EVENT_TOOL_ERROR = "tool.error"

# Eventos de contexto
EVENT_CONTEXT_UPDATED = "context.updated"
EVENT_MEMORY_STORED = "memory.stored"

# Eventos de tareas
EVENT_TASK_CREATED = "task.created"
EVENT_TASK_UPDATED = "task.updated"
EVENT_TASK_COMPLETED = "task.completed"
