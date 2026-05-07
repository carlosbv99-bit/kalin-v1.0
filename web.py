from dotenv import load_dotenv
load_dotenv()  # Cargar .env ANTES de cualquier import

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import difflib

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

MODO_SEGURO = True
RUTA_PROYECTO = ""
ULTIMO_FIX = None

# ==============================
# 🌐 WEB
# ==============================

@app.route("/")
def home():
    return render_template("index.html")

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
                results.append({
                    'model': model,
                    'status': 'error',
                    'message': f'❌ Error al descargar {model}'
                })
        
        except subprocess.TimeoutExpired:
            results.append({
                'model': model,
                'status': 'timeout',
                'message': f'⏱️  Timeout descargando {model}'
            })
        except Exception as e:
            results.append({
                'model': model,
                'status': 'error',
                'message': f'❌ Error: {str(e)}'
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
        {
            'name': 'deepseek-coder:6.7b',
            'size': '~4GB',
            'category': 'recommended',
            'description': 'Especializado en generación de código (Python, JS, Java, etc.)',
            'use_case': 'Generación y análisis de código'
        },
        {
            'name': 'llama3.2:3b',
            'size': '~2GB',
            'category': 'recommended',
            'description': 'Modelo ligero para conversación y tareas generales',
            'use_case': 'Chat y asistencia conversacional'
        },
        {
            'name': 'qwen2.5-coder:7b',
            'size': '~4.5GB',
            'category': 'recommended',
            'description': 'Excelente para programación multi-lenguaje',
            'use_case': 'Desarrollo de software'
        },
        {
            'name': 'codellama:7b',
            'size': '~4GB',
            'category': 'popular',
            'description': 'Modelo de Meta especializado en código',
            'use_case': 'Programación y debugging'
        },
        {
            'name': 'mistral:7b',
            'size': '~4GB',
            'category': 'popular',
            'description': 'Modelo versátil de alto rendimiento',
            'use_case': 'Tareas generales y razonamiento'
        },
        {
            'name': 'llama3.1:8b',
            'size': '~5GB',
            'category': 'popular',
            'description': 'Última versión de Llama con mejor rendimiento',
            'use_case': 'Asistente general avanzado'
        },
        {
            'name': 'phi3:mini',
            'size': '~2GB',
            'category': 'lightweight',
            'description': 'Modelo ultra-ligero de Microsoft',
            'use_case': 'Equipos con recursos limitados'
        },
        {
            'name': 'gemma2:9b',
            'size': '~5.5GB',
            'category': 'latest',
            'description': 'Último modelo de Google, excelente calidad',
            'use_case': 'Tareas complejas y creativas'
        }
    ]
    
    # Verificar qué modelos están instalados
    try:
        from agent.llm.provider_manager import get_manager
        manager = get_manager()
        
        installed_models = []
        if 'ollama' in manager.providers:
            ollama_provider = manager.providers['ollama']
            if hasattr(ollama_provider, 'get_available_models'):
                installed_models = ollama_provider.get_available_models()
        
        # Marcar modelos instalados
        for model in recommended:
            model['installed'] = any(
                model['name'] in installed or installed in model['name']
                for installed in installed_models
            )
    except Exception as e:
        print(f"⚠️ No se pudo verificar modelos instalados: {e}")
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

@app.route("/system/set-model", methods=['POST'])
def set_model():
    """Cambia el modelo activo de Ollama y guarda en .env"""
    data = request.get_json()
    model_name = data.get('model', '')
    
    if not model_name:
        return jsonify({
            'status': 'error',
            'message': '❌ No se especificó un modelo'
        }), 400
    
    try:
        from agent.llm.provider_manager import get_manager
        from agent.llm.config import LLMConfig
        
        manager = get_manager()
        
        # Verificar que el modelo está disponible
        if 'ollama' in manager.providers:
            ollama_provider = manager.providers['ollama']
            if hasattr(ollama_provider, 'is_model_available'):
                if not ollama_provider.is_model_available(model_name):
                    return jsonify({
                        'status': 'error',
                        'message': f'❌ Modelo "{model_name}" no está instalado en Ollama'
                    }), 404
        
        # Actualizar variable de entorno
        os.environ['OLLAMA_MODEL'] = model_name
        
        # Guardar en archivo .env para persistencia
        env_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_path):
            # Leer contenido actual
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Buscar y actualizar línea OLLAMA_MODEL
            updated = False
            new_lines = []
            for line in lines:
                if line.startswith('OLLAMA_MODEL='):
                    new_lines.append(f'OLLAMA_MODEL={model_name}\n')
                    updated = True
                else:
                    new_lines.append(line)
            
            # Si no existía, agregarla
            if not updated:
                new_lines.append(f'\nOLLAMA_MODEL={model_name}\n')
            
            # Escribir archivo actualizado
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        
        # Recargar configuración del manager
        manager.config = LLMConfig()
        
        # Actualizar modelo en el proveedor Ollama
        if 'ollama' in manager.providers:
            manager.providers['ollama'].model = model_name
        
        return jsonify({
            'status': 'success',
            'message': f'✅ Modelo cambiado a: {model_name}\n\n💾 Configuración guardada permanentemente.\nKalin usará este modelo incluso después de reiniciar.',
            'model': model_name
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Error al cambiar modelo: {str(e)}'
        }), 500

@app.route("/system/current-model")
def current_model():
    """Obtiene el modelo actualmente activo y lista de instalados con detalles"""
    try:
        from agent.llm.provider_manager import get_manager
        import os
        import subprocess
        
        manager = get_manager()
        
        current = os.getenv('OLLAMA_MODEL', 'deepseek-coder:6.7b')
        
        # Forzar refresh de modelos Ollama
        installed_models = []
        model_details = []
        
        print("🔍 Buscando modelos instalados en Ollama...")
        
        # Método 1: Usar API de Ollama a través del proveedor
        if 'ollama' in manager.providers:
            ollama_provider = manager.providers['ollama']
            # Forzar actualización de la lista de modelos
            if hasattr(ollama_provider, 'refresh_models'):
                try:
                    installed_models = ollama_provider.refresh_models()
                    print(f"✅ Modelos desde API: {installed_models}")
                except Exception as e:
                    print(f"⚠️ Error usando API: {e}")
            elif hasattr(ollama_provider, 'get_available_models'):
                installed_models = ollama_provider.get_available_models()
                print(f"✅ Modelos desde cache: {installed_models}")
        else:
            print("⚠️ Proveedor Ollama no encontrado")
        
        # Método 2: Usar CLI de Ollama como respaldo
        try:
            print("🔍 Verificando con 'ollama list'...")
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Saltar header
                cli_models = []
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            model_name = parts[0]
                            model_size = parts[1] if len(parts) > 1 else 'Unknown'
                            model_details.append({
                                'name': model_name,
                                'size': model_size,
                                'installed': True
                            })
                            cli_models.append(model_name)
                            # Agregar a installed_models si no está
                            if model_name not in installed_models:
                                installed_models.append(model_name)
                print(f"✅ Modelos detectados desde CLI: {cli_models}")
            else:
                print(f"⚠️ Error en CLI: {result.stderr}")
        except FileNotFoundError:
            print("❌ Comando 'ollama' no encontrado. ¿Está instalado?")
        except Exception as e:
            print(f"⚠️ Error obteniendo detalles de modelos: {e}")
        
        print(f"📊 Total modelos encontrados: {len(installed_models)}")
        print(f"📊 Modelos: {installed_models}")
        
        return jsonify({
            'status': 'success',
            'current_model': current,
            'installed_models': installed_models,
            'model_details': model_details if model_details else [{'name': m, 'size': 'Unknown', 'installed': True} for m in installed_models]
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

    estado = {
        "ruta_proyecto": RUTA_PROYECTO,
        "ultimo_fix": ULTIMO_FIX
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
        response = orchestrator.handle(mensaje, estado, utils)
    except Exception as exc:
        return jsonify({"respuesta": f"❌ Error interno: {str(exc)}"}), 500

    RUTA_PROYECTO = estado.get("ruta_proyecto", RUTA_PROYECTO)
    ULTIMO_FIX = estado.get("ultimo_fix", ULTIMO_FIX)

    return response

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