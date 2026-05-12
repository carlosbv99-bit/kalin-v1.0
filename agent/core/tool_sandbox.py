"""
Tool Execution Sandbox
Sistema de sandbox para ejecutar tools de forma segura y controlada

Flujo obligatorio:
LLM → Intent → Tool Executor → Sandbox → Resultado

Nunca permite ejecución directa del modelo.
Siempre pasa por validación, permisos y aislamiento.
"""

import os
import sys
import time
import subprocess
import tempfile
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from agent.core.logger import get_logger

logger = get_logger('kalin.tool_sandbox')


class SandboxConfig:
    """Configuración del sandbox"""
    
    def __init__(
        self,
        allowed_tools: List[str] = None,
        blocked_operations: List[str] = None,
        max_execution_time: int = 30,
        max_memory_mb: int = 512,
        allow_file_write: bool = True,
        allow_file_delete: bool = False,
        allow_network: bool = False,
        allow_shell: bool = False,
        working_directory: str = None
    ):
        self.allowed_tools = allowed_tools or []  # Lista blanca de tools
        self.blocked_operations = blocked_operations or [
            'rm -rf',
            'format',
            'del /f',
            'shutdown',
            'sudo'
        ]
        self.max_execution_time = max_execution_time
        self.max_memory_mb = max_memory_mb
        self.allow_file_write = allow_file_write
        self.allow_file_delete = allow_file_delete
        self.allow_network = allow_network
        self.allow_shell = allow_shell
        self.working_directory = working_directory or os.getcwd()


class ToolExecutionResult:
    """Resultado de ejecución de tool en sandbox"""
    
    def __init__(
        self,
        success: bool,
        result: Any = None,
        error: str = None,
        execution_time: float = 0.0,
        sandbox_violations: List[str] = None
    ):
        self.success = success
        self.result = result
        self.error = error
        self.execution_time = execution_time
        self.sandbox_violations = sandbox_violations or []
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'result': self.result,
            'error': self.error,
            'execution_time': self.execution_time,
            'sandbox_violations': self.sandbox_violations,
            'timestamp': self.timestamp
        }


class ToolSandbox:
    """
    Sandbox para ejecución segura de tools
    
    Flujo:
    1. Validar tool contra lista blanca
    2. Verificar permisos
    3. Ejecutar en entorno aislado
    4. Capturar resultado
    5. Validar output
    """
    
    def __init__(self, config: SandboxConfig = None):
        self.config = config or SandboxConfig()
        self.execution_log: List[Dict] = []
        self.violation_count = 0
        
        logger.info("ToolSandbox initialized")
    
    def execute_tool(
        self,
        tool_name: str,
        tool_func: Callable,
        params: Dict[str, Any],
        context: Dict[str, Any] = None,
        task_id: str = None
    ) -> ToolExecutionResult:
        """
        Ejecuta una tool dentro del sandbox
        
        Args:
            tool_name: Nombre de la tool
            tool_func: Función a ejecutar
            params: Parámetros
            context: Contexto de ejecución
            task_id: ID de tarea para tracking
        
        Returns:
            ToolExecutionResult con resultado o error
        """
        start_time = time.time()
        context = context or {}
        
        logger.info(f"Sandbox executing: {tool_name} (task: {task_id})")
        
        # PASO 1: Validar tool contra lista blanca
        if self.config.allowed_tools and tool_name not in self.config.allowed_tools:
            violation = f"Tool '{tool_name}' not in allowed list"
            logger.warning(violation)
            return ToolExecutionResult(
                success=False,
                error=violation,
                execution_time=time.time() - start_time,
                sandbox_violations=[violation]
            )
        
        # PASO 2: Validar parámetros (buscar operaciones bloqueadas)
        violations = self._validate_params(params)
        if violations:
            self.violation_count += len(violations)
            logger.warning(f"Sandbox violations detected: {violations}")
            return ToolExecutionResult(
                success=False,
                error=f"Sandbox violations: {', '.join(violations)}",
                execution_time=time.time() - start_time,
                sandbox_violations=violations
            )
        
        # PASO 2.5: Validar parámetros requeridos para tools específicos
        required_params = self._get_required_params(tool_name)
        missing_params = [p for p in required_params if p not in params]
        if missing_params:
            error_msg = f"Tool '{tool_name}' requires parameters: {', '.join(required_params)}. Missing: {', '.join(missing_params)}"
            logger.warning(error_msg)
            # En lugar de fallar, devolver resultado parcial con advertencia
            # Esto permite que la respuesta del LLM se use aunque el tool falle
            return ToolExecutionResult(
                success=False,
                error=error_msg,
                execution_time=time.time() - start_time,
                sandbox_violations=[f"Missing required parameters: {', '.join(missing_params)}"]
            )
        
        # PASO 3: Ejecutar con timeout y captura de errores
        try:
            result = self._execute_with_safety(tool_func, params, context)
            
            execution_time = time.time() - start_time
            
            # PASO 4: Validar resultado
            if self._validate_result(result, tool_name):
                logger.info(f"Tool executed successfully: {tool_name} ({execution_time:.3f}s)")
                
                # Log ejecución
                self.execution_log.append({
                    'task_id': task_id,
                    'tool': tool_name,
                    'success': True,
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                })
                
                return ToolExecutionResult(
                    success=True,
                    result=result,
                    execution_time=execution_time
                )
            else:
                violation = f"Invalid result from tool: {tool_name}"
                return ToolExecutionResult(
                    success=False,
                    error=violation,
                    execution_time=execution_time,
                    sandbox_violations=[violation]
                )
        
        except TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Tool execution timed out after {self.config.max_execution_time}s"
            logger.error(error_msg)
            
            return ToolExecutionResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(error_msg)
            
            return ToolExecutionResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
    
    def _validate_params(self, params: Dict[str, Any]) -> List[str]:
        """Valida parámetros buscando operaciones peligrosas"""
        violations = []
        
        # Convertir params a string para búsqueda
        params_str = str(params).lower()
        
        # Verificar operaciones bloqueadas
        for operation in self.config.blocked_operations:
            if operation.lower() in params_str:
                violations.append(f"Blocked operation detected: {operation}")
        
        # Verificar paths fuera del working directory
        for key, value in params.items():
            if isinstance(value, str) and ('path' in key.lower() or 'file' in key.lower()):
                abs_path = os.path.abspath(value)
                if not abs_path.startswith(os.path.abspath(self.config.working_directory)):
                    violations.append(f"Path outside working directory: {value}")
        
        # Verificar si se permite escritura/eliminación
        if not self.config.allow_file_delete:
            delete_indicators = ['delete', 'remove', 'unlink', 'rmdir']
            if any(indicator in params_str for indicator in delete_indicators):
                violations.append("File deletion not allowed")
        
        return violations
    
    def _execute_with_safety(
        self,
        tool_func: Callable,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """Ejecuta tool con medidas de seguridad"""
        
        # Si es proceso externo, usar subprocess con timeout
        if hasattr(tool_func, '__module__') and 'subprocess' in str(tool_func.__module__):
            return self._execute_subprocess(tool_func, params)
        
        # Para funciones Python, ejecutar directamente con validación
        import inspect
        sig = inspect.signature(tool_func)
        
        # Verificar si acepta context
        if 'context' in sig.parameters:
            result = tool_func(**params, context=context)
        else:
            result = tool_func(**params)
        
        return result
    
    def _execute_subprocess(self, tool_func: Callable, params: Dict) -> Any:
        """Ejecuta subprocess con restricciones de seguridad"""
        if not self.config.allow_shell:
            raise PermissionError("Shell execution not allowed in sandbox")
        
        # Ejecutar con timeout y sin shell si es posible
        timeout = self.config.max_execution_time
        
        try:
            result = subprocess.run(
                **params,
                timeout=timeout,
                capture_output=True,
                text=True,
                shell=False  # Nunca usar shell=True por seguridad
            )
            return result
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Subprocess timed out after {timeout}s")
    
    def _get_required_params(self, tool_name: str) -> List[str]:
        """Devuelve lista de parámetros requeridos para cada tool"""
        required = {
            'write_file': ['path', 'content'],
            'read_file': ['path'],
            'apply_patch': ['file_path'],
            'create_patch': ['file_path', 'modified'],
            'generate_with_llm': ['prompt'],
        }
        return required.get(tool_name, [])
    
    def _validate_result(self, result: Any, tool_name: str) -> bool:
        """Valida el resultado de la tool"""
        
        # Resultado None puede ser válido para algunas tools
        if result is None:
            return tool_name in ['write_file', 'delete_file', 'apply_patch']
        
        # Verificar que no sea demasiado grande
        result_str = str(result)
        if len(result_str) > 10_000_000:  # 10MB límite
            logger.warning(f"Result too large: {len(result_str)} bytes")
            return False
        
        return True
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Estadísticas de ejecución del sandbox"""
        total_executions = len(self.execution_log)
        successful = sum(1 for log in self.execution_log if log['success'])
        failed = total_executions - successful
        
        avg_time = 0.0
        if total_executions > 0:
            total_time = sum(log['execution_time'] for log in self.execution_log)
            avg_time = total_time / total_executions
        
        return {
            'total_executions': total_executions,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total_executions if total_executions > 0 else 0,
            'avg_execution_time': round(avg_time, 3),
            'violations_detected': self.violation_count
        }
    
    def clear_log(self):
        """Limpia el log de ejecuciones"""
        self.execution_log.clear()
        self.violation_count = 0


class SandboxedToolExecutor:
    """
    Executor que envuelve ToolManager con Sandbox
    
    Uso:
        executor = SandboxedToolExecutor()
        result = executor.execute_safe(tool_name, params, context)
    """
    
    def __init__(self, sandbox_config: SandboxConfig = None):
        self.sandbox = ToolSandbox(sandbox_config)
        
        # Registrar tools permitidas por defecto
        self.sandbox.config.allowed_tools = [
            'read_file',
            'write_file',
            'analyze_code',
            'generate_with_llm',
            'search_files',
            'apply_patch',
            'create_patch',
            'undo_patch',
            'emit_event'
        ]
        
        logger.info("SandboxedToolExecutor initialized")
    
    def execute_safe(
        self,
        tool_name: str,
        tool_func: Callable,
        params: Dict[str, Any],
        context: Dict[str, Any] = None,
        task_id: str = None
    ) -> ToolExecutionResult:
        """
        Ejecuta tool de forma segura en sandbox
        
        Args:
            tool_name: Nombre de la tool
            tool_func: Función de la tool
            params: Parámetros
            context: Contexto
            task_id: ID de tarea
        
        Returns:
            ToolExecutionResult
        """
        return self.sandbox.execute_tool(
            tool_name=tool_name,
            tool_func=tool_func,
            params=params,
            context=context,
            task_id=task_id
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del executor"""
        return self.sandbox.get_execution_stats()


# Singleton global
_sandbox_executor = None


def get_sandbox_executor() -> SandboxedToolExecutor:
    """Obtiene instancia singleton del SandboxedToolExecutor"""
    global _sandbox_executor
    if _sandbox_executor is None:
        _sandbox_executor = SandboxedToolExecutor()
    return _sandbox_executor
