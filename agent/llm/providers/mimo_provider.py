"""
Xiaomi MiMo Provider - Modelos de Xiaomi MiMo
Soporta: mimo-v2-flash, mimo-v2-pro
API disponible en: https://platform.xiaomimimo.com/
Compatible con formato OpenAI
"""

from .base_provider import BaseLLMProvider
import os


class MimoProvider(BaseLLMProvider):
    """Proveedor para Xiaomi MiMo API"""
    
    def __init__(self, config=None):
        super().__init__(config or {})
        self.api_key = os.getenv('MIMO_API_KEY', '')
        self.base_url = os.getenv('MIMO_BASE_URL', 'https://api.xiaomimimo.com/v1')
        
        # Modelos disponibles
        self.available_models = [
            'mimo-v2-flash',
            'mimo-v2-pro',
        ]
    
    def is_available(self):
        """Verificar si el proveedor está configurado"""
        return bool(self.api_key)
    
    def get_model_name(self):
        """Obtener nombre del modelo configurado"""
        return os.getenv('MIMO_MODEL', 'mimo-v2-flash')
    
    def generate(self, prompt, temperature=0.7, max_tokens=2048):
        """Generar respuesta usando MiMo API (formato OpenAI)"""
        if not self.is_available():
            raise Exception("MIMO_API_KEY no configurada")
        
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=60  # Aumentar timeout a 60 segundos
            )
            
            # Usar stream=True para respuestas más rápidas en tareas sencillas
            response = client.chat.completions.create(
                model=self.get_model_name(),
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True  # Habilitar streaming para mejor UX
            )
            
            # Procesar streaming
            content = ""
            total_tokens = 0
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content
                
                # Intentar obtener tokens del último chunk
                if hasattr(chunk, 'usage') and chunk.usage:
                    total_tokens = chunk.usage.total_tokens
            
            self.tokens_used = total_tokens
            self.cost = 0.0
            
            return {
                'text': content,
                'tokens_used': self.tokens_used,
                'cost': self.cost,
                'model': self.get_model_name()
            }
            
        except ImportError:
            raise Exception("openai package no instalado. Ejecuta: pip install openai")
        except Exception as e:
            raise Exception(f"Error al generar con MiMo: {str(e)}")
    
    def get_available_models(self):
        """Obtener lista de modelos disponibles"""
        return self.available_models
    
    def get_provider_info(self):
        """Información del proveedor"""
        return {
            'name': 'Xiaomi MiMo',
            'type': 'cloud',
            'models': self.available_models,
            'configured': self.is_available(),
            'base_url': self.base_url
        }
