"""
Task Queue para Kalin usando Celery.
Permite ejecutar operaciones asíncronas (análisis largo, fixes complejos, etc.)
"""

import os
from celery import Celery
from celery.result import AsyncResult
from typing import Dict, Any, Optional
from agent.core.logger import get_logger

logger = get_logger('kalin.tasks')

# Configuración de Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Crear aplicación Celery
celery_app = Celery(
    'kalin_tasks',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Configuración
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutos máximo por tarea
    worker_prefetch_multiplier=1,
)

@celery_app.task(bind=True)
def analyze_project_task(self, project_path: str) -> Dict[str, Any]:
    """
    Tarea asíncrona para analizar un proyecto completo.
    """
    try:
        logger.info(f"Starting project analysis: {project_path}")
        
        from agent.core.project_analyzer import ProjectAnalyzer
        
        analyzer = ProjectAnalyzer(project_path)
        resumen = analyzer.get_resumen()
        
        # Actualizar progreso
        self.update_state(state='PROGRESS', meta={'progress': 100})
        
        logger.info(f"Project analysis completed: {resumen['total_archivos']} files")
        
        return {
            'status': 'completed',
            'result': resumen
        }
        
    except Exception as e:
        logger.error(f"Project analysis failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }

@celery_app.task(bind=True)
def fix_code_task(self, file_path: str, codigo: str, analisis: str) -> Dict[str, Any]:
    """
    Tarea asíncrona para reparar código.
    """
    try:
        logger.info(f"Starting code fix: {file_path}")
        
        from agent.actions.tools.fix_tool import reparar_codigo
        
        # Actualizar progreso
        self.update_state(state='PROGRESS', meta={'progress': 50})
        
        nuevo_codigo = reparar_codigo(codigo, analisis)
        
        self.update_state(state='PROGRESS', meta={'progress': 100})
        
        if not nuevo_codigo:
            return {
                'status': 'failed',
                'error': 'No se pudo generar código'
            }
        
        logger.info(f"Code fix completed: {file_path}")
        
        return {
            'status': 'completed',
            'result': {
                'nuevo_codigo': nuevo_codigo,
                'file_path': file_path
            }
        }
        
    except Exception as e:
        logger.error(f"Code fix failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }

@celery_app.task(bind=True)
def scan_and_fix_task(self, project_path: str) -> Dict[str, Any]:
    """
    Tarea asíncrona para escanear y reparar múltiples archivos.
    """
    try:
        logger.info(f"Starting scan and fix: {project_path}")
        
        from agent.core.project_analyzer import ProjectAnalyzer
        from agent.analyzer import analizar_codigo
        from agent.actions.tools.fix_tool import reparar_codigo
        
        analyzer = ProjectAnalyzer(project_path)
        archivos = analyzer.get_archivos_por_tipo()
        
        total = len(archivos.get('python', []))
        fixed_count = 0
        
        for i, archivo in enumerate(archivos.get('python', [])):
            try:
                # Leer archivo
                with open(os.path.join(project_path, archivo), 'r', encoding='utf-8') as f:
                    codigo = f.read()
                
                # Analizar
                analisis = analizar_codigo(codigo)
                
                # Reparar
                nuevo = reparar_codigo(codigo, analisis)
                
                if nuevo and nuevo != codigo:
                    # Guardar cambios
                    with open(os.path.join(project_path, archivo), 'w', encoding='utf-8') as f:
                        f.write(nuevo)
                    fixed_count += 1
                
                # Actualizar progreso
                progress = int((i + 1) / total * 100) if total > 0 else 100
                self.update_state(state='PROGRESS', meta={
                    'progress': progress,
                    'current_file': archivo,
                    'fixed_so_far': fixed_count
                })
                
            except Exception as e:
                logger.warning(f"Failed to fix {archivo}: {e}")
        
        logger.info(f"Scan and fix completed: {fixed_count} files fixed")
        
        return {
            'status': 'completed',
            'result': {
                'total_files': total,
                'fixed_files': fixed_count
            }
        }
        
    except Exception as e:
        logger.error(f"Scan and fix failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }

class TaskManager:
    """Gestiona tareas asíncronas"""
    
    @staticmethod
    def start_analysis(project_path: str) -> str:
        """Inicia análisis asíncrono y retorna task_id"""
        task = analyze_project_task.delay(project_path)
        logger.info(f"Analysis task started: {task.id}")
        return task.id
    
    @staticmethod
    def start_fix(file_path: str, codigo: str, analisis: str) -> str:
        """Inicia fix asíncrono y retorna task_id"""
        task = fix_code_task.delay(file_path, codigo, analisis)
        logger.info(f"Fix task started: {task.id}")
        return task.id
    
    @staticmethod
    def start_scan_and_fix(project_path: str) -> str:
        """Inicia scan & fix asíncrono y retorna task_id"""
        task = scan_and_fix_task.delay(project_path)
        logger.info(f"Scan and fix task started: {task.id}")
        return task.id
    
    @staticmethod
    def get_task_status(task_id: str) -> Dict[str, Any]:
        """Obtiene el estado de una tarea"""
        result = AsyncResult(task_id, app=celery_app)
        
        if result.state == 'PENDING':
            return {'state': 'pending', 'progress': 0}
        elif result.state == 'STARTED':
            return {'state': 'started', 'progress': 0}
        elif result.state == 'PROGRESS':
            return {
                'state': 'in_progress',
                'progress': result.info.get('progress', 0),
                'meta': result.info
            }
        elif result.state == 'SUCCESS':
            return {
                'state': 'completed',
                'result': result.result
            }
        elif result.state == 'FAILURE':
            return {
                'state': 'failed',
                'error': str(result.result)
            }
        else:
            return {'state': result.state}
    
    @staticmethod
    def revoke_task(task_id: str):
        """Cancela una tarea en ejecución"""
        celery_app.control.revoke(task_id, terminate=True)
        logger.info(f"Task revoked: {task_id}")

# Instancia global
task_manager = TaskManager()
