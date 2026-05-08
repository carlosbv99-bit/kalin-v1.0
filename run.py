import builtins
from typing import Dict, List, Any, Optional
import os
import webbrowser
import threading
import time
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# monkey patch typing
builtins.Dict = Dict
builtins.List = List
builtins.Any = Any
builtins.Optional = Optional

# importar app
import web

# Configuración desde .env
host = os.getenv('FLASK_HOST', '127.0.0.1')
port = int(os.getenv('FLASK_PORT', '5000'))
debug = False  # FORZADO A FALSE - Sin reinicios automáticos

def open_browser():
    """Abrir navegador automaticamente despues de iniciar"""
    time.sleep(2)  # Esperar a que el servidor inicie
    webbrowser.open(f'http://{host}:{port}')

print("\n" + "="*60)
print("  KALIN AI - ASISTENTE DE PROGRAMACION")
print("="*60)
print(f"\n🚀 Iniciando servidor...")
print(f"📍 Host: {host}")
print(f"📍 Puerto: {port}")
print(f"📍 Debug: {debug}")
print(f"📍 URL: http://{host}:{port}")
print("\n💡 El navegador se abrira automaticamente en 2 segundos...")
print("   Si no se abre, visita manualmente la URL de arriba")
print("\n⚠️  Presiona Ctrl+C para detener Kalin")
print("="*60 + "\n")

# SEGURIDAD: Advertencia si se expone publicamente
if host == '0.0.0.0' and not debug:
    print("\n⚠️  ADVERTENCIA: Servidor expuesto a todas las interfaces")
    print("   Para produccion, usa un reverse proxy (nginx) con HTTPS\n")

# Abrir navegador en un hilo separado
# DESACTIVADO TEMPORALMENTE - Evitar envío automático de mensajes
# browser_thread = threading.Thread(target=open_browser)
# browser_thread.daemon = True
# browser_thread.start()

# Iniciar servidor Flask
web.app.run(host=host, port=port, debug=debug)