import builtins
from typing import Dict, List, Any, Optional

# monkey patch typing
builtins.Dict = Dict
builtins.List = List
builtins.Any = Any
builtins.Optional = Optional

# importar app
import web

print("🚀 Iniciando servidor (run.py)...")

web.app.run(host="0.0.0.0", port=5000, debug=False)