from dotenv import load_dotenv
load_dotenv()  # Cargar .env ANTES de cualquier import

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import difflib
import logging

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger('kalin.web')

from agent.core.orchestrator import Orchestrator
from agent.analyzer import analizar_codigo
from agent.llm.client import get_provider_status
from agent.core.brain import construir_contexto, planificar
from agent.core.security_hardening import NetworkSecurity, CredentialManager
from agent.core.stability import health_monitor, performance_optimizer
from agent.core.experience_memory import get_experience_memory

# Inicializar Flask con configuración segura
app = Flask(__name__)

# CORS: Permitir requests desde el mismo origen (necesario para desarrollo)
CORS(app, resources={
    r"/*": {
        "origins": "*",  # En desarrollo, permitir todos los orígenes
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# SEGURIDAD: Agregar headers de seguridad en todas las respuestas
@app.after_request
def add_security_headers(response):
    # NO agregar headers de seguridad que puedan interferir con CORS
    # Solo agregar headers básicos
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

orchestrator = Orchestrator()

# Verificación de configuración activa
active_provider = os.getenv('ACTIVE_PROVIDER', 'ollama')
# Normalizar nombre del proveedor (aceptar 'grok' o 'groq')
if active_provider.lower() in ['grok', 'groq']:
    active_provider_normalized = 'GROQ'
else:
    active_provider_normalized = active_provider.upper()
    
print(f"\n🤖 Proveedor Activo: {active_provider_normalized}")
if active_provider.lower() in ['grok', 'groq']:
    print(f"🔑 Groq API Key configurada: {'Sí' if os.getenv('GROK_API_KEY') or os.getenv('GROQ_API_KEY') else 'No'}")
    print(f"📦 Modelo Groq: {os.getenv('GROK_MODEL', 'llama-3.1-8b-instant')}")
elif active_provider.lower() == 'ollama':
    print(f"📦 Modelo Ollama: {os.getenv('OLLAMA_MODEL', 'deepseek-coder:6.7b')}")
print("="*50 + "\n")

MODO_SEGURO = True
RUTA_PROYECTO = ""
ULTIMO_FIX = None

# ==============================
# 🌐 WEB
# ==============================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/test-sidebar")
def test_sidebar():
    """Página de prueba para el menú lateral"""
    return render_template("test-sidebar.html")

@app.route("/diagnostico-botones")
def diagnostico_botones():
    """Página de diagnóstico para botones del sidebar"""
    return render_template("diagnostico-botones.html")

@app.route("/help")
def help_page():
    return jsonify({
        "respuesta": "Comandos disponibles: /setpath <ruta>, /scan, /fix <archivo>, /apply, /analyze <archivo>, /create <requerimiento>, /refactor <archivo>, /llm-status"
    })

@app.route("/llm-status")
def llm_status():
    try:
        status = get_provider_status()
        return jsonify({
            "respuesta": "✅ Estado de proveedores LLM",
            "providers": status
        })
    except Exception as exc:
        return jsonify({
            "respuesta": f"❌ Error al obtener estado LLM: {str(exc)}"
        }), 500

@app.route("/orchestration/stats")
def orchestration_stats():
    """Estadísticas de la capa de orquestación"""
    try:
        from agent.core.orchestration_layer import get_orchestration_layer
        orchestration = get_orchestration_layer()
        stats = orchestration.get_stats()
        
        return jsonify({
            "status": "success",
            "orchestration_stats": stats
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/memory/stats")
def memory_stats():
    """Estadísticas del gestor de memoria"""
    try:
        from agent.core.memory_manager import get_memory_manager
        memory_mgr = get_memory_manager()
        stats = memory_mgr.get_manager_stats()
        
        return jsonify({
            "status": "success",
            "memory_stats": stats
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/memory/session/<session_id>")
def memory_session(session_id):
    """Obtiene historial de una sesión específica"""
    try:
        from agent.core.memory_manager import get_memory_manager
        memory_mgr = get_memory_manager()
        history = memory_mgr.get_history(session_id, limit=20)
        session_stats = memory_mgr.get_session_stats(session_id)
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "history": history,
            "stats": session_stats
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/memory/clear/<session_id>", methods=['POST'])
def memory_clear(session_id):
    """Limpia la memoria de una sesión"""
    try:
        from agent.core.memory_manager import get_memory_manager
        memory_mgr = get_memory_manager()
        memory_mgr.clear_session(session_id)
        
        return jsonify({
            "status": "success",
            "message": f"Sesión {session_id} limpiada"
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/tools/list")
def tools_list():
    """Lista todas las tools disponibles"""
    try:
        from agent.core.tool_manager import get_tool_manager
        tool_mgr = get_tool_manager()
        tools = tool_mgr.get_available_tools()
        
        return jsonify({
            "status": "success",
            "tools": tools,
            "total": len(tools)
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/tools/stats")
def tools_stats():
    """Estadísticas de uso de tools"""
    try:
        from agent.core.tool_manager import get_tool_manager
        tool_mgr = get_tool_manager()
        stats = tool_mgr.get_stats()
        
        return jsonify({
            "status": "success",
            "tool_stats": stats
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/context/status")
def context_status():
    """Estado actual de todos los contextos modulares"""
    try:
        from agent.core.context_manager import get_context_manager
        context_mgr = get_context_manager()
        summary = context_mgr.get_context_summary()
        
        return jsonify({
            "status": "success",
            "context_summary": summary
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/context/full-prompt", methods=['POST'])
def context_full_prompt():
    """Genera prompt completo con todos los contextos"""
    try:
        from agent.core.context_manager import get_context_manager
        data = request.get_json()
        user_query = data.get('query', '')
        
        context_mgr = get_context_manager()
        full_prompt = context_mgr.build_full_prompt(user_query)
        
        return jsonify({
            "status": "success",
            "prompt": full_prompt,
            "length": len(full_prompt),
            "sections": context_mgr.get_context_summary()
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/project/state")
def project_state():
    """Obtiene el estado actual del proyecto"""
    try:
        from agent.core.project_state import get_active_project_state
        state = get_active_project_state()
        
        if not state:
            return jsonify({
                "status": "error",
                "message": "No hay proyecto activo"
            }), 404
        
        return jsonify({
            "status": "success",
            "project_state": state.get_state(),
            "summary": state.get_summary()
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/project/tasks", methods=['GET', 'POST'])
def project_tasks():
    """Gestiona tareas del proyecto"""
    try:
        from agent.core.project_state import get_active_project_state
        state = get_active_project_state()
        
        if not state:
            return jsonify({
                "status": "error",
                "message": "No hay proyecto activo"
            }), 404
        
        if request.method == 'POST':
            # Crear nueva tarea
            data = request.get_json()
            state.add_task(data)
            
            return jsonify({
                "status": "success",
                "message": "Tarea creada",
                "tasks": state.get_summary()['total_tasks']
            })
        else:
            # Listar tareas
            status_filter = request.args.get('status')
            
            if status_filter:
                tasks = state.get_tasks_by_status(status_filter)
            else:
                tasks = state.state['tasks']
            
            return jsonify({
                "status": "success",
                "tasks": tasks,
                "total": len(tasks)
            })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/project/scan", methods=['POST'])
def project_scan():
    """Re-escanea el proyecto y actualiza el estado"""
    try:
        from agent.core.project_state import get_active_project_state
        state = get_active_project_state()
        
        if not state:
            return jsonify({
                "status": "error",
                "message": "No hay proyecto activo"
            }), 404
        
        state.scan_project()
        
        return jsonify({
            "status": "success",
            "message": "Proyecto escaneado",
            "summary": state.get_summary()
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/patch/apply", methods=['POST'])
def patch_apply():
    """Aplica un parche a un archivo"""
    try:
        from agent.core.patch_system import get_patch_manager
        data = request.get_json()
        
        file_path = data.get('file_path')
        diff = data.get('diff')
        new_content = data.get('new_content')
        description = data.get('description', '')
        
        if not file_path:
            return jsonify({
                "status": "error",
                "message": "file_path requerido"
            }), 400
        
        patch_mgr = get_patch_manager()
        
        # Si se proporciona new_content, crear patch automáticamente
        if new_content and not diff:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            patch = patch_mgr.create_patch(
                file_path=file_path,
                original_content=original_content,
                new_content=new_content,
                description=description
            )
            
            success = patch_mgr.apply_patch(patch)
        else:
            # Aplicar diff directamente (implementación futura)
            return jsonify({
                "status": "error",
                "message": "Usa new_content por ahora"
            }), 400
        
        return jsonify({
            "status": "success" if success else "error",
            "message": "Parche aplicado" if success else "Error al aplicar parche",
            "patch_info": patch.to_dict() if success else None
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/patch/undo", methods=['POST'])
def patch_undo():
    """Revierte el último parche aplicado"""
    try:
        from agent.core.patch_system import get_patch_manager
        data = request.get_json()
        
        file_path = data.get('file_path')  # Opcional
        
        patch_mgr = get_patch_manager()
        success = patch_mgr.undo_last_patch(file_path)
        
        return jsonify({
            "status": "success" if success else "error",
            "message": "Parche revertido" if success else "No hay parche para revertir"
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/patch/history")
def patch_history():
    """Obtiene historial de parches"""
    try:
        from agent.core.patch_system import get_patch_manager
        
        file_path = request.args.get('file_path')
        limit = request.args.get('limit', type=int)
        
        patch_mgr = get_patch_manager()
        history = patch_mgr.get_patch_history(file_path, limit)
        stats = patch_mgr.get_stats()
        
        return jsonify({
            "status": "success",
            "history": history,
            "stats": stats
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/api/revert", methods=['POST'])
def api_revert():
    """Revierte el último cambio usando el nuevo PatchManager"""
    try:
        from agent.core.orchestration_layer import get_orchestration_layer
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        
        orchestrator = get_orchestration_layer()
        reverted_files = orchestrator.revert_last_change(session_id)
        
        if reverted_files:
            return jsonify({
                "success": True,
                "files": reverted_files,
                "message": "Cambio revertido exitosamente"
            })
        else:
            return jsonify({
                "success": False,
                "message": "No hay cambios para revertir"
            })
    except Exception as exc:
        logger.error(f"Error al revertir: {exc}")
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500

@app.route("/api/history")
def api_history():
    """Obtiene historial de cambios del PatchManager"""
    try:
        from agent.core.orchestration_layer import get_orchestration_layer
        session_id = request.args.get('session_id', 'default')
        limit = request.args.get('limit', type=int, default=10)
        
        orchestrator = get_orchestration_layer()
        history = orchestrator.get_change_history(session_id, limit)
        
        return jsonify(history)
    except Exception as exc:
        logger.error(f"Error al obtener historial: {exc}")
        return jsonify({
            "error": str(exc)
        }), 500

@app.route("/events/history")
def events_history():
    """Obtiene historial de eventos"""
    try:
        from agent.core.event_bus import get_event_bus
        
        event_name = request.args.get('event_name')
        limit = request.args.get('limit', type=int, default=50)
        
        event_bus = get_event_bus()
        history = event_bus.get_event_history(limit, event_name)
        stats = event_bus.get_stats()
        
        return jsonify({
            "status": "success",
            "events": history,
            "stats": stats
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/events/stats")
def events_stats():
    """Estadísticas del event bus"""
    try:
        from agent.core.event_bus import get_event_bus
        
        event_bus = get_event_bus()
        stats = event_bus.get_stats()
        
        return jsonify({
            "status": "success",
            "stats": stats
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/tasks/stats")
def tasks_stats():
    """Estadísticas del task manager"""
    try:
        from agent.core.task_identity import get_task_manager
        
        task_mgr = get_task_manager()
        stats = task_mgr.get_stats()
        
        return jsonify({
            "status": "success",
            "stats": stats
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/tasks/session/<session_id>")
def tasks_session(session_id):
    """Obtiene tareas de una sesión específica"""
    try:
        from agent.core.task_identity import get_task_manager
        
        limit = request.args.get('limit', type=int, default=50)
        
        task_mgr = get_task_manager()
        tasks = task_mgr.get_session_tasks(session_id, limit)
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "tasks": tasks,
            "total": len(tasks)
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/tasks/active")
def tasks_active():
    """Obtiene tareas activas actualmente"""
    try:
        from agent.core.task_identity import get_task_manager
        
        session_id = request.args.get('session_id')
        
        task_mgr = get_task_manager()
        active = task_mgr.get_active_tasks(session_id)
        
        return jsonify({
            "status": "success",
            "active_tasks": [t.to_dict() for t in active],
            "count": len(active)
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/sandbox/stats")
def sandbox_stats():
    """Estadísticas del sandbox"""
    try:
        from agent.core.tool_sandbox import get_sandbox_executor
        
        executor = get_sandbox_executor()
        stats = executor.get_stats()
        
        return jsonify({
            "status": "success",
            "sandbox_stats": stats
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/health")
def health():
    try:
        # Health check completo con monitoreo
        health_status = health_monitor.check_health()
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return jsonify({
            "status": health_status['status'],
            "llm_providers": get_provider_status(),
            "checks": health_status.get('checks', {}),
            "message": "Servidor operativo" if health_status['status'] == 'healthy' else "Sistema degradado",
            "timestamp": health_status.get('timestamp')
        }), status_code
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/system-status")
def system_status():
    """Estado completo del sistema con recomendaciones"""
    try:
        health_status = health_monitor.check_health()
        requirements = performance_optimizer.check_system_requirements()
        tips = performance_optimizer.get_performance_tips()
        
        return jsonify({
            "health": health_status,
            "requirements": requirements,
            "tips": tips,
            "recovery_suggestions": health_monitor.get_recovery_suggestions(health_status)
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500

@app.route("/experience")
def experience_status():
    """Obtiene estado de la memoria experiencial"""
    try:
        exp_memory = get_experience_memory()
        summary = exp_memory.get_learning_summary()
        
        return jsonify({
            "respuesta": "🧠 Estado del Aprendizaje",
            "summary": summary
        })
    except Exception as exc:
        return jsonify({
            "respuesta": f"❌ Error al obtener experiencia: {str(exc)}"
        }), 500

@app.route("/experience/patterns")
def experience_patterns():
    """Obtiene patrones detectados"""
    try:
        exp_memory = get_experience_memory()
        patterns = exp_memory.get_patterns()
        
        return jsonify({
            "respuesta": f"🔍 Patrones Detectados ({len(patterns)})",
            "patterns": [p.to_dict() for p in patterns]
        })
    except Exception as exc:
        return jsonify({
            "respuesta": f"❌ Error al obtener patrones: {str(exc)}"
        }), 500

@app.route("/system/check-dependencies")
def check_dependencies():
    """Verifica el estado de las dependencias del sistema"""
    import subprocess
    import sys
    
    results = {
        'python': False,
        'pip': False,
        'ollama': False,
        'flask': False,
        'packages': []
    }
    
    # Verificar Python
    try:
        result = subprocess.run([sys.executable, '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            results['python'] = True
            results['python_version'] = result.stdout.strip()
    except:
        pass
    
    # Verificar pip
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            results['pip'] = True
    except:
        pass
    
    # Verificar Flask
    try:
        import flask
        results['flask'] = True
        results['flask_version'] = flask.__version__
    except:
        pass
    
    # Verificar Ollama
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            results['ollama'] = True
            # Extraer modelos instalados
            lines = result.stdout.strip().split('\n')[1:]  # Saltar header
            models = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        models.append(parts[0])
            results['models'] = models
    except:
        pass
    
    # Verificar paquetes principales
    required_packages = [
        'flask', 'flask-cors', 'python-dotenv', 'requests'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            results['packages'].append({'name': package, 'installed': True})
        except ImportError:
            results['packages'].append({'name': package, 'installed': False})
    
    return jsonify({
        'status': 'success',
        'results': results
    })

@app.route("/system/install-dependencies", methods=['POST'])
def install_dependencies():
    """Instala las dependencias automáticamente"""
    import subprocess
    import sys
    
    try:
        # Instalar desde requirements.txt
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos máximo
        )
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': '✅ Dependencias instaladas correctamente',
                'output': result.stdout[-500:]  # Últimos 500 caracteres
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '❌ Error al instalar dependencias',
                'error': result.stderr[-500:]
            }), 500
    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'error',
            'message': '⏱️  Timeout: La instalación tardó demasiado'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Error: {str(e)}'
        }), 500

@app.route("/system/check-pending-deps")
def check_pending_deps():
    """Verifica dependencias Python pendientes de instalación"""
    from agent.core.state_manager import StateManager
    from agent.actions.tools.install_dependencies import detectar_dependencias_desde_codigo
    
    try:
        state_manager = StateManager()
        codigo = state_manager.get_ultimo_codigo_generado()
        
        if not codigo:
            return jsonify({
                'status': 'success',
                'pending': [],
                'message': 'No hay código reciente'
            })
        
        # Detectar dependencias
        dependencias = detectar_dependencias_desde_codigo(codigo)
        
        # Verificar cuáles faltan
        from agent.actions.tools.install_dependencies import verificar_dependencia
        faltantes = [dep for dep in dependencias if not verificar_dependencia(dep)]
        
        return jsonify({
            'status': 'success',
            'pending': faltantes,
            'all_detected': dependencias
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route("/system/install-pending-deps", methods=['POST'])
def install_pending_deps():
    """Instala dependencias Python pendientes"""
    from agent.core.state_manager import StateManager
    from agent.actions.tools.install_dependencies import instalar_multiples_dependencias
    
    try:
        state_manager = StateManager()
        dependencias = state_manager.get_dependencias_pendientes()
        
        if not dependencias:
            return jsonify({
                'status': 'error',
                'message': 'No hay dependencias pendientes'
            }), 400
        
        # Instalar dependencias
        resultados = instalar_multiples_dependencias(dependencias)
        
        # Limpiar dependencias pendientes
        state_manager.clear_dependencias_pendientes()
        
        return jsonify({
            'status': 'success',
            'results': resultados,
            'message': f'Instalación completada: {len(resultados)} paquetes'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route("/system/check-model", methods=['POST'])
def check_model():
    """Verifica si un modelo específico está instalado en Ollama"""
    import subprocess
    
    data = request.get_json()
    model_name = data.get('model', '')
    
    if not model_name:
        return jsonify({
            'status': 'error',
            'message': 'No se especificó un modelo'
        }), 400
    
    try:
        # Ejecutar ollama list para verificar
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            # Ollama no está disponible o error
            return jsonify({
                'status': 'error',
                'message': 'Ollama no está disponible',
                'installed': False
            }), 500
        
        # Verificar si el modelo está en la lista
        # Buscar coincidencia exacta o parcial (ej: qwen2.5 coincide con qwen2.5:latest)
        lines = result.stdout.strip().split('\n')
        installed = False
        for line in lines[1:]:  # Saltar header
            if line.strip() and model_name in line:
                installed = True
                break
        
        return jsonify({
            'status': 'success',
            'installed': installed,
            'model': model_name
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'error',
            'message': 'Timeout verificando modelo',
            'installed': False
        }), 500
    except FileNotFoundError:
        return jsonify({
            'status': 'error',
            'message': 'Ollama no está instalado',
            'installed': False
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'installed': False
        }), 500

@app.route("/system/download-model", methods=['POST'])
def download_single_model():
    """Descarga un único modelo de Ollama"""
    import subprocess
    
    data = request.get_json()
    model_name = data.get('model', '')
    
    if not model_name:
        return jsonify({
            'status': 'error',
            'message': '❌ No se especificó un modelo'
        }), 400
    
    try:
        # Verificar si ya está instalado
        check = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if check.returncode == 0 and model_name in check.stdout:
            return jsonify({
                'status': 'success',
                'message': f'✅ {model_name} ya está instalado',
                'already_installed': True
            })
        
        # Descargar modelo
        result = subprocess.run(
            ['ollama', 'pull', model_name],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos máximo
        )
        
        if result.returncode == 0:
            # Refrescar modelos en Kalin
            try:
                from agent.llm.provider_manager import get_manager
                manager = get_manager()
                if 'ollama' in manager.providers:
                    ollama_provider = manager.providers['ollama']
                    if hasattr(ollama_provider, 'refresh_models'):
                        ollama_provider.refresh_models()
            except Exception as e:
                print(f"⚠️ No se pudieron refrescar modelos: {e}")
            
            return jsonify({
                'status': 'success',
                'message': f'✅ {model_name} descargado correctamente'
            })
        else:
            error_detail = result.stderr.strip() if result.stderr else 'Error desconocido'
            return jsonify({
                'status': 'error',
                'message': f'❌ Error al descargar {model_name}: {error_detail}'
            }), 500
    
    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'error',
            'message': f'⏱️ Timeout descargando {model_name} (tardó más de 10 minutos)'
        }), 500
    except FileNotFoundError:
        return jsonify({
            'status': 'error',
            'message': '❌ Ollama no está instalado'
        }), 500
    except Exception as e:
        error_msg = str(e)
        if 'certificate' in error_msg.lower() or 'ssl' in error_msg.lower():
            error_msg += '\n\n💡 Sugerencia: Ejecuta "ollama pull ' + model_name + '" en PowerShell para ver el error detallado.'
        
        return jsonify({
            'status': 'error',
            'message': f'❌ Error: {error_msg}'
        }), 500

@app.route("/system/download-models", methods=['POST'])
def download_models():
    """Descarga los modelos seleccionados de Ollama"""
    import subprocess
    
    data = request.get_json()
    selected_models = data.get('models', [])
    
    if not selected_models:
        return jsonify({
            'status': 'error',
            'message': '❌ No se seleccionaron modelos'
        }), 400
    
    results = []
    
    for model in selected_models:
        try:
            # Verificar si ya está instalado
            check = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if model in check.stdout:
                results.append({
                    'model': model,
                    'status': 'already_installed',
                    'message': f'✅ {model} ya está instalado'
                })
                continue
            
            # Descargar modelo
            result = subprocess.run(
                ['ollama', 'pull', model],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos máximo por modelo
            )
            
            if result.returncode == 0:
                results.append({
                    'model': model,
                    'status': 'success',
                    'message': f'✅ {model} descargado correctamente'
                })
            else:
                # Incluir el error detallado de Ollama
                error_detail = result.stderr.strip() if result.stderr else 'Error desconocido'
                results.append({
                    'model': model,
                    'status': 'error',
                    'message': f'❌ Error al descargar {model}: {error_detail}'
                })
        
        except subprocess.TimeoutExpired:
            results.append({
                'model': model,
                'status': 'timeout',
                'message': f'⏱️ Timeout descargando {model} (tardó más de 10 minutos)'
            })
        except Exception as e:
            error_msg = str(e)
            # Si es error de SSL/certificado, dar sugerencia
            if 'certificate' in error_msg.lower() or 'ssl' in error_msg.lower():
                error_msg += '\n\n💡 Sugerencia: Ejecuta "ollama pull ' + model + '" en PowerShell para ver el error detallado.\nPuede ser un problema de certificados SSL o proxy.'
            
            results.append({
                'model': model,
                'status': 'error',
                'message': f'❌ Error: {error_msg}'
            })
    
    # Refrescar modelos en Kalin automáticamente
    try:
        from agent.llm.provider_manager import get_manager
        manager = get_manager()
        
        # Refrescar modelos Ollama
        if 'ollama' in manager.providers:
            ollama_provider = manager.providers['ollama']
            if hasattr(ollama_provider, 'refresh_models'):
                new_models = ollama_provider.refresh_models()
                print(f"✅ Kalin detectó {len(new_models)} modelos disponibles")
    except Exception as e:
        print(f"⚠️ No se pudieron refrescar modelos en Kalin: {e}")
    
    return jsonify({
        'status': 'success',
        'results': results
    })

@app.route("/system/available-models")
def available_models():
    """Obtiene lista de modelos recomendados y populares"""
    recommended = [
        # ===== MODELOS LIGEROS (2-4GB RAM) =====
        {
            'name': 'llama3.2:1b',
            'size': '~1.3GB',
            'category': 'lightweight',
            'description': 'Modelo ultra-ligero, ideal para equipos básicos',
            'use_case': 'Tareas simples, equipos con poca RAM',
            'min_ram': '4GB'
        },
        {
            'name': 'phi3:mini',
            'size': '~2GB',
            'category': 'lightweight',
            'description': 'Modelo compacto de Microsoft, buen rendimiento',
            'use_case': 'Chat básico, tareas sencillas',
            'min_ram': '4GB'
        },
        {
            'name': 'llama3.2:3b',
            'size': '~2GB',
            'category': 'recommended',
            'description': 'Equilibrado entre tamaño y calidad',
            'use_case': 'Chat y tareas generales',
            'min_ram': '8GB'
        },
        
        # ===== MODELOS RECOMENDADOS (4-8GB RAM) =====
        {
            'name': 'deepseek-coder:6.7b',
            'size': '~4GB',
            'category': 'recommended',
            'description': 'Especializado en generación de código (Python, JS, Java, etc.)',
            'use_case': 'Generación y análisis de código',
            'min_ram': '8GB'
        },
        {
            'name': 'qwen2.5-coder:7b',
            'size': '~4.5GB',
            'category': 'recommended',
            'description': 'Excelente para programación multi-lenguaje',
            'use_case': 'Desarrollo de software',
            'min_ram': '8GB'
        },
        {
            'name': 'codellama:7b',
            'size': '~4GB',
            'category': 'popular',
            'description': 'Modelo de Meta especializado en código',
            'use_case': 'Programación y debugging',
            'min_ram': '8GB'
        },
        {
            'name': 'mistral:7b',
            'size': '~4GB',
            'category': 'popular',
            'description': 'Modelo versátil de alto rendimiento',
            'use_case': 'Tareas generales y razonamiento',
            'min_ram': '8GB'
        },
        {
            'name': 'llama3.1:8b',
            'size': '~5GB',
            'category': 'popular',
            'description': 'Última versión de Llama con mejor rendimiento',
            'use_case': 'Asistente general avanzado',
            'min_ram': '8GB'
        },
        
        # ===== MODELOS POTENTES (8-16GB RAM) =====
        {
            'name': 'gemma2:9b',
            'size': '~5.5GB',
            'category': 'latest',
            'description': 'Último modelo de Google, excelente calidad',
            'use_case': 'Tareas complejas y creativas',
            'min_ram': '16GB'
        },
        {
            'name': 'llama3.2:10b',
            'size': '~6GB',
            'category': 'high-performance',
            'description': 'Versión potente de Llama 3.2, mejor razonamiento',
            'use_case': 'Análisis complejo, razonamiento avanzado',
            'min_ram': '16GB'
        },
        {
            'name': 'qwen2.5-coder:14b',
            'size': '~9GB',
            'category': 'high-performance',
            'description': 'Versión grande de Qwen, superior en código',
            'use_case': 'Proyectos grandes, código complejo',
            'min_ram': '16GB'
        },
        {
            'name': 'mistral-nemo:12b',
            'size': '~7GB',
            'category': 'high-performance',
            'description': 'Nuevo modelo de Mistral, equilibrio perfecto',
            'use_case': 'Tareas avanzadas multi-propósito',
            'min_ram': '16GB'
        },
        
        # ===== MODELOS ULTRA-POTENTES (16GB+ RAM) =====
        {
            'name': 'llama3.3:70b',
            'size': '~40GB',
            'category': 'ultra',
            'description': '🔥 El más potente de Meta, calidad excepcional',
            'use_case': 'Tareas muy complejas, máxima calidad',
            'min_ram': '32GB+',
            'note': 'Requiere GPU potente o CPU con mucha RAM'
        },
        {
            'name': 'qwen2.5-coder:32b',
            'size': '~20GB',
            'category': 'ultra',
            'description': '🚀 Versión masiva de Qwen, state-of-the-art en código',
            'use_case': 'Desarrollo profesional, arquitecturas complejas',
            'min_ram': '32GB+',
            'note': 'Para workstations profesionales'
        },
        {
            'name': 'deepseek-coder:33b',
            'size': '~20GB',
            'category': 'ultra',
            'description': '💎 Modelo premium de DeepSeek, excelente en código',
            'use_case': 'Proyectos enterprise, código crítico',
            'min_ram': '32GB+',
            'note': 'Máxima precisión en generación de código'
        },
        {
            'name': 'mixtral:8x7b',
            'size': '~26GB',
            'category': 'ultra',
            'description': '⚡ Modelo MoE (Mixture of Experts), rápido y potente',
            'use_case': 'Tareas diversas de alta complejidad',
            'min_ram': '32GB+',
            'note': 'Arquitectura innovadora de expertos'
        }
    ]
    
    # Verificar qué modelos están instalados
    try:
        import subprocess
        
        installed_models = []
        
        # Método principal: Usar comando 'ollama list'
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Saltar header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            installed_models.append(parts[0])
            else:
                print(f"Error ejecutando ollama list: {result.stderr}")
        except FileNotFoundError:
            print("Comando 'ollama' no encontrado en PATH")
        except Exception as e:
            print(f"Error ejecutando ollama list: {e}")
        
        # Método secundario: También intentar vía API para comparar
        try:
            from agent.llm.provider_manager import get_manager
            manager = get_manager()
            
            api_models = []
            if 'ollama' in manager.providers:
                ollama_provider = manager.providers['ollama']
                if hasattr(ollama_provider, 'get_available_models'):
                    try:
                        api_models = ollama_provider.get_available_models()
                    except Exception as api_error:
                        print(f"Error usando API: {api_error}")
            
            # Si CLI no encontró nada pero API sí, usar API
            if not installed_models and api_models:
                installed_models = api_models
        except Exception as e:
            print(f"Error verificando vía API: {e}")
        
        # Marcar modelos instalados - COMPARACIÓN ESTRICTA
        installed_count = 0
        for model in recommended:
            # Comparación ESTRICTA: solo coincidencia exacta o misma familia con tag diferente
            is_installed = False
            
            for installed_model in installed_models:
                # 1. Coincidencia exacta (preferida)
                if model['name'] == installed_model:
                    is_installed = True
                    break
                
                # 2. Mismo modelo base pero con tags diferentes
                # Ejemplo: 'qwen2.5-coder:7b' vs 'qwen2.5-coder:7b-instruct'
                model_base = model['name'].split(':')[0]
                installed_base = installed_model.split(':')[0]
                
                if model_base == installed_base:
                    # Verificar que los tags sean compatibles
                    model_tag = model['name'].split(':')[1] if ':' in model['name'] else None
                    installed_tag = installed_model.split(':')[1] if ':' in installed_model else None
                    
                    # Si ambos tienen el mismo tag o uno no tiene tag, considerar instalado
                    if model_tag == installed_tag or model_tag is None or installed_tag is None:
                        is_installed = True
                        break
            
            model['installed'] = is_installed
            if is_installed:
                installed_count += 1
        
    except Exception as e:
        print(f"⚠️ ERROR al verificar modelos instalados: {e}")
        import traceback
        traceback.print_exc()
        for model in recommended:
            model['installed'] = False
    
    return jsonify({
        'status': 'success',
        'models': recommended
    })

@app.route("/system/create-venv", methods=['POST'])
def create_venv():
    """Crea un entorno virtual de Python"""
    import subprocess
    import sys
    import os
    
    try:
        venv_path = os.path.join(os.getcwd(), '.venv')
        
        # Verificar si ya existe
        if os.path.exists(venv_path):
            return jsonify({
                'status': 'warning',
                'message': f'⚠️ El entorno virtual ya existe en: {venv_path}',
                'path': venv_path
            })
        
        # Crear entorno virtual
        result = subprocess.run(
            [sys.executable, '-m', 'venv', '.venv'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': f'✅ Entorno virtual creado en: {venv_path}\n\n💡 **Próximos pasos:**\n1. Activa el entorno:\n   - Windows: `.venv\\Scripts\\activate`\n   - Linux/Mac: `source .venv/bin/activate`\n2. Instala dependencias: `pip install -r requirements.txt`',
                'path': venv_path
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '❌ Error al crear entorno virtual',
                'error': result.stderr
            }), 500
    
    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'error',
            'message': '⏱️ Timeout creando entorno virtual'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Error: {str(e)}'
        }), 500

@app.route("/system/list-models")
def list_models():
    """Lista los modelos disponibles (Locales Ollama + Nube API)"""
    import subprocess
    
    try:
        # Recargar .env para obtener configuraciones actualizadas
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        all_models = []
        
        # 1. Obtener modelos locales de Ollama
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            all_models.append(f"{parts[0]} (Local)")
        except (FileNotFoundError, Exception):
            pass # Si Ollama no está, simplemente continuamos con los de nube
        
        # 2. Obtener modelos de Nube configurados en .env (DINÁMICO)
        from agent.llm.config import LLMConfig
        cloud_providers = LLMConfig.get_configured_cloud_providers()
        
        for provider_info in cloud_providers:
            all_models.append(provider_info['display_name'])

        if not all_models:
            return jsonify({
                'status': 'error',
                'message': '❌ No hay modelos locales ni APIs de nube configuradas.'
            }), 404

        # Agregar información sobre qué proveedores están configurados (DINÁMICO)
        from agent.llm.config import LLMConfig, ProviderType
        
        providers_configured = {
            'ollama': len([m for m in all_models if '(Local)' in m]) > 0,
        }
        
        # Agregar dinámicamente todos los proveedores de nube configurados
        for provider_type in ProviderType:
            if provider_type == ProviderType.OLLAMA:
                continue
            providers_configured[provider_type.value] = LLMConfig.is_configured(provider_type)

        return jsonify({
            'status': 'success',
            'models': all_models,
            'count': len(all_models),
            'providers_configured': providers_configured
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Error al listar modelos: {str(e)}'
        }), 500

@app.route("/api/ollama/models")
def get_ollama_models():
    """Obtiene lista detallada de modelos Ollama con estado de instalación"""
    import subprocess
    
    try:
        # Lista de modelos disponibles para descargar
        available_models = [
            {'name': 'llama3.2', 'size': '3B', 'description': 'Ligero y rápido'},
            {'name': 'llama3.1', 'size': '8B', 'description': 'Balanceado'},
            {'name': 'mistral', 'size': '7B', 'description': 'Eficiente'},
            {'name': 'qwen2.5', 'size': '7B', 'description': 'Excelente para código'},
            {'name': 'codellama', 'size': '7B', 'description': 'Especializado en código'},
            {'name': 'deepseek-coder', 'size': '6.7B', 'description': 'Optimizado para programación'}
        ]
        
        # Obtener modelos instalados
        installed_models = []
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            model_name = parts[0]
                            model_size = parts[1] if len(parts) > 1 else 'Unknown'
                            installed_models.append({
                                'name': model_name,
                                'size': model_size,
                                'installed': True
                            })
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return jsonify({
                'status': 'error',
                'message': f'Ollama no está instalado o no responde: {str(e)}'
            }), 500
        
        # Marcar estado de instalación para cada modelo disponible
        for model in available_models:
            model['installed'] = any(
                model['name'] in inst['name'] or inst['name'] in model['name']
                for inst in installed_models
            )
        
        return jsonify({
            'status': 'success',
            'models': available_models,
            'installed': installed_models
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener modelos: {str(e)}'
        }), 500

@app.route("/api/ollama/delete-model", methods=['POST'])
def delete_ollama_model():
    """Borra un modelo de Ollama buscando el nombre exacto instalado"""
    import subprocess
    
    data = request.get_json()
    model_name = data.get('model', '')
    
    if not model_name:
        return jsonify({
            'status': 'error',
            'message': 'No se especificó un modelo'
        }), 400
    
    try:
        # PRIMERO: Obtener lista de modelos instalados para encontrar el nombre exacto
        result_list = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        exact_model_name = None
        if result_list.returncode == 0:
            lines = result_list.stdout.strip().split('\n')
            # Buscar modelo que coincida (puede tener tag como :latest, :7b, etc.)
            for line in lines[1:]:  # Saltar header
                if line.strip() and model_name in line:
                    # Extraer nombre completo (primera columna)
                    parts = line.split()
                    if parts:
                        exact_model_name = parts[0]
                        break
        
        # Si no se encontró el nombre exacto, usar el proporcionado
        if not exact_model_name:
            exact_model_name = model_name
        
        # Ejecutar comando ollama rm con el nombre exacto
        result = subprocess.run(
            ['ollama', 'rm', exact_model_name],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': f'Modelo {exact_model_name} borrado correctamente'
            })
        else:
            # Si falla, intentar con variaciones comunes del nombre
            common_tags = [':latest', ':7b', ':8b', ':3b', ':14b', ':72b']
            for tag in common_tags:
                if not model_name.endswith(tag):
                    alternative_name = model_name + tag
                    result_alt = subprocess.run(
                        ['ollama', 'rm', alternative_name],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    if result_alt.returncode == 0:
                        return jsonify({
                            'status': 'success',
                            'message': f'Modelo {alternative_name} borrado correctamente'
                        })
            
            # Si todas las alternativas fallan, devolver error original
            return jsonify({
                'status': 'error',
                'message': f'Error al borrar modelo: {result.stderr}'
            }), 500
    
    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'error',
            'message': 'Tiempo de espera agotado al borrar modelo'
        }), 500
    except FileNotFoundError:
        return jsonify({
            'status': 'error',
            'message': 'Ollama no está instalado'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

@app.route("/system/set-model", methods=['POST'])
def set_model():
    """Cambia el modelo activo (Local Ollama o Nube API) y guarda en .env"""
    print(f"\n{'='*60}")
    print(f"🔍 [set-model] ENDPOINT LLAMADO")
    print(f"{'='*60}")
    
    data = request.get_json()
    model_raw = data.get('model', '')
    
    print(f"🔍 [set-model] Datos recibidos: {data}")
    print(f"🔍 [set-model] model_raw: '{model_raw}'")
    
    if not model_raw:
        return jsonify({
            'status': 'error',
            'message': '❌ No se especificó un modelo'
        }), 400
    
    try:
        from agent.llm.provider_manager import get_manager
        from agent.llm.config import LLMConfig
        from dotenv import load_dotenv
        
        # Limpiar la etiqueta (ej: "grok-beta (Nube - xAI)" -> "grok-beta")
        model_name = model_raw.split(' (')[0].strip()
        
        manager = get_manager()
        
        # Detectar si es cloud basado en el parámetro provider o en el formato del nombre
        is_cloud = "(Nube" in model_raw or data.get('provider') in ['openai', 'anthropic', 'groq', 'gemini', 'mistral', 'mimo']
        
        print(f"🔍 [set-model] model_name: {model_name}, is_cloud: {is_cloud}, provider: {data.get('provider')}")
        
        # Determinar el tipo de modelo y actualizar variables de entorno
        if is_cloud:
            # Detectar proveedor por el nombre del modelo o contexto
            provider_type = "GROK"  # Default para este caso
            
            # Detectar proveedor basado en el nombre del modelo
            if 'OpenAI' in model_raw:
                provider_type = "OPENAI"
            elif 'Anthropic' in model_raw:
                provider_type = "ANTHROPIC"
            elif 'Gemini' in model_raw:
                provider_type = "GEMINI"
            elif 'Mistral' in model_raw:
                provider_type = "MISTRAL"
            elif 'MiMo' in model_raw or 'mimo' in model_raw:
                provider_type = "MIMO"
            
            print(f"🔍 [set-model] provider_type detectado: {provider_type}")
            
            env_var_model = f"{provider_type}_MODEL"
            env_var_key = f"{provider_type}_API_KEY"
            
            # Si se proporcionó una API Key, guardarla en .env
            api_key = data.get('api_key')
            if api_key:
                os.environ[env_var_key] = api_key
            
            # Verificar que tengamos la API Key
            if not os.getenv(env_var_key):
                return jsonify({
                    'status': 'error',
                    'message': f'❌ No se encontró la API Key para {provider_type}'
                }), 400
                
            os.environ[env_var_model] = model_name
            # Normalizar provider a 'groq' (aceptar 'grok' como alias)
            normalized_provider = 'groq' if provider_type.lower() in ['grok', 'groq'] else provider_type.lower()
            os.environ['ACTIVE_PROVIDER'] = normalized_provider
            
        else:
            # Es un modelo local de Ollama
            if 'ollama' in manager.providers:
                ollama_provider = manager.providers['ollama']
                if hasattr(ollama_provider, 'is_model_available'):
                    if not ollama_provider.is_model_available(model_name):
                        return jsonify({
                            'status': 'error',
                            'message': f'❌ Modelo "{model_name}" no está instalado en Ollama'
                        }), 404
            
            os.environ['OLLAMA_MODEL'] = model_name
            os.environ['ACTIVE_PROVIDER'] = 'ollama'

        # Guardar en archivo .env para persistencia
        env_path = os.path.join(os.getcwd(), '.env')
        print(f"🔍 [set-model] Guardando en .env: {env_path}")
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"🔍 [set-model] Líneas leídas: {len(lines)}")
            
            updated_lines = []
            model_updated = False
            provider_updated = False
            
            for line in lines:
                stripped = line.strip()
                # Actualizar la variable del modelo específico
                if is_cloud and (stripped.startswith(f"{provider_type}_MODEL=") or stripped.startswith(f"# {provider_type}_MODEL=")):
                    updated_lines.append(f"{env_var_model}={model_name}\n")
                    model_updated = True
                elif not is_cloud and stripped.startswith('OLLAMA_MODEL='):
                    updated_lines.append(f'OLLAMA_MODEL={model_name}\n')
                    model_updated = True
                # Actualizar la API Key si se proporcionó
                elif is_cloud and api_key and (stripped.startswith(f"{provider_type}_API_KEY=") or stripped.startswith(f"# {provider_type}_API_KEY=")):
                    updated_lines.append(f"{env_var_key}={api_key}\n")
                # Actualizar el proveedor activo
                elif stripped.startswith('ACTIVE_PROVIDER='):
                    # Normalizar a 'groq' si es 'grok'
                    current_provider = os.environ['ACTIVE_PROVIDER']
                    normalized = 'groq' if current_provider.lower() in ['grok', 'groq'] else current_provider
                    updated_lines.append(f"ACTIVE_PROVIDER={normalized}\n")
                    provider_updated = True
                else:
                    updated_lines.append(line)
            
            # Agregar líneas faltantes si no existían
            if not model_updated:
                updated_lines.append(f'{env_var_model if is_cloud else "OLLAMA_MODEL"}={model_name}\n')
            if not provider_updated:
                # Normalizar a 'groq' si es 'grok'
                current_provider = os.environ['ACTIVE_PROVIDER']
                normalized = 'groq' if current_provider.lower() in ['grok', 'groq'] else current_provider
                updated_lines.append(f'ACTIVE_PROVIDER={normalized}\n')
            # Agregar API Key si es cloud y se proporcionó pero no estaba en .env
            if is_cloud and api_key:
                print(f"🔍 [set-model] Intentando guardar API Key para {provider_type}")
                # Verificar tanto si existe la línea comentada como sin comentar
                api_key_exists = any(
                    line.strip().startswith(f"{provider_type}_API_KEY=") or 
                    line.strip().startswith(f"# {provider_type}_API_KEY=")
                    for line in lines
                )
                print(f"🔍 [set-model] API Key existe: {api_key_exists}")
                if not api_key_exists:
                    print(f"✅ [set-model] Agregando nueva línea de API Key")
                    updated_lines.append(f'{env_var_key}={api_key}\n')
                else:
                    # Si existe pero está comentada o vacía, actualizarla
                    for i, line in enumerate(updated_lines):
                        if line.strip().startswith(f"# {provider_type}_API_KEY=") or \
                           (line.startswith(f"{provider_type}_API_KEY=") and '=' in line and line.split('=')[1].strip() == ''):
                            print(f"✅ [set-model] Actualizando línea existente de API Key")
                            updated_lines[i] = f'{env_var_key}={api_key}\n'
                            break
            
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            
            print(f"✅ [set-model] Archivo .env actualizado con {len(updated_lines)} líneas")
        
        # Recargar configuración del manager para aplicar cambios inmediatamente
        load_dotenv(override=True)
        
        # Destruir el singleton del manager para que se recree con la nueva config
        import agent.llm.provider_manager as pm
        pm._manager = None  # Forzar recreación del singleton
        
        # Obtener nuevo manager con configuración actualizada
        manager = get_manager()
        
        return jsonify({
            'status': 'success',
            'message': f'✅ Modelo activado: {model_name}\nProveedor: {"Nube (" + provider_type + ")" if is_cloud else "Local (Ollama)"}',
            'model': model_name
        })
    
    except Exception as e:
        print(f"Error en set_model: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'❌ Error al cambiar modelo: {str(e)}'
        }), 500

@app.route("/system/current-model")
def current_model():
    """Obtiene el modelo actualmente activo (Local o Nube) - DINÁMICO"""
    try:
        from agent.llm.provider_manager import get_manager
        from agent.llm.config import LLMConfig, ProviderType
        import os
        import subprocess
        
        manager = get_manager()
        active_provider = os.getenv('ACTIVE_PROVIDER', 'ollama').lower()
        
        # Normalizar nombre del proveedor (aceptar 'grok' o 'groq')
        if active_provider in ['grok', 'groq']:
            active_provider = 'groq'
        
        # Determinar el modelo actual basado en el proveedor activo (DINÁMICO)
        current = None
        
        # Buscar en los proveedores configurados
        for provider_type in ProviderType:
            provider_value = provider_type.value
            
            # Si es el proveedor activo
            if active_provider == provider_value or (provider_value == 'groq' and active_provider == 'groq'):
                config = LLMConfig.PROVIDERS.get(provider_type)
                if config:
                    model_name = config.get('model', 'unknown')
                    
                    # Obtener nombre amigable del proveedor
                    display_names = {
                        'openai': 'OpenAI',
                        'anthropic': 'Anthropic',
                        'azure': 'Azure',
                        'huggingface': 'HuggingFace',
                        'groq': 'Groq',
                        'gemini': 'Gemini',
                        'mistral': 'Mistral',
                        'mimo': 'MiMo',
                    }
                    display_name = display_names.get(provider_value, provider_value.title())
                    current = f"{model_name} (Nube - {display_name})"
                    break
        
        # Si no se encontró, usar Ollama por defecto
        if not current:
            current = os.getenv('OLLAMA_MODEL', 'deepseek-coder:latest') + ' (Local)'
        
        # Obtener modelos instalados de Ollama (solo si es relevante)
        installed_models = []
        model_details = []
        
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Saltar header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            model_name = parts[0]
                            installed_models.append(model_name)
                            model_details.append({
                                'name': model_name,
                                'size': parts[1] if len(parts) > 1 else 'Unknown',
                                'installed': True
                            })
        except Exception:
            pass # Si Ollama no está, no pasa nada
        
        return jsonify({
            'status': 'success',
            'current_model': current,
            'installed_models': installed_models,
            'model_details': model_details
        })
    except Exception as e:
        print(f"❌ Error en /system/current-model: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

@app.route("/system/create-env", methods=['POST'])
def create_env_file():
    """Crea o actualiza el archivo .env con configuración completa"""
    import os
    
    try:
        env_path = os.path.join(os.getcwd(), '.env')
        
        # Verificar si ya existe
        if os.path.exists(env_path):
            # Preguntar si desea sobrescribir
            data = request.get_json() if request.is_json else {}
            overwrite = data.get('overwrite', False)
            
            if not overwrite:
                return jsonify({
                    'status': 'warning',
                    'message': '⚠️ El archivo .env ya existe. ¿Deseas sobrescribirlo?',
                    'requires_confirmation': True
                })
        
        # Obtener configuración actual
        current_model = os.getenv('OLLAMA_MODEL', 'deepseek-coder:6.7b')
        
        # Si no hay modelo configurado, detectar el mejor disponible
        if not os.getenv('OLLAMA_MODEL'):
            best_model = detect_best_model()
            if best_model:
                current_model = best_model
                os.environ['OLLAMA_MODEL'] = best_model
        
        # Crear contenido del .env
        env_content = f"""# ============================================================================
# CONFIGURACIÓN DE KALIN AI
# Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ============================================================================

# ----------------------------------------------------------------------------
# MODO DE OPERACIÓN
# ----------------------------------------------------------------------------
# local = Desarrollo (usa Ollama local, gratis)
# cloud = Producción (usa OpenAI/Anthropic, requiere API keys)
KALIN_MODE=local

# ----------------------------------------------------------------------------
# OLLAMA (LOCAL - DESARROLLO)
# ----------------------------------------------------------------------------
# Instalación: https://ollama.ai
# Modelo recomendado: deepseek-coder (gratuito, funciona offline)
OLLAMA_ENDPOINT=http://127.0.0.1:11434
OLLAMA_MODEL={current_model}

# ----------------------------------------------------------------------------
# OPENAI (CLOUD - PRODUCCIÓN) - OPCIONAL
# ----------------------------------------------------------------------------
# Obtén tu API key en: https://platform.openai.com/api-keys
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4-turbo

# ----------------------------------------------------------------------------
# ANTHROPIC / CLAUDE (CLOUD - FALLBACK) - OPCIONAL
# ----------------------------------------------------------------------------
# Obtén tu API key en: https://console.anthropic.com/
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# ----------------------------------------------------------------------------
# CONFIGURACIÓN DEL SERVIDOR FLASK
# ----------------------------------------------------------------------------
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=0  # 0 = production, 1 = development

# ----------------------------------------------------------------------------
# NOTAS IMPORTANTES
# ----------------------------------------------------------------------------
# 1. NUNCA subas este archivo a GitHub (está en .gitignore)
# 2. Las API keys deben mantenerse vacías si no las usas
# 3. Para cambiar el modelo, usa el menú lateral o edita OLLAMA_MODEL
# 4. Reinicia Kalin después de editar manualmente este archivo
"""
        
        # Guardar archivo
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        return jsonify({
            'status': 'success',
            'message': f'✅ Archivo .env creado exitosamente\n\n📄 Ubicación: {env_path}\n\n💾 Configuración guardada:\n• Modelo: {current_model}\n• Endpoint Ollama: http://127.0.0.1:11434\n• Puerto Flask: 5000\n\n🔄 Reinicia Kalin para aplicar cambios.',
            'path': env_path,
            'model_selected': current_model
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Error al crear .env: {str(e)}'
        }), 500

def detect_best_model():
    """Detecta el mejor modelo disponible basado en prioridad y versión"""
    import subprocess
    
    try:
        # Lista de modelos en orden de preferencia (más reciente/mejor primero)
        preferred_models = [
            'deepseek-coder:latest',
            'deepseek-coder:6.7b',
            'qwen2.5-coder:latest',
            'qwen2.5-coder:7b',
            'codellama:latest',
            'codellama:7b',
            'llama3.2:latest',
            'llama3.2:3b',
            'llama3.1:latest',
            'llama3.1:8b',
            'mistral:latest',
            'mistral:7b',
            'gemma2:latest',
            'gemma2:9b',
            'phi3:latest',
            'phi3:mini',
        ]
        
        # Obtener modelos instalados
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return None
        
        installed = []
        lines = result.stdout.strip().split('\n')[1:]  # Saltar header
        for line in lines:
            if line.strip():
                parts = line.split()
                if parts:
                    installed.append(parts[0])
        
        # Buscar el primer modelo preferido que esté instalado
        for preferred in preferred_models:
            # Verificar coincidencia exacta o parcial
            for inst in installed:
                if preferred.split(':')[0] in inst or inst in preferred:
                    print(f"✅ Mejor modelo detectado: {inst}")
                    return inst
        
        # Si no hay modelos preferidos, devolver el primero instalado
        if installed:
            print(f"✅ Usando primer modelo disponible: {installed[0]}")
            return installed[0]
        
        return None
        
    except Exception as e:
        print(f"⚠️ Error detectando mejor modelo: {e}")
        return None

@app.route("/system/create-shortcut", methods=['POST'])
def create_desktop_shortcut():
    """Crea un acceso directo en el escritorio para iniciar Kalin"""
    import os
    import sys
    
    try:
        # Obtener ruta del escritorio
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        
        # Ruta del script batch
        bat_path = os.path.join(os.getcwd(), 'Iniciar_Kalin.bat')
        
        # Verificar que el archivo .bat existe
        if not os.path.exists(bat_path):
            return jsonify({
                'status': 'error',
                'message': '❌ No se encontró el archivo Iniciar_Kalin.bat'
            }), 404
        
        # Crear acceso directo usando VBScript
        vbscript = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{desktop}\\Kalin.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{bat_path}"
oLink.WorkingDirectory = "{os.getcwd()}"
oLink.Description = "Kalin AI - Asistente de Programación"
oLink.IconLocation = "%SystemRoot%\\System32\\SHELL32.dll, 13"
oLink.Save
'''
        
        # Guardar script temporal
        vbs_path = os.path.join(os.getcwd(), 'create_shortcut.vbs')
        with open(vbs_path, 'w', encoding='utf-8') as f:
            f.write(vbscript)
        
        # Ejecutar VBScript
        import subprocess
        result = subprocess.run(
            ['cscript', '//nologo', vbs_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Eliminar script temporal
        if os.path.exists(vbs_path):
            os.remove(vbs_path)
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': f'✅ Acceso directo creado en el Escritorio\n\n📍 Ubicación: {desktop}\\Kalin.lnk\n\n💡 Ahora puedes iniciar Kalin con doble click en el icono del escritorio.',
                'path': os.path.join(desktop, 'Kalin.lnk')
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'❌ Error al crear acceso directo: {result.stderr}'
            }), 500
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Error: {str(e)}'
        }), 500

@app.route("/system/read-env")
def read_env_file():
    """Lee y devuelve el contenido del archivo .env"""
    import os
    
    try:
        env_path = os.path.join(os.getcwd(), '.env')
        
        if not os.path.exists(env_path):
            return jsonify({
                'status': 'error',
                'message': '❌ El archivo .env no existe. Crea uno primero desde el menú de instalación.'
            }), 404
        
        # Leer contenido del archivo
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'status': 'success',
            'content': content,
            'path': env_path
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Error al leer .env: {str(e)}'
        }), 500

@app.route("/system/update-env", methods=['POST'])
def update_env_file():
    """Actualiza el contenido del archivo .env"""
    import os
    
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({
                'status': 'error',
                'message': '❌ No se proporcionó contenido para el archivo .env'
            }), 400
        
        env_path = os.path.join(os.getcwd(), '.env')
        new_content = data['content']
        
        # Validar contenido básico (debe contener al menos algunas variables)
        if not new_content.strip():
            return jsonify({
                'status': 'error',
                'message': '❌ El contenido del archivo está vacío'
            }), 400
        
        # Guardar backup antes de actualizar
        if os.path.exists(env_path):
            backup_path = env_path + '.backup'
            import shutil
            shutil.copy2(env_path, backup_path)
        
        # Escribir nuevo contenido
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return jsonify({
            'status': 'success',
            'message': '✅ Archivo .env actualizado correctamente. Reinicia Kalin para aplicar los cambios.',
            'path': env_path
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Error al actualizar .env: {str(e)}'
        }), 500

# ==============================
# 📁 UTILS
# ==============================

def leer_archivo(ruta):
    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except:
        return None

def buscar_archivo_inteligente(query, ruta_base):
    query = query.lower().replace("/", os.sep).replace("\\", os.sep)
    query_nombre = os.path.basename(query)  # "brain.py" de "agent/core/brain.py"
    candidatos = []
    for root, _, files in os.walk(ruta_base):
        for f in files:
            nombre = f.lower()
            ruta = os.path.join(root, f)

            # Match por nombre de archivo o por ruta relativa
            ruta_relativa = os.path.relpath(ruta, ruta_base).lower().replace("\\", "/")
            match = False
            score = 0

            if query_nombre == nombre:
                score += 100
                match = True
            elif query in nombre:
                score += 50
                match = True
            elif query in ruta_relativa:
                score += 30
                match = True

            if match:
                if "main" in nombre:
                    score += 20
                if "app" in nombre:
                    score += 10
                if "test" in nombre:
                    score -= 10
                candidatos.append((score, ruta))

    if not candidatos:
        return None

    candidatos.sort(reverse=True)
    return candidatos[0][1]

def guardar_backup(ruta, contenido):
    with open(ruta + ".bak", "w", encoding="utf-8") as f:
        f.write(contenido)

def escribir_archivo(ruta, contenido):
    """Escribe contenido al archivo. Si es diff, lo aplica primero."""
    es_diff = contenido.strip().startswith("---") or contenido.strip().startswith("@@")
    
    if es_diff:
        # Lee archivo original
        try:
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                original = f.read()
            # Aplica diff (simplificado: no es un parser de diff completo)
            print(f"⚠️ Diff detectado, aplicando cambios...")
            # Por ahora, solo log - en producción usar patch library
            contenido_final = original  # Placeholder
        except:
            contenido_final = contenido
    else:
        contenido_final = contenido
    
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido_final)

def es_codigo_valido(codigo):
    if not codigo or len(codigo.strip()) < 10:
        return False
    try:
        compile(codigo, "<string>", "exec")
        return True
    except:
        return False

def limpiar_codigo(texto):
    if not texto:
        return ""
    texto = texto.replace("`python", "").replace("`", "")
    return texto.strip()

def generar_diff(original, nuevo):
    diff = difflib.unified_diff(
        original.splitlines(),
        nuevo.splitlines(),
        lineterm=""
    )
    return "\n".join(diff)


def aplicar_diff(codigo_original: str, diff_text: str) -> str:
    """Aplica un diff unificado a un código y devuelve el resultado"""
    try:
        import difflib
        lines = diff_text.strip().split('\n')
        
        # Extrae las líneas del diff (saltando headers)
        resultado = codigo_original.split('\n')
        offset = 0
        
        for linea in lines:
            if linea.startswith('@@'):
                # Parse @@ -start,count +start,count @@
                continue
            elif linea.startswith('-') and not linea.startswith('---'):
                # Línea a eliminar
                try:
                    idx = int(linea.split()[0][1:]) - 1 + offset
                    if 0 <= idx < len(resultado):
                        resultado.pop(idx)
                        offset -= 1
                except:
                    pass
            elif linea.startswith('+') and not linea.startswith('+++'):
                # Línea a añadir
                try:
                    idx = int(linea.split()[0][1:]) + offset
                    resultado.insert(idx, linea[1:])
                    offset += 1
                except:
                    pass
        
        return '\n'.join(resultado)
    except Exception as e:
        print(f"⚠️ Error aplicando diff: {e}")
        return ""

# ==============================
# 🧠 API
# ==============================

@app.route("/chat", methods=["POST"])
def chat():
    global RUTA_PROYECTO, ULTIMO_FIX

    data = request.json or {}
    mensaje = (data.get("mensaje") or data.get("command") or data.get("message") or "").strip()
    
    # Obtener o generar session_id para mantener contexto conversacional
    session_id = data.get("session_id")
    if not session_id:
        import time
        session_id = f"session_{int(time.time())}"

    estado = {
        "ruta_proyecto": RUTA_PROYECTO,
        "ultimo_fix": ULTIMO_FIX,
        "session_id": session_id
    }

    utils = {
        "leer_archivo": leer_archivo,
        "buscar_archivo_inteligente": buscar_archivo_inteligente,
        "limpiar_codigo": limpiar_codigo,
        "generar_diff": generar_diff,
        "es_codigo_valido": es_codigo_valido,
        "guardar_backup": guardar_backup,
        "escribir_archivo": escribir_archivo,
        "analizar_codigo": analizar_codigo,
        "jsonify": jsonify
    }

    try:
        # Usar la nueva capa de orquestación
        from agent.core.orchestration_layer import get_orchestration_layer
        orchestration = get_orchestration_layer()
        
        # Procesar a través de la capa de orquestación
        response_data = orchestration.process_request(mensaje, estado, utils)
        
        # Incluir session_id en la respuesta
        response_data['session_id'] = session_id
        
        return jsonify(response_data)
        
    except ImportError as import_err:
        logger.error(f"❌ Error de importación: {import_err}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "respuesta": f"❌ Error de importación: {str(import_err)}",
            "session_id": session_id,
            "error_details": str(import_err)
        }), 500
    except Exception as exc:
        logger.error(f"❌ Error interno en /chat: {exc}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "respuesta": f"❌ Error interno: {str(exc)}",
            "session_id": session_id,
            "error_type": type(exc).__name__,
            "error_details": str(exc)
        }), 500

    RUTA_PROYECTO = estado.get("ruta_proyecto", RUTA_PROYECTO)
    ULTIMO_FIX = estado.get("ultimo_fix", ULTIMO_FIX)

# ==============================
# 📦 EXPERIENCE EXPORT/IMPORT
# ==============================

@app.route("/experience/export")
def export_experience():
    """Exporta la experiencia de Kalin como archivo JSON descargable"""
    try:
        from agent.core.experience_memory import ExperienceMemory
        exp_mem = ExperienceMemory()
        
        # Obtener todos los datos de experiencia
        experience_data = {
            'experiences': exp_mem.get_all_experiences(),
            'patterns': exp_mem.get_all_patterns(),
            'statistics': exp_mem.get_statistics(),
            'exported_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        # Crear respuesta JSON descargable
        response = jsonify(experience_data)
        response.headers['Content-Disposition'] = f'attachment; filename=kalin_experience_{datetime.now().strftime("%Y%m%d")}.json'
        return response
        
    except Exception as e:
        logger.error(f"Error exportando experiencia: {e}")
        return jsonify({
            'status': 'error',
            'message': f'❌ Error al exportar experiencia: {str(e)}'
        }), 500

@app.route("/experience/import", methods=['POST'])
def import_experience():
    """Importa experiencia desde un archivo JSON"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': '❌ No se proporcionó archivo'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': '❌ Nombre de archivo vacío'
            }), 400
        
        # Leer y parsear JSON
        import json
        data = json.load(file)
        
        # Validar estructura
        if 'experiences' not in data and 'patterns' not in data:
            return jsonify({
                'status': 'error',
                'message': '❌ Archivo no válido: debe contener experiencias o patrones'
            }), 400
        
        # Importar experiencias
        from agent.core.experience_memory import ExperienceMemory
        exp_mem = ExperienceMemory()
        
        imported_count = 0
        if 'experiences' in data:
            for exp in data['experiences']:
                exp_mem.add_experience(exp)
                imported_count += 1
        
        if 'patterns' in data:
            for pattern in data['patterns']:
                exp_mem.add_pattern(pattern)
                imported_count += 1
        
        return jsonify({
            'status': 'success',
            'message': f'✅ Se importaron {imported_count} elementos de experiencia',
            'imported_count': imported_count
        })
        
    except Exception as e:
        logger.error(f"Error importando experiencia: {e}")
        return jsonify({
            'status': 'error',
            'message': f'❌ Error al importar experiencia: {str(e)}'
        }), 500

# ==============================
# ⚙️ DEPENDENCY MANAGEMENT
# ==============================

@app.route("/system/install-deps", methods=['POST'])
def install_deps_quick():
    """Instala dependencias desde requirements.txt (versión rápida)"""
    try:
        import subprocess
        import sys
        
        # Verificar que existe requirements.txt
        req_file = os.path.join(os.getcwd(), 'requirements.txt')
        if not os.path.exists(req_file):
            return jsonify({
                'status': 'error',
                'message': '❌ requirements.txt no encontrado'
            }), 404
        
        # Ejecutar pip install
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', req_file],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos timeout
        )
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': '✅ Dependencias instaladas correctamente'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'❌ Error instalando dependencias:\n{result.stderr}'
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'error',
            'message': '❌ Timeout: La instalación tardó demasiado'
        }), 500
    except Exception as e:
        logger.error(f"Error instalando dependencias: {e}")
        return jsonify({
            'status': 'error',
            'message': f'❌ Error: {str(e)}'
        }), 500

# ==============================
# 🚀 START
# ==============================

if __name__ == "__main__":
    # Configuración desde .env con valores seguros por defecto
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes')
    
    print("🚀 Iniciando servidor...")
    print(f"📍 Host: {host}")
    print(f"📍 Puerto: {port}")
    print(f"📍 Debug: {debug}")
    print(f"📍 URL: http://{host}:{port}")
    print("📍 Rutas: /, /help, /chat, /llm-status, /health, /system-status")
    
    # SEGURIDAD: Validar configuración antes de iniciar
    if host == '0.0.0.0' and not debug:
        print("\n⚠️  ADVERTENCIA: Servidor expuesto a todas las interfaces")
        print("   Para producción, usa un reverse proxy (nginx) con HTTPS")
    
    app.run(host=host, port=port, debug=debug)