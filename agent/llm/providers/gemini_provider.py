"""
Google Gemini Provider - Modelos de Google AI
Soporta: Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini Pro
API gratuita disponible en: https://makersuite.google.com/app/apikey
"""

from .base_provider import BaseLLMProvider
import os


class GeminiProvider(BaseLLMProvider):
    """Proveedor para Google Gemini API"""
    
    def __init__(self, config=None):
        super().__init__(config or {})
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        
        # Modelos disponibles
        self.available_models = [
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-1.0-pro',
            'gemini-pro',
        ]
    
    def is_available(self):
        """Verificar si el proveedor está configurado"""
        return bool(self.api_key)
    
    def get_model_name(self):
        """Obtener nombre del modelo configurado"""
        return os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    def generate(self, prompt, temperature=0.7, max_tokens=2048):
        """Generar respuesta usando Gemini API"""
        if not self.is_available():
            raise Exception("GEMINI_API_KEY no configurada")
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel(self.get_model_name())
            
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        
        except ImportError:
            raise Exception("Instala google-generativeai: pip install google-generativeai")
        except Exception as e:
            raise Exception(f"Error en Gemini: {str(e)}")
    
    def get_available_models(self):
        """Lista de modelos disponibles"""
        return self.available_models
    
    def refresh_models(self):
        """Refrescar lista de modelos"""
        return self.available_models
