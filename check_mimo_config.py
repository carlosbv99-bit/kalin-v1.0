"""
Script de diagnóstico para verificar configuración de proveedores cloud
"""
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

print("=" * 70)
print("DIAGNÓSTICO DE PROVEEDORES CONFIGURADOS")
print("=" * 70)
print()

# Verificar MiMo
print("📱 XIAOMI MiMo:")
mimo_key = os.getenv('MIMO_API_KEY')
mimo_model = os.getenv('MIMO_MODEL', 'mimo-v2-flash')
mimo_url = os.getenv('MIMO_BASE_URL', 'https://api.xiaomimimo.com/v1')
print(f"   API Key: {'✅ CONFIGURADA' if mimo_key else '❌ NO CONFIGURADA'}")
if mimo_key:
    print(f"   Modelo: {mimo_model}")
    print(f"   Base URL: {mimo_url}")
    print(f"   Longitud API Key: {len(mimo_key)} caracteres")
print()

# Verificar otros proveedores
providers = {
    'OpenAI': ('OPENAI_API_KEY', 'OPENAI_MODEL', 'gpt-4-turbo'),
    'Anthropic': ('ANTHROPIC_API_KEY', 'ANTHROPIC_MODEL', 'claude-3-5-sonnet'),
    'Groq/Grok': ('GROQ_API_KEY', 'GROK_MODEL', 'llama-3.1-8b-instant'),
    'Gemini': ('GEMINI_API_KEY', 'GEMINI_MODEL', 'gemini-1.5-flash'),
    'Mistral': ('MISTRAL_API_KEY', 'MISTRAL_MODEL', 'mistral-small-latest'),
}

for name, (key_var, model_var, default_model) in providers.items():
    key = os.getenv(key_var) or os.getenv(key_var.replace('GROQ', 'GROK'))
    model = os.getenv(model_var, default_model)
    status = '✅ CONFIGURADA' if key else '❌ NO CONFIGURADA'
    print(f"🔹 {name}:")
    print(f"   API Key: {status}")
    if key:
        print(f"   Modelo: {model}")
        print(f"   Longitud: {len(key)} caracteres")
    print()

print("=" * 70)
print("PROVEEDORES ACTIVOS:")
print("=" * 70)

# Usar el método dinámico de LLMConfig
try:
    from agent.llm.config import LLMConfig
    
    cloud_providers = LLMConfig.get_configured_cloud_providers()
    
    if cloud_providers:
        for provider in cloud_providers:
            print(f"✅ {provider['display_name']}")
            print(f"   Provider Type: {provider['provider_type']}")
            print(f"   Model: {provider['model_name']}")
            print()
    else:
        print("❌ No hay proveedores de nube configurados")
        print()
        print("💡 Para agregar MiMo, añade estas líneas a tu .env:")
        print("   MIMO_API_KEY=tu_api_key_aqui")
        print("   MIMO_MODEL=mimo-v2-flash  # o mimo-v2-pro")
        
except Exception as e:
    print(f"❌ Error al cargar LLMConfig: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
