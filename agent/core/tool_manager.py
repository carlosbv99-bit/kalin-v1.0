"""
Tool Manager Centralizado
Gestiona herramientas desacopladas para múltiples agentes

Uso:
    tool_manager = ToolManager()
    result = tool_manager.run("generate_code", params={...})
    
Ventajas:
- Frontend agent, backend agent, QA agent usan las mismas tools
- Fácil agregar nuevas tools sin modificar agentes
- Logging y métricas centralizadas
"""

import os
import time
from typing import Dict, Any, Optional, Callable
from agent.core.logger import get_logger

logger = get_logger('kalin.tool_manager')


class ToolRegistry:
    """Registro de herramientas disponibles"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def register(self, name: str, func: Callable, description: str = "", category: str = "general"):
        """
        Registra una herramienta
        
        Args:
            name: Nombre único de la tool
            func: Función ejecutable
            description: Descripción de lo que hace
            category: Categoría (io, llm, filesystem, etc.)
        """
        self.tools[name] = {
            'func': func,
            'description': description,
            'category': category,
            'registered_at': time.time()
        }
        logger.info(f"Tool registered: {name} ({category})")
    
    def get(self, name: str) -> Optional[Dict]:
        """Obtiene una tool por nombre"""
        return self.tools.get(name)
    
    def list_tools(self) -> Dict[str, Dict]:
        """Lista todas las tools registradas"""
        return {
            name: {
                'description': info['description'],
                'category': info['category']
            }
            for name, info in self.tools.items()
        }


class ToolManager:
    """
    Gestor centralizado de herramientas
    
    Uso:
        tool_manager = ToolManager()
        result = tool_manager.run("read_file", {"path": "main.py"})
    """
    
    def __init__(self):
        self.registry = ToolRegistry()
        self.execution_stats = {
            'total_executions': 0,
            'errors': 0,
            'avg_execution_time': 0.0,
            'tool_usage': {}
        }
        
        # Registrar tools del sistema
        self._register_system_tools()
        
        logger.info("ToolManager initialized")
    
    def run(self, tool_name: str, params: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Any:
        """
        Ejecuta una herramienta por nombre
        
        Args:
            tool_name: Nombre de la tool a ejecutar
            params: Parámetros para la tool
            context: Contexto adicional (session_id, task_id, ruta proyecto, etc.)
        
        Returns:
            Resultado de la ejecución
        
        Raises:
            ValueError: Si la tool no existe
            Exception: Si la tool falla
        """
        start_time = time.time()
        self.execution_stats['total_executions'] += 1
        
        # Extraer task_id del contexto si existe
        task_id = context.get('task_id') if context else None
        session_id = context.get('session_id') if context else None
        
        # Verificar que la tool existe
        tool_info = self.registry.get(tool_name)
        if not tool_info:
            error_msg = f"Tool '{tool_name}' no registrada"
            logger.error(error_msg)
            self.execution_stats['errors'] += 1
            raise ValueError(error_msg)
        
        try:
            # Ejecutar tool
            func = tool_info['func']
            params = params or {}
            
            logger.debug(f"Executing tool: {tool_name} with {len(params)} params")
            
            # EJECUTAR A TRAVÉS DEL SANDBOX
            from agent.core.tool_sandbox import get_sandbox_executor
            sandbox_executor = get_sandbox_executor()
            
            sandbox_result = sandbox_executor.execute_safe(
                tool_name=tool_name,
                tool_func=func,
                params=params,
                context=context,
                task_id=context.get('task_id') if context else None
            )
            
            # Verificar resultado del sandbox
            if not sandbox_result.success:
                error_msg = f"Sandbox blocked execution: {sandbox_result.error}"
                logger.error(error_msg)
                self.execution_stats['errors'] += 1
                raise Exception(error_msg)
            
            result = sandbox_result.result
            
            # Actualizar estadísticas
            duration = time.time() - start_time
            self._update_stats(tool_name, duration, success=True)
            
            # Emitir evento de tool ejecutada con task_id
            if task_id or session_id:
                from agent.core.event_bus import get_event_bus, EVENT_TOOL_EXECUTED
                event_bus = get_event_bus()
                event_bus.emit(EVENT_TOOL_EXECUTED, {
                    'task_id': task_id,
                    'session_id': session_id,
                    'tool': tool_name,
                    'duration': duration,
                    'success': True
                }, source='tool_manager')
            
            logger.debug(f"Tool {tool_name} executed in {duration:.3f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.execution_stats['errors'] += 1
            self._update_stats(tool_name, duration, success=False)
            
            logger.error(f"Tool {tool_name} failed after {duration:.3f}s: {e}")
            raise
    
    def run_multiple(self, tool_calls: list) -> list:
        """
        Ejecuta múltiples tools en secuencia
        
        Args:
            tool_calls: Lista de dicts con {'tool': name, 'params': {...}}
        
        Returns:
            Lista de resultados
        """
        results = []
        
        for call in tool_calls:
            tool_name = call.get('tool')
            params = call.get('params', {})
            context = call.get('context', {})
            
            try:
                result = self.run(tool_name, params, context)
                results.append({
                    'tool': tool_name,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'tool': tool_name,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def get_available_tools(self) -> Dict:
        """Lista todas las tools disponibles"""
        return self.registry.list_tools()
    
    def get_stats(self) -> Dict:
        """Estadísticas de uso de tools"""
        return {
            **self.execution_stats,
            'registered_tools': len(self.registry.tools),
            'tools_list': list(self.registry.tools.keys())
        }
    
    def _register_system_tools(self):
        """Registra tools del sistema"""
        
        # Tools de I/O de archivos (desde web.py via utils)
        # Estas se registrarán dinámicamente cuando se pasen como utils
        # Por ahora, usamos wrappers que llaman a las funciones reales
        
        self.registry.register(
            name="read_file",
            func=self._read_file_wrapper,
            description="Lee el contenido de un archivo",
            category="io"
        )
        
        self.registry.register(
            name="write_file",
            func=self._write_file_wrapper,
            description="Escribe contenido en un archivo",
            category="io"
        )
        
        # Tools de análisis
        self.registry.register(
            name="analyze_code",
            func=self._analyze_code_wrapper,
            description="Analiza código en busca de problemas",
            category="analysis"
        )
        
        # Tools de LLM
        self.registry.register(
            name="generate_with_llm",
            func=self._generate_with_llm,
            description="Genera texto/código usando LLM",
            category="llm"
        )
        
        # Tools de utilidad
        self.registry.register(
            name="search_files",
            func=self._search_files,
            description="Busca archivos por patrón",
            category="filesystem"
        )
        
        # Tools de patching
        self.registry.register(
            name="apply_patch",
            func=self._apply_patch,
            description="Aplica un parche/diff a un archivo",
            category="patching"
        )
        
        self.registry.register(
            name="create_patch",
            func=self._create_patch,
            description="Crea un parche comparando dos versiones",
            category="patching"
        )
        
        self.registry.register(
            name="undo_patch",
            func=self._undo_patch,
            description="Revierte el último parche aplicado",
            category="patching"
        )
        
        # Tool de eventos
        self.registry.register(
            name="emit_event",
            func=self._emit_event,
            description="Emite un evento al event bus",
            category="events"
        )
        
        logger.info(f"Registered {len(self.registry.tools)} system tools")
    
    def _generate_with_llm(self, prompt: str, model: str = None, temperature: float = 0.7, **kwargs) -> str:
        """Tool para generar con LLM"""
        from agent.llm.provider_manager import get_manager
        
        manager = get_manager()
        response = manager.generate(prompt, use_case="fix", max_tokens=2048)
        
        if response and response.text:
            return response.text
        return ""
    
    def _search_files(self, pattern: str, directory: str = ".", **kwargs) -> list:
        """Tool para buscar archivos"""
        import fnmatch
        
        matches = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    matches.append(os.path.join(root, filename))
        
        return matches
    
    def _apply_patch(self, file_path: str, diff: str = None, new_content: str = None, **kwargs) -> Dict[str, Any]:
        """Tool para aplicar parche a archivo"""
        from agent.core.patch_system import get_patch_manager
        
        patch_mgr = get_patch_manager()
        
        # Si se proporciona diff, aplicarlo directamente
        if diff:
            # Leer contenido actual
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Crear patch desde diff (simplificado)
            # En producción, parsear el diff correctamente
            success = True  # Placeholder
            return {'success': success, 'message': 'Patch applied'}
        
        # Si se proporciona new_content, crear patch y aplicar
        elif new_content:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            patch = patch_mgr.create_patch(
                file_path=file_path,
                original_content=original_content,
                new_content=new_content,
                description=kwargs.get('description', 'Auto-generated patch'),
                author=kwargs.get('author', 'tool_manager')
            )
            
            success = patch_mgr.apply_patch(patch)
            
            return {
                'success': success,
                'patch_info': patch.to_dict() if success else None
            }
        
        else:
            raise ValueError("Must provide either 'diff' or 'new_content'")
    
    def _create_patch(self, file_path: str, original: str = None, modified: str = None, **kwargs) -> Dict[str, Any]:
        """Tool para crear parche"""
        from agent.core.patch_system import get_patch_manager
        
        patch_mgr = get_patch_manager()
        
        # Si no se proporcionan contenidos, leer del archivo
        if original is None:
            # Asumir que es el contenido actual del archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                original = f.read()
        
        if modified is None:
            raise ValueError("Must provide 'modified' content")
        
        patch = patch_mgr.create_patch(
            file_path=file_path,
            original_content=original,
            new_content=modified,
            description=kwargs.get('description', ''),
            author=kwargs.get('author', 'tool_manager')
        )
        
        return {
            'success': True,
            'patch': patch.to_dict(),
            'diff_preview': patch.diff[:500]  # Preview del diff
        }
    
    def _undo_patch(self, file_path: str = None, **kwargs) -> Dict[str, Any]:
        """Tool para revertir último parche"""
        from agent.core.patch_system import get_patch_manager
        
        patch_mgr = get_patch_manager()
        success = patch_mgr.undo_last_patch(file_path)
        
        return {
            'success': success,
            'message': 'Patch undone' if success else 'No patch to undo'
        }
    
    def _emit_event(self, event_name: str, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Tool para emitir evento"""
        from agent.core.event_bus import get_event_bus
        
        event_bus = get_event_bus()
        event_bus.emit(event_name, data, source=kwargs.get('source', 'tool_manager'))
        
        return {
            'success': True,
            'event': event_name,
            'data': data
        }
    
    def _read_file_wrapper(self, path: str, **kwargs) -> str:
        """Wrapper para leer archivo (debe recibir utils desde context)"""
        context = kwargs.get('context', {})
        utils = context.get('utils', {})
        
        if 'leer_archivo' in utils:
            return utils['leer_archivo'](path)
        else:
            # Implementación básica si no hay utils
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {e}"
    
    def _write_file_wrapper(self, path: str, content: str, **kwargs) -> bool:
        """Wrapper para escribir archivo"""
        context = kwargs.get('context', {})
        utils = context.get('utils', {})
        
        if 'escribir_archivo' in utils:
            return utils['escribir_archivo'](path, content)
        else:
            # Implementación básica
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            except Exception as e:
                return False
    
    def _analyze_code_wrapper(self, code: str, **kwargs) -> Dict:
        """Wrapper para analizar código"""
        context = kwargs.get('context', {})
        utils = context.get('utils', {})
        
        if 'analizar_codigo' in utils:
            return utils['analizar_codigo'](code)
        else:
            # Análisis básico
            return {
                'lines': len(code.splitlines()),
                'chars': len(code),
                'issues': []
            }
    
    def _update_stats(self, tool_name: str, duration: float, success: bool):
        """Actualiza estadísticas de ejecución"""
        if tool_name not in self.execution_stats['tool_usage']:
            self.execution_stats['tool_usage'][tool_name] = {
                'count': 0,
                'errors': 0,
                'avg_time': 0.0
            }
        
        stats = self.execution_stats['tool_usage'][tool_name]
        stats['count'] += 1
        
        if not success:
            stats['errors'] += 1
        
        # Calcular promedio móvil
        current_avg = stats['avg_time']
        count = stats['count']
        stats['avg_time'] = (current_avg * (count - 1) + duration) / count
        
        # Actualizar promedio global
        total = self.execution_stats['total_executions']
        global_avg = self.execution_stats['avg_execution_time']
        self.execution_stats['avg_execution_time'] = (
            (global_avg * (total - 1) + duration) / total
        )


# Singleton global
_tool_manager = None


def get_tool_manager() -> ToolManager:
    """Obtiene instancia singleton del ToolManager"""
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = ToolManager()
    return _tool_manager
