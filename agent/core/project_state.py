"""
Project State Manager
Representación central del estado del proyecto para múltiples agentes

Todos los agentes (frontend, backend, QA) leen/escriben sobre el mismo estado.
No trabajan sobre texto suelto, sino sobre una estructura de datos compartida.
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from agent.core.logger import get_logger

logger = get_logger('kalin.project_state')


class ProjectState:
    """
    Estado centralizado del proyecto
    
    Estructura:
    {
        "files": [],           # Archivos del proyecto
        "dependencies": [],    # Dependencias detectadas
        "architecture": {},    # Arquitectura del proyecto
        "tasks": [],          # Tareas pendientes/completadas
        "history": []         # Historial de cambios
    }
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path or ""
        self.state = {
            'files': [],
            'dependencies': [],
            'architecture': {
                'type': 'unknown',
                'layers': [],
                'modules': [],
                'patterns': []
            },
            'tasks': [],
            'history': [],
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
        }
        
        # Si hay ruta, escanear automáticamente
        if self.project_path and os.path.exists(self.project_path):
            self.scan_project()
        
        logger.info(f"ProjectState initialized: {self.project_path}")
    
    def scan_project(self):
        """Escanea el proyecto y actualiza el estado"""
        if not self.project_path or not os.path.exists(self.project_path):
            logger.warning("Project path not set or doesn't exist")
            return
        
        logger.info(f"Scanning project: {self.project_path}")
        
        # Escanear archivos
        self._scan_files()
        
        # Detectar dependencias
        self._detect_dependencies()
        
        # Analizar arquitectura
        self._analyze_architecture()
        
        # Actualizar metadata
        self.state['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Emitir evento
        from agent.core.event_bus import get_event_bus, EVENT_PROJECT_SCANNED
        event_bus = get_event_bus()
        event_bus.emit(EVENT_PROJECT_SCANNED, {
            'project_path': self.project_path,
            'files_count': len(self.state['files']),
            'dependencies_count': len(self.state['dependencies'])
        }, source='project_state')
        
        logger.info(f"Project scanned: {len(self.state['files'])} files, {len(self.state['dependencies'])} dependencies")
    
    def _scan_files(self):
        """Escanea todos los archivos del proyecto"""
        files = []
        
        for root, dirs, filenames in os.walk(self.project_path):
            # Ignorar directorios ocultos y node_modules
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git']]
            
            for filename in filenames:
                if filename.startswith('.'):
                    continue
                
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, self.project_path)
                
                # Obtener información del archivo
                try:
                    stat = os.stat(filepath)
                    file_info = {
                        'path': rel_path,
                        'absolute_path': filepath,
                        'size': stat.st_size,
                        'extension': os.path.splitext(filename)[1].lower(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
                    }
                    
                    files.append(file_info)
                    
                except Exception as e:
                    logger.debug(f"Error scanning file {filepath}: {e}")
        
        self.state['files'] = files
    
    def _detect_dependencies(self):
        """Detecta dependencias del proyecto"""
        dependencies = []
        
        if not self.project_path:
            return
        
        # Python: requirements.txt
        req_file = os.path.join(self.project_path, 'requirements.txt')
        if os.path.exists(req_file):
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            pkg = line.split('==')[0].split('>=')[0].strip()
                            dependencies.append({
                                'name': pkg,
                                'source': 'requirements.txt',
                                'language': 'python'
                            })
            except Exception as e:
                logger.error(f"Error reading requirements.txt: {e}")
        
        # Node.js: package.json
        pkg_file = os.path.join(self.project_path, 'package.json')
        if os.path.exists(pkg_file):
            try:
                with open(pkg_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    
                    for pkg, version in deps.items():
                        dependencies.append({
                            'name': pkg,
                            'version': version,
                            'source': 'package.json',
                            'language': 'javascript',
                            'type': 'production'
                        })
                    
                    for pkg, version in dev_deps.items():
                        dependencies.append({
                            'name': pkg,
                            'version': version,
                            'source': 'package.json',
                            'language': 'javascript',
                            'type': 'development'
                        })
            except Exception as e:
                logger.error(f"Error reading package.json: {e}")
        
        self.state['dependencies'] = dependencies
    
    def _analyze_architecture(self):
        """Analiza la arquitectura del proyecto"""
        architecture = {
            'type': 'unknown',
            'layers': [],
            'modules': [],
            'patterns': []
        }
        
        if not self.project_path:
            self.state['architecture'] = architecture
            return
        
        # Detectar tipo de proyecto
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
                architecture['type'] = proj_type
                break
        
        # Detectar capas/arquitectura por estructura de directorios
        common_dirs = os.listdir(self.project_path)
        
        layer_mapping = {
            'src': 'source',
            'lib': 'library',
            'app': 'application',
            'core': 'core',
            'api': 'api',
            'web': 'web',
            'ui': 'ui',
            'models': 'data_models',
            'controllers': 'controllers',
            'services': 'services',
            'utils': 'utilities',
            'tests': 'tests',
            'docs': 'documentation'
        }
        
        for dir_name in common_dirs:
            if dir_name in layer_mapping:
                architecture['layers'].append(layer_mapping[dir_name])
        
        # Detectar patrones arquitectónicos
        if any(d in common_dirs for d in ['models', 'views', 'controllers']):
            architecture['patterns'].append('MVC')
        
        if any(d in common_dirs for d in ['components', 'pages', 'hooks']):
            architecture['patterns'].append('Component-based')
        
        if 'main.py' in common_dirs or 'index.js' in common_dirs:
            architecture['patterns'].append('Entry point pattern')
        
        self.state['architecture'] = architecture
    
    def add_task(self, task: Dict[str, Any]):
        """
        Agrega una tarea al estado
        
        Args:
            task: Dict con {description, status, priority, assigned_to, etc.}
        """
        task_entry = {
            'id': f"task_{len(self.state['tasks']) + 1}",
            'description': task.get('description', ''),
            'status': task.get('status', 'pending'),  # pending, in_progress, completed, failed
            'priority': task.get('priority', 'medium'),  # low, medium, high
            'assigned_to': task.get('assigned_to', 'unassigned'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'metadata': task.get('metadata', {})
        }
        
        self.state['tasks'].append(task_entry)
        self._record_history('task_added', {'task_id': task_entry['id'], 'description': task_entry['description']})
        
        logger.info(f"Task added: {task_entry['id']} - {task_entry['description']}")
    
    def update_task(self, task_id: str, updates: Dict[str, Any]):
        """Actualiza una tarea existente"""
        for task in self.state['tasks']:
            if task['id'] == task_id:
                task.update(updates)
                task['updated_at'] = datetime.now().isoformat()
                self._record_history('task_updated', {'task_id': task_id, 'updates': updates})
                logger.info(f"Task updated: {task_id}")
                return True
        
        logger.warning(f"Task not found: {task_id}")
        return False
    
    def get_tasks_by_status(self, status: str) -> List[Dict]:
        """Obtiene tareas filtradas por estado"""
        return [t for t in self.state['tasks'] if t['status'] == status]
    
    def get_pending_tasks(self) -> List[Dict]:
        """Obtiene tareas pendientes"""
        return self.get_tasks_by_status('pending')
    
    def add_file_change(self, file_path: str, change_type: str, details: Dict = None):
        """
        Registra un cambio en un archivo
        
        Args:
            file_path: Ruta del archivo
            change_type: created, modified, deleted
            details: Detalles adicionales
        """
        change_entry = {
            'file': file_path,
            'type': change_type,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self._record_history('file_change', change_entry)
        
        # Actualizar lista de archivos si es necesario
        if change_type == 'created':
            self._add_file_to_state(file_path)
        elif change_type == 'deleted':
            self._remove_file_from_state(file_path)
        
        logger.info(f"File change recorded: {change_type} - {file_path}")
    
    def _add_file_to_state(self, file_path: str):
        """Agrega un archivo al estado"""
        abs_path = os.path.join(self.project_path, file_path) if self.project_path else file_path
        
        if os.path.exists(abs_path):
            stat = os.stat(abs_path)
            file_info = {
                'path': file_path,
                'absolute_path': abs_path,
                'size': stat.st_size,
                'extension': os.path.splitext(file_path)[1].lower(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
            }
            
            # Verificar si ya existe
            existing = [f for f in self.state['files'] if f['path'] == file_path]
            if not existing:
                self.state['files'].append(file_info)
    
    def _remove_file_from_state(self, file_path: str):
        """Elimina un archivo del estado"""
        self.state['files'] = [f for f in self.state['files'] if f['path'] != file_path]
    
    def _record_history(self, event_type: str, data: Dict):
        """Registra un evento en el historial"""
        history_entry = {
            'event': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self.state['history'].append(history_entry)
        
        # Limitar historial a últimos 100 eventos
        if len(self.state['history']) > 100:
            self.state['history'] = self.state['history'][-100:]
    
    def get_state(self) -> Dict[str, Any]:
        """Obtiene el estado completo del proyecto"""
        return self.state.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtiene resumen del estado"""
        return {
            'project_path': self.project_path,
            'total_files': len(self.state['files']),
            'total_dependencies': len(self.state['dependencies']),
            'architecture_type': self.state['architecture']['type'],
            'total_tasks': len(self.state['tasks']),
            'pending_tasks': len(self.get_pending_tasks()),
            'history_events': len(self.state['history']),
            'last_updated': self.state['metadata']['last_updated']
        }
    
    def export_state(self, filepath: str = None):
        """Exporta el estado a JSON"""
        if filepath is None:
            filepath = os.path.join(self.project_path, '.kalin_state.json') if self.project_path else 'project_state.json'
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Project state exported to: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting state: {e}")
            return False
    
    def import_state(self, filepath: str):
        """Importa estado desde JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
            
            logger.info(f"Project state imported from: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error importing state: {e}")
            return False
    
    def reset(self):
        """Reinicia el estado (manteniendo metadata)"""
        created_at = self.state['metadata']['created_at']
        
        self.state = {
            'files': [],
            'dependencies': [],
            'architecture': {
                'type': 'unknown',
                'layers': [],
                'modules': [],
                'patterns': []
            },
            'tasks': [],
            'history': [],
            'metadata': {
                'created_at': created_at,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
        }
        
        logger.info("Project state reset")


class ProjectStateManager:
    """
    Gestor singleton de ProjectState
    
    Permite múltiples instancias de ProjectState para diferentes proyectos,
    pero mantiene un estado activo principal.
    """
    
    def __init__(self):
        self.active_state: Optional[ProjectState] = None
        self.project_states: Dict[str, ProjectState] = {}
        
        logger.info("ProjectStateManager initialized")
    
    def set_active_project(self, project_path: str) -> ProjectState:
        """
        Establece el proyecto activo
        
        Args:
            project_path: Ruta del proyecto
        
        Returns:
            ProjectState del proyecto activo
        """
        # Si ya existe, reutilizar
        if project_path in self.project_states:
            self.active_state = self.project_states[project_path]
            logger.info(f"Switched to existing project: {project_path}")
        else:
            # Crear nuevo estado
            new_state = ProjectState(project_path)
            self.project_states[project_path] = new_state
            self.active_state = new_state
            logger.info(f"Created new project state: {project_path}")
        
        return self.active_state
    
    def get_active_state(self) -> Optional[ProjectState]:
        """Obtiene el estado del proyecto activo"""
        return self.active_state
    
    def get_project_state(self, project_path: str) -> Optional[ProjectState]:
        """Obtiene el estado de un proyecto específico"""
        return self.project_states.get(project_path)
    
    def list_projects(self) -> List[str]:
        """Lista todos los proyectos gestionados"""
        return list(self.project_states.keys())
    
    def remove_project(self, project_path: str):
        """Elimina un proyecto del gestor"""
        if project_path in self.project_states:
            del self.project_states[project_path]
            
            if self.active_state and self.active_state.project_path == project_path:
                self.active_state = None
            
            logger.info(f"Removed project: {project_path}")


# Singleton global
_project_state_manager = None


def get_project_state_manager() -> ProjectStateManager:
    """Obtiene instancia singleton del ProjectStateManager"""
    global _project_state_manager
    if _project_state_manager is None:
        _project_state_manager = ProjectStateManager()
    return _project_state_manager


def get_active_project_state() -> Optional[ProjectState]:
    """Obtiene el estado del proyecto activo directamente"""
    manager = get_project_state_manager()
    return manager.get_active_state()
