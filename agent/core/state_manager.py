"""
Estado mínimo y persistente del agente.
- Último archivo procesado
- Ruta del proyecto
- Último fix (para /apply)
- Estrategia activa
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

STATE_FILE = ".agent_state.json"

class StateManager:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.state_file = os.path.join(base_path, STATE_FILE)
        self.memory: Dict[str, Any] = {
            "ruta_proyecto": None,
            "ultimo_archivo": None,
            "ultimo_fix": None,
            "ultimo_codigo_generado": None,  # Código generado por /create
            "estrategia_activa": "smart",  # smart, aggressive, conservative
            "contador_fallos": 0,
            "contador_exitos": 0,
        }
        self._cargar()

    def _cargar(self):
        """Carga estado desde disco si existe"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                    self.memory.update(datos)
            except Exception:
                pass  # Si falla, mantiene valores por defecto

    def guardar(self):
        """Persiste estado a disco"""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2)
        except Exception:
            pass  # Silent fail - no bloquear operación

    def set_ruta(self, ruta: str):
        """Configura ruta del proyecto"""
        if os.path.isdir(ruta):
            self.memory["ruta_proyecto"] = os.path.abspath(ruta)
            self.guardar()
            return True
        return False

    def get_ruta(self) -> Optional[str]:
        return self.memory.get("ruta_proyecto")

    def set_ultimo_archivo(self, ruta: str, codigo: str):
        """Registra último archivo procesado"""
        self.memory["ultimo_archivo"] = {
            "ruta": ruta,
            "primeras_lineas": codigo[:300]  # Preview
        }
        self.guardar()

    def set_ultimo_fix(self, ruta: str, original: str, nuevo: str):
        """Registra último fix (para /apply)"""
        self.memory["ultimo_fix"] = {
            "ruta": ruta,
            "codigo_original": original,
            "codigo_nuevo": nuevo,
        }
        self.guardar()

    def get_ultimo_fix(self) -> Optional[Dict]:
        return self.memory.get("ultimo_fix")

    def clear_ultimo_fix(self):
        """Limpia fix pendiente (después de /apply)"""
        self.memory["ultimo_fix"] = None
        self.guardar()

    def registrar_exito(self):
        self.memory["contador_exitos"] += 1
        self.guardar()

    def registrar_fallo(self):
        self.memory["contador_fallos"] += 1
        # Cambiar a estrategia más agresiva si muchos fallos
        if self.memory["contador_fallos"] > 2:
            self.memory["estrategia_activa"] = "aggressive"
        self.guardar()

    def reset_contadores(self):
        self.memory["contador_fallos"] = 0
        self.memory["contador_exitos"] = 0
        self.memory["estrategia_activa"] = "smart"
        self.guardar()

    def get_estado(self) -> Dict[str, Any]:
        """Retorna estado actual (para debug)"""
        return self.memory.copy()
    
    def get_ultimo_archivo(self) -> Optional[Dict]:
        """Obtiene último archivo procesado"""
        return self.memory.get("ultimo_archivo")
    
    def set_ultimo_codigo_generado(self, codigo: str):
        """Guarda el último código generado por /create"""
        self.memory["ultimo_codigo_generado"] = codigo
        self.guardar()
    
    def get_ultimo_codigo_generado(self) -> Optional[str]:
        """Obtiene el último código generado"""
        return self.memory.get("ultimo_codigo_generado")
    
    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas de éxitos y fallos"""
        return {
            "exitos": self.memory.get("contador_exitos", 0),
            "fallos": self.memory.get("contador_fallos", 0)
        }
