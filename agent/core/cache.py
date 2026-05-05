"""
Sistema de caché inteligente para Kalin.
Caché de archivos analizados y respuestas LLM para mejorar rendimiento.
"""

import os
import json
import hashlib
import time
from typing import Any, Optional, Dict
from pathlib import Path
from agent.core.logger import get_logger

logger = get_logger('kalin.cache')

class CacheEntry:
    """Entrada individual del caché"""
    
    def __init__(self, key: str, value: Any, ttl: int = 3600):
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl  # Time to live en segundos
        self.access_count = 0
    
    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado"""
        return (time.time() - self.created_at) > self.ttl
    
    def access(self):
        """Registra un acceso"""
        self.access_count += 1
        self.last_accessed = time.time()

class SmartCache:
    """Caché inteligente con TTL y métricas"""
    
    def __init__(self, max_size: int = 1000, storage_dir: str = None):
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        
        if storage_dir is None:
            storage_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'cache'
            )
        
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0
        }
        
        logger.info(f"SmartCache initialized: max_size={max_size}, storage={storage_dir}")
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché"""
        self.stats['total_requests'] += 1
        
        if key not in self._cache:
            self.stats['misses'] += 1
            return None
        
        entry = self._cache[key]
        
        if entry.is_expired():
            self._remove(key)
            self.stats['misses'] += 1
            return None
        
        entry.access()
        self.stats['hits'] += 1
        
        logger.debug(f"Cache HIT: {key}")
        return entry.value
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Establece un valor en el caché"""
        # Eviction si está lleno
        if len(self._cache) >= self.max_size:
            self._evict()
        
        entry = CacheEntry(key, value, ttl)
        self._cache[key] = entry
        
        logger.debug(f"Cache SET: {key}, ttl={ttl}s")
    
    def _remove(self, key: str):
        """Elimina una entrada del caché"""
        if key in self._cache:
            del self._cache[key]
    
    def _evict(self):
        """Elimina la entrada menos usada (LFU)"""
        if not self._cache:
            return
        
        # Encontrar la entrada con menos accesos
        min_key = min(self._cache.keys(), key=lambda k: self._cache[k].access_count)
        self._remove(min_key)
        self.stats['evictions'] += 1
        
        logger.debug(f"Cache EVICT: {min_key}")
    
    def clear(self):
        """Limpia todo el caché"""
        self._cache.clear()
        self.stats['hits'] = 0
        self.stats['misses'] = 0
        self.stats['evictions'] = 0
        self.stats['total_requests'] = 0
        
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del caché"""
        hit_rate = (
            (self.stats['hits'] / self.stats['total_requests'] * 100)
            if self.stats['total_requests'] > 0 else 0
        )
        
        return {
            **self.stats,
            'size': len(self._cache),
            'hit_rate': f"{hit_rate:.2f}%"
        }
    
    def save_to_disk(self):
        """Guarda el caché en disco"""
        try:
            cache_file = os.path.join(self.storage_dir, 'cache.json')
            
            cache_data = {
                'entries': {
                    k: {
                        'value': v.value,
                        'created_at': v.created_at,
                        'ttl': v.ttl,
                        'access_count': v.access_count
                    }
                    for k, v in self._cache.items()
                },
                'stats': self.stats,
                'timestamp': time.time()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Cache saved to disk: {len(self._cache)} entries")
            
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def load_from_disk(self):
        """Carga el caché desde disco"""
        try:
            cache_file = os.path.join(self.storage_dir, 'cache.json')
            
            if not os.path.exists(cache_file):
                return
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            self._cache = {
                k: CacheEntry(
                    key=k,
                    value=v['value'],
                    ttl=v['ttl']
                )
                for k, v in cache_data.get('entries', {}).items()
            }
            
            self.stats = cache_data.get('stats', self.stats)
            
            # Limpiar expirados
            expired = [k for k, v in self._cache.items() if v.is_expired()]
            for key in expired:
                self._remove(key)
            
            logger.info(f"Cache loaded from disk: {len(self._cache)} entries")
            
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")

class AnalysisCache(SmartCache):
    """Caché específico para análisis de código"""
    
    def __init__(self, storage_dir=None):
        if storage_dir is None:
            storage_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'cache'
            )
        super().__init__(max_size=500, storage_dir=storage_dir)
        self.load_from_disk()
    
    def get_analysis(self, file_path: str, file_hash: str) -> Optional[str]:
        """Obtiene análisis caché de un archivo"""
        key = f"analysis:{file_hash}:{os.path.getmtime(file_path)}"
        return self.get(key)
    
    def set_analysis(self, file_path: str, file_hash: str, analysis: str, ttl: int = 7200):
        """Guarda análisis de un archivo"""
        key = f"analysis:{file_hash}:{os.path.getmtime(file_path)}"
        self.set(key, analysis, ttl)
        self.save_to_disk()

class LLMCache(SmartCache):
    """Caché específico para respuestas LLM"""
    
    def __init__(self, storage_dir=None):
        if storage_dir is None:
            storage_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'cache'
            )
        super().__init__(max_size=1000, storage_dir=storage_dir)
    
    def get_response(self, prompt: str, model: str) -> Optional[str]:
        """Obtiene respuesta LLM caché"""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        key = f"llm:{model}:{prompt_hash}"
        return self.get(key)
    
    def set_response(self, prompt: str, model: str, response: str, ttl: int = 86400):
        """Guarda respuesta LLM"""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        key = f"llm:{model}:{prompt_hash}"
        self.set(key, response, ttl)

# Instancias globales
analysis_cache = AnalysisCache()
llm_cache = LLMCache()
