"""
Memory Manager Centralizado
Gestiona memoria para múltiples agentes, sesiones y contextos
Reemplaza: agent.memory.append(message)
Por: memory_manager.store(session_id, message, metadata)
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from agent.core.logger import get_logger

logger = get_logger('kalin.memory_manager')


class MemoryStore:
    """Almacenamiento de memoria para una sesión específica"""
    
    def __init__(self, session_id: str, storage_dir: str):
        self.session_id = session_id
        self.storage_dir = storage_dir
        self.messages = []
        self.metadata = {}
        self.file_path = os.path.join(storage_dir, f"{session_id}.json")
        
        # Cargar si existe
        self._load()
    
    def _load(self):
        """Carga memoria desde disco"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.messages = data.get('messages', [])
                    self.metadata = data.get('metadata', {})
                logger.debug(f"Loaded memory for session {self.session_id}: {len(self.messages)} messages")
            except Exception as e:
                logger.error(f"Error loading memory: {e}")
                self.messages = []
                self.metadata = {}
    
    def store(self, message: str, role: str = "user", metadata: Dict[str, Any] = None):
        """
        Almacena un mensaje en la memoria de la sesión
        
        Args:
            message: Contenido del mensaje
            role: Rol (user, assistant, system)
            metadata: Metadatos adicionales (intención, archivos, etc.)
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'message': message,
            'metadata': metadata or {}
        }
        
        self.messages.append(entry)
        logger.debug(f"Stored message in session {self.session_id}: {len(message)} chars")
    
    def get_history(self, limit: int = None) -> List[Dict]:
        """Obtiene historial de mensajes"""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def clear(self):
        """Limpia la memoria de la sesión"""
        self.messages = []
        self.metadata = {}
        self._save()
    
    def _save(self):
        """Guarda memoria en disco"""
        try:
            os.makedirs(self.storage_dir, exist_ok=True)
            data = {
                'session_id': self.session_id,
                'messages': self.messages,
                'metadata': self.metadata,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved memory for session {self.session_id}: {len(self.messages)} messages")
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas de la sesión"""
        return {
            'session_id': self.session_id,
            'total_messages': len(self.messages),
            'first_message': self.messages[0]['timestamp'] if self.messages else None,
            'last_message': self.messages[-1]['timestamp'] if self.messages else None,
            'file_size': os.path.getsize(self.file_path) if os.path.exists(self.file_path) else 0
        }


class MemoryManager:
    """
    Gestor centralizado de memoria para múltiples sesiones y agentes
    
    Uso:
        memory_manager = MemoryManager()
        memory_manager.store(session_id, message, metadata)
        history = memory_manager.get_history(session_id)
    """
    
    def __init__(self, storage_dir: str = None, max_sessions: int = 100):
        """
        Inicializa el gestor de memoria
        
        Args:
            storage_dir: Directorio para almacenar sesiones (default: sessions/)
            max_sessions: Máximo número de sesiones en memoria (LRU cache)
        """
        if storage_dir is None:
            storage_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'sessions'
            )
        
        self.storage_dir = storage_dir
        self.max_sessions = max_sessions
        self.sessions: Dict[str, MemoryStore] = {}
        self.access_order = []  # Para LRU eviction
        
        os.makedirs(storage_dir, exist_ok=True)
        logger.info(f"MemoryManager initialized: storage_dir={storage_dir}")
    
    def store(self, session_id: str, message: str, role: str = "user", metadata: Dict[str, Any] = None):
        """
        Almacena un mensaje en la sesión especificada
        
        Args:
            session_id: ID único de la sesión
            message: Contenido del mensaje
            role: Rol (user, assistant, system)
            metadata: Metadatos adicionales
        """
        # Obtener o crear sesión
        session = self._get_or_create_session(session_id)
        
        # Almacenar mensaje
        session.store(message, role, metadata)
        
        # Emitir evento
        from agent.core.event_bus import get_event_bus, EVENT_MEMORY_STORED
        event_bus = get_event_bus()
        event_bus.emit(EVENT_MEMORY_STORED, {
            'session_id': session_id,
            'role': role,
            'message_length': len(message)
        }, source='memory_manager')
        
        # Actualizar orden de acceso (LRU)
        self._update_access_order(session_id)
        
        # Auto-guardar cada 10 mensajes
        if len(session.messages) % 10 == 0:
            session._save()
    
    def get_history(self, session_id: str, limit: int = None) -> List[Dict]:
        """
        Obtiene historial de una sesión
        
        Args:
            session_id: ID de la sesión
            limit: Límite de mensajes (None = todos)
        
        Returns:
            Lista de mensajes
        """
        session = self._get_session(session_id)
        if not session:
            return []
        
        self._update_access_order(session_id)
        return session.get_history(limit)
    
    def get_context(self, session_id: str, window: int = 5) -> str:
        """
        Obtiene contexto conversacional formateado para LLM
        
        Args:
            session_id: ID de la sesión
            window: Número de intercambios recientes
        
        Returns:
            String formateado con contexto
        """
        history = self.get_history(session_id, limit=window * 2)
        
        context_lines = []
        for msg in history:
            role = msg['role']
            message = msg['message']
            context_lines.append(f"{role}: {message}")
        
        return "\n".join(context_lines)
    
    def clear_session(self, session_id: str):
        """Limpia una sesión específica"""
        session = self._get_session(session_id)
        if session:
            session.clear()
            logger.info(f"Cleared session {session_id}")
    
    def delete_session(self, session_id: str):
        """Elimina completamente una sesión"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if os.path.exists(session.file_path):
                os.remove(session.file_path)
            del self.sessions[session_id]
            if session_id in self.access_order:
                self.access_order.remove(session_id)
            logger.info(f"Deleted session {session_id}")
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Obtiene estadísticas de una sesión"""
        session = self._get_session(session_id)
        if not session:
            return {'error': 'Session not found'}
        
        return session.get_stats()
    
    def get_all_sessions(self) -> List[str]:
        """Lista todas las sesiones activas"""
        return list(self.sessions.keys())
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """
        Limpia sesiones antiguas
        
        Args:
            max_age_hours: Edad máxima en horas
        """
        current_time = time.time()
        sessions_to_delete = []
        
        for session_id, session in self.sessions.items():
            if os.path.exists(session.file_path):
                file_age = current_time - os.path.getmtime(session.file_path)
                age_hours = file_age / 3600
                
                if age_hours > max_age_hours:
                    sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            self.delete_session(session_id)
        
        if sessions_to_delete:
            logger.info(f"Cleaned up {len(sessions_to_delete)} old sessions")
    
    def _get_or_create_session(self, session_id: str) -> MemoryStore:
        """Obtiene o crea una sesión"""
        if session_id not in self.sessions:
            # Evict LRU si excede máximo
            if len(self.sessions) >= self.max_sessions:
                self._evict_lru()
            
            self.sessions[session_id] = MemoryStore(session_id, self.storage_dir)
            logger.debug(f"Created new session: {session_id}")
        
        return self.sessions[session_id]
    
    def _get_session(self, session_id: str) -> Optional[MemoryStore]:
        """Obtiene una sesión existente"""
        return self.sessions.get(session_id)
    
    def _update_access_order(self, session_id: str):
        """Actualiza orden de acceso para LRU"""
        if session_id in self.access_order:
            self.access_order.remove(session_id)
        self.access_order.append(session_id)
    
    def _evict_lru(self):
        """Evict least recently used session"""
        if self.access_order:
            oldest_session = self.access_order.pop(0)
            if oldest_session in self.sessions:
                # Guardar antes de eliminar de memoria
                self.sessions[oldest_session]._save()
                del self.sessions[oldest_session]
                logger.debug(f"Evicted LRU session: {oldest_session}")
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Estadísticas del gestor de memoria"""
        total_messages = sum(len(s.messages) for s in self.sessions.values())
        total_size = sum(
            os.path.getsize(s.file_path) if os.path.exists(s.file_path) else 0
            for s in self.sessions.values()
        )
        
        return {
            'active_sessions': len(self.sessions),
            'max_sessions': self.max_sessions,
            'total_messages': total_messages,
            'total_storage_bytes': total_size,
            'total_storage_mb': round(total_size / (1024 * 1024), 2)
        }


# Singleton global
_memory_manager = None


def get_memory_manager() -> MemoryManager:
    """Obtiene instancia singleton del MemoryManager"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
