"""
Mistral AI Provider - Modelos de Mistral
Soporta: Mistral Large, Mixtral, Mistral Medium
API disponible en: https://console.mistral.ai/
"""

from .base_provider import BaseLLMProvider
import os


class MistralProvider(BaseLLMProvider):
    """Proveedor para Mistral AI API"""
    
    def __init__(self, config=None):
        super().__init__(config or {})
        self.api_key = os.getenv('MISTRAL_API_KEY', '')
        
        # Modelos disponibles
        self.available_models = [
            'mistral-large-latest',
            'mistral-medium-latest',
            'mistral-small-latest',
            'codestral-latest',
            'open-mixtral-8x7b',
            'open-mixtral-8x22b',
        ]
    
    def is_available(self):
        """Verificar si el proveedor está configurado"""
        return bool(self.api_key)
    
    def get_model_name(self):
        """Obtener nombre del modelo configurado"""
        return os.getenv('MISTRAL_MODEL', 'mistral-small-latest')
    
    def generate(self, prompt, temperature=0.7, max_tokens=2048):
        """Generar respuesta usando Mistral API"""
        if not self.is_available():
            raise Exception("MISTRAL_API_KEY no configurada")
        
        try:
            from mistralai import Mistral
            
            client = Mistral(api_key=self.api_key)
            
            response = client.chat.complete(
                model=self.get_model_name(),
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except ImportError:
            raise Exception("Instala mistralai: pip install mistralai")
        except Exception as e:
            raise Exception(f"Error en Mistral: {str(e)}")
    
    def get_available_models(self):
        """Lista de modelos disponibles"""
        return self.available_models
    
    def refresh_models(self):
        """Refrescar lista de modelos"""
        return self.available_models
