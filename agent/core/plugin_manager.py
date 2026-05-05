"""
Sistema de Plugins Dinámicos para Kalin.
Permite cargar, recargar y gestionar plugins en tiempo de ejecución.
"""

import os
import sys
import importlib
import inspect
from typing import Dict, List, Optional, Type, Any
from pathlib import Path
from agent.core.logger import get_logger
from agent.actions.commands.base import BaseCommand
from agent.core.security_hardening import PluginValidator

logger = get_logger('kalin.plugins')

class PluginMetadata:
    """Metadatos de un plugin"""
    
    def __init__(self, name: str, version: str, description: str, author: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.author = author
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author
        }

class Plugin:
    """Clase base para todos los plugins"""
    
    metadata: PluginMetadata = None
    
    def on_load(self):
        """Se llama cuando el plugin se carga"""
        pass
    
    def on_unload(self):
        """Se llama cuando el plugin se descarga"""
        pass
    
    def get_commands(self) -> List[BaseCommand]:
        """Retorna lista de comandos que proporciona este plugin"""
        return []
    
    def get_hooks(self) -> Dict[str, callable]:
        """Retorna hooks/eventos que este plugin maneja"""
        return {}

class PluginManager:
    """Gestiona la carga, descarga y ciclo de vida de plugins"""
    
    def __init__(self, plugins_dir: str = None):
        if plugins_dir is None:
            plugins_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'plugins'
            )
        
        self.plugins_dir = plugins_dir
        os.makedirs(plugins_dir, exist_ok=True)
        
        # Agregar directorio de plugins al path
        if plugins_dir not in sys.path:
            sys.path.insert(0, plugins_dir)
        
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_modules: Dict[str, Any] = {}
        self._hooks_registry: Dict[str, List[callable]] = {}
        
        logger.info(f"PluginManager initialized: {plugins_dir}")
    
    def discover_plugins(self) -> List[str]:
        """Descubre todos los plugins disponibles en el directorio"""
        plugins = []
        
        if not os.path.exists(self.plugins_dir):
            return plugins
        
        for item in os.listdir(self.plugins_dir):
            item_path = os.path.join(self.plugins_dir, item)
            
            # Buscar archivos .py o directorios con __init__.py
            if item.endswith('.py') and not item.startswith('_'):
                plugin_name = item[:-3]  # Remover .py
                plugins.append(plugin_name)
            
            elif os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, '__init__.py')):
                plugins.append(item)
        
        logger.info(f"Discovered {len(plugins)} plugins")
        return plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Carga un plugin específico con validación de seguridad"""
        try:
            # VALIDACIÓN DE SEGURIDAD: Verificar plugin antes de cargar
            plugin_file = os.path.join(self.plugins_dir, f"{plugin_name}.py")
            if os.path.exists(plugin_file):
                is_safe, alerts = PluginValidator.validate_plugin_code(plugin_file)
                
                if not is_safe:
                    logger.error(f"Plugin blocked due to security concerns: {plugin_name}")
                    for alert in alerts:
                        logger.error(f"  - {alert}")
                    return False
                
                if alerts:
                    logger.warning(f"Plugin {plugin_name} has security warnings:")
                    for alert in alerts:
                        logger.warning(f"  - {alert}")
            
            # Importar módulo del plugin
            module = importlib.import_module(plugin_name)
            
            # Buscar clase Plugin en el módulo
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Plugin) and 
                    obj != Plugin):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                logger.error(f"No Plugin class found in {plugin_name}")
                return False
            
            # Instanciar plugin
            plugin_instance = plugin_class()
            
            # Validar metadatos
            if not plugin_instance.metadata:
                logger.warning(f"Plugin {plugin_name} has no metadata")
            
            # Llamar hook de carga
            plugin_instance.on_load()
            
            # Registrar plugin
            self._plugins[plugin_name] = plugin_instance
            self._plugin_modules[plugin_name] = module
            
            # Registrar comandos del plugin
            commands = plugin_instance.get_commands()
            for command in commands:
                logger.info(f"Plugin {plugin_name} provides command: {command.__class__.__name__}")
            
            # Registrar hooks del plugin
            hooks = plugin_instance.get_hooks()
            for hook_name, hook_func in hooks.items():
                if hook_name not in self._hooks_registry:
                    self._hooks_registry[hook_name] = []
                self._hooks_registry[hook_name].append(hook_func)
            
            logger.info(f"Plugin loaded successfully: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Descarga un plugin"""
        if plugin_name not in self._plugins:
            logger.warning(f"Plugin not loaded: {plugin_name}")
            return False
        
        try:
            plugin = self._plugins[plugin_name]
            
            # Llamar hook de descarga
            plugin.on_unload()
            
            # Eliminar plugin
            del self._plugins[plugin_name]
            del self._plugin_modules[plugin_name]
            
            logger.info(f"Plugin unloaded: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Recarga un plugin (hot-reload)"""
        logger.info(f"Reloading plugin: {plugin_name}")
        
        # Descargar
        if plugin_name in self._plugins:
            self.unload_plugin(plugin_name)
        
        # Recargar módulo
        if plugin_name in self._plugin_modules:
            importlib.reload(self._plugin_modules[plugin_name])
        
        # Cargar nuevamente
        return self.load_plugin(plugin_name)
    
    def load_all_plugins(self):
        """Carga todos los plugins disponibles"""
        plugins = self.discover_plugins()
        
        loaded = 0
        failed = 0
        
        for plugin_name in plugins:
            if self.load_plugin(plugin_name):
                loaded += 1
            else:
                failed += 1
        
        logger.info(f"Loaded {loaded} plugins, {failed} failed")
    
    def trigger_hook(self, hook_name: str, *args, **kwargs):
        """Ejecuta todos los hooks registrados para un evento"""
        if hook_name not in self._hooks_registry:
            return
        
        results = []
        for hook_func in self._hooks_registry[hook_name]:
            try:
                result = hook_func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Hook {hook_name} failed: {e}")
        
        return results
    
    def list_plugins(self) -> List[Dict]:
        """Lista todos los plugins cargados"""
        result = []
        
        for name, plugin in self._plugins.items():
            info = {
                'name': name,
                'loaded': True,
                'metadata': plugin.metadata.to_dict() if plugin.metadata else None
            }
            result.append(info)
        
        return result
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Obtiene una instancia de plugin"""
        return self._plugins.get(plugin_name)
    
    def get_all_commands(self) -> List[BaseCommand]:
        """Obtiene todos los comandos de todos los plugins"""
        all_commands = []
        
        for plugin in self._plugins.values():
            commands = plugin.get_commands()
            all_commands.extend(commands)
        
        return all_commands

# Instancia global
plugin_manager = PluginManager()
