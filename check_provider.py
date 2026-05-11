#!/usr/bin/env python3
"""
Verifica y corrige la configuración del proveedor LLM
"""
import os
from dotenv import load_dotenv

load_dotenv()

active_provider = os.getenv('ACTIVE_PROVIDER', 'ollama')
print(f"Proveedor activo actual: {active_provider}")

# Verificar si Ollama está disponible
if active_provider.lower() == 'ollama':
    import subprocess
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama está ejecutándose")
            print("Modelos disponibles:")
            print(result.stdout)
        else:
            print("❌ Ollama no está ejecutándose")
            print("Opciones:")
            print("1. Ejecuta: ollama serve")
            print("2. Cambia a Groq: ACTIVE_PROVIDER=groq en .env")
    except FileNotFoundError:
        print("❌ Ollama no está instalado")
        print("Cambia a Groq: ACTIVE_PROVIDER=groq en .env")
    except subprocess.TimeoutExpired:
        print("❌ Timeout conectando a Ollama")
elif active_provider.lower() == 'groq':
    grok_api_key = os.getenv('GROK_API_KEY', '')
    if grok_api_key and grok_api_key.startswith('gsk_'):
        print("✅ Groq configurado correctamente")
        print(f"Modelo: {os.getenv('GROK_MODEL', 'no configurado')}")
    else:
        print("❌ API Key de Groq no válida o faltante")
else:
    print(f"⚠️ Proveedor desconocido: {active_provider}")
