"""
Conversation Manager para Kalin.
Gestiona historial de conversaciones, contexto persistente y memoria de tareas.
"""

import json
import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from agent.core.logger import get_logger

logger = get_logger('kalin.conversation')

@dataclass
class Message:
    """Representa un mensaje en la conversación"""
    role: str  # 'user' o 'assistant'
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        return cls(**data)

@dataclass
class TaskContext:
    """Contexto de una tarea en progreso"""
    task_id: str
    task_type: str  # 'fix', 'create', 'analyze', etc.
    status: str = 'pending'  # 'pending', 'in_progress', 'completed', 'failed'
    file_path: Optional[str] = None
    original_code: Optional[str] = None
    modified_code: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TaskContext':
        return cls(**data)

class ConversationManager:
    """Gestiona el estado conversacional del agente"""
    
    def __init__(self, session_id: Optional[str] = None, storage_dir: Optional[str] = None):
        self.session_id = session_id or f"session_{int(time.time())}"
        
        if storage_dir is None:
            storage_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'sessions'
            )
        
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.session_file = os.path.join(self.storage_dir, f"{self.session_id}.json")
        
        # Estado en memoria
        self.messages: List[Message] = []
        self.task_contexts: Dict[str, TaskContext] = {}
        self.variables: Dict[str, Any] = {}  # Variables de contexto
        self.metadata: Dict[str, Any] = {
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'message_count': 0
        }
        
        # DESACTIVADO: No cargar sesión anterior para evitar procesar historial antiguo
        # self._load_session()
        
        logger.info(f"ConversationManager initialized: session={self.session_id}")
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None) -> Message:
        """Agrega un mensaje a la conversación"""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        self.messages.append(message)
        self.metadata['message_count'] = len(self.messages)
        self.metadata['last_activity'] = datetime.now().isoformat()
        
        logger.debug(f"Message added: role={role}, length={len(content)}")
        
        # Auto-guardar cada 10 mensajes
        if len(self.messages) % 10 == 0:
            self.save()
        
        return message
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Obtiene los últimos N mensajes"""
        return self.messages[-limit:] if limit > 0 else self.messages
    
    def get_conversation_history(self, max_messages: int = 50) -> List[Dict]:
        """Obtiene historial completo para contexto LLM"""
        recent = self.get_recent_messages(max_messages)
        return [msg.to_dict() for msg in recent]
    
    def create_task(self, task_type: str, file_path: str = None, metadata: Dict = None) -> str:
        """Crea un nuevo contexto de tarea"""
        import uuid
        task_id = str(uuid.uuid4())[:8]
        
        task = TaskContext(
            task_id=task_id,
            task_type=task_type,
            file_path=file_path,
            metadata=metadata or {}
        )
        
        self.task_contexts[task_id] = task
        self.variables['current_task'] = task_id
        
        logger.info(f"Task created: id={task_id}, type={task_type}")
        
        return task_id
    
    def update_task(self, task_id: str, **kwargs) -> Optional[TaskContext]:
        """Actualiza el estado de una tarea"""
        if task_id not in self.task_contexts:
            logger.warning(f"Task not found: {task_id}")
            return None
        
        task = self.task_contexts[task_id]
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = time.time()
        
        if 'status' in kwargs:
            logger.info(f"Task updated: id={task_id}, status={kwargs['status']}")
        
        return task
    
    def get_task(self, task_id: str) -> Optional[TaskContext]:
        """Obtiene una tarea por ID"""
        return self.task_contexts.get(task_id)
    
    def get_current_task(self) -> Optional[TaskContext]:
        """Obtiene la tarea activa actual"""
        current_task_id = self.variables.get('current_task')
        if current_task_id:
            return self.task_contexts.get(current_task_id)
        return None
    
    def set_variable(self, key: str, value: Any):
        """Establece una variable de contexto"""
        self.variables[key] = value
        logger.debug(f"Variable set: {key}={value}")
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Obtiene una variable de contexto"""
        return self.variables.get(key, default)
    
    def get_context_for_llm(self) -> Dict:
        """Genera contexto completo para enviar al LLM"""
        current_task = self.get_current_task()
        
        context = {
            'session_id': self.session_id,
            'message_count': len(self.messages),
            'recent_messages': self.get_conversation_history(20),
            'current_task': current_task.to_dict() if current_task else None,
            'variables': self.variables,
            'metadata': self.metadata
        }
        
        return context
    
    def save(self):
        """Guarda la sesión en disco"""
        try:
            session_data = {
                'session_id': self.session_id,
                'messages': [msg.to_dict() for msg in self.messages],
                'task_contexts': {k: v.to_dict() for k, v in self.task_contexts.items()},
                'variables': self.variables,
                'metadata': self.metadata
            }
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Session saved: {self.session_file}")
            
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def _load_session(self):
        """Carga una sesión previa desde disco"""
        if not os.path.exists(self.session_file):
            logger.info(f"No previous session found: {self.session_id}")
            return
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.messages = [Message.from_dict(m) for m in session_data.get('messages', [])]
            self.task_contexts = {
                k: TaskContext.from_dict(v) 
                for k, v in session_data.get('task_contexts', {}).items()
            }
            self.variables = session_data.get('variables', {})
            self.metadata = session_data.get('metadata', {})
            
            logger.info(f"Session loaded: {len(self.messages)} messages, {len(self.task_contexts)} tasks")
            
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
    
    def clear(self):
        """Limpia la sesión actual"""
        self.messages.clear()
        self.task_contexts.clear()
        self.variables.clear()
        self.metadata['message_count'] = 0
        self.metadata['last_activity'] = datetime.now().isoformat()
        
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
        
        logger.info(f"Session cleared: {self.session_id}")
    
    def get_summary(self) -> Dict:
        """Obtiene resumen de la sesión"""
        return {
            'session_id': self.session_id,
            'message_count': len(self.messages),
            'active_tasks': len([t for t in self.task_contexts.values() if t.status == 'in_progress']),
            'completed_tasks': len([t for t in self.task_contexts.values() if t.status == 'completed']),
            'variables_count': len(self.variables),
            'last_activity': self.metadata.get('last_activity')
        }
