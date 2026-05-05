import builtins
from typing import Dict, List, Any, Optional
import os
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
debug = os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes')

print("🚀 Iniciando servidor (run.py)...")
print(f"📍 Host: {host}")
print(f"📍 Puerto: {port}")
print(f"📍 Debug: {debug}")
print(f"📍 URL: http://{host}:{port}")

# SEGURIDAD: Advertencia si se expone públicamente
if host == '0.0.0.0' and not debug:
    print("\n⚠️  ADVERTENCIA: Servidor expuesto a todas las interfaces")
    print("   Para producción, usa un reverse proxy (nginx) con HTTPS")

web.app.run(host=host, port=port, debug=debug)