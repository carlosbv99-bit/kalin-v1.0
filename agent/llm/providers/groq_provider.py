"""
Groq Provider - Modelos ultra-rápidos en la nube
Soporta: Llama 3, Mixtral, Gemma
API gratuita disponible en: https://console.groq.com/keys
"""

from .base_provider import BaseLLMProvider
import os


class GroqProvider(BaseLLMProvider):
    """Proveedor para Groq API"""
    
    def __init__(self, config=None):
        super().__init__(config or {})
        self.api_key = os.getenv('GROQ_API_KEY', '')
        self.base_url = 'https://api.groq.com/openai/v1'
        
        # Modelos disponibles en Groq
        self.available_models = [
            'llama-3.3-70b-versatile',
            'llama-3.1-8b-instant',
            'llama3-70b-8192',
            'llama3-8b-8192',
            'mixtral-8x7b-32768',
            'gemma2-9b-it',
            'gemma-7b-it',
        ]
    
    def is_available(self):
        """Verificar si el proveedor está configurado"""
        return bool(self.api_key)
    
    def get_model_name(self):
        """Obtener nombre del modelo configurado"""
        return os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
    
    def generate(self, prompt, temperature=0.7, max_tokens=2048):
        """Generar respuesta usando Groq API"""
        if not self.is_available():
            raise Exception("GROQ_API_KEY no configurada")
        
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            response = client.chat.completions.create(
                model=self.get_model_name(),
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except ImportError:
            raise Exception("Instala openai: pip install openai")
        except Exception as e:
            raise Exception(f"Error en Groq: {str(e)}")
    
    def get_available_models(self):
        """Lista de modelos disponibles"""
        return self.available_models
    
    def refresh_models(self):
        """Refrescar lista de modelos"""
        return self.available_models
