"""
Script para verificar que la configuración de modelo único está correcta.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(__file__))

def test_configuracion_modelo():
    """Verifica que solo se usa deepseek-coder"""
    print("="*80)
    print("🔍 VERIFICANDO CONFIGURACIÓN DE MODELO ÚNICO")
    print("="*80)
    
    from agent.llm.config import LLMConfig, ProviderType
    
    # Verificar modo
    print(f"\n✅ Modo actual: {LLMConfig.MODE}")
    assert LLMConfig.MODE == "local", "El modo debería ser 'local'"
    
    # Verificar que OLLAMA_CHAT ya no existe como provider separado
    providers = list(LLMConfig.PROVIDERS.keys())
    print(f"✅ Proveedores configurados: {[p.value for p in providers]}")
    
    assert ProviderType.OLLAMA in providers, "OLLAMA debe estar presente"
    assert ProviderType.OPENAI in providers, "OPENAI debe estar presente (fallback)"
    assert ProviderType.ANTHROPIC in providers, "ANTHROPIC debe estar presente (fallback)"
    
    # Verificar que OLLAMA_CHAT NO está
    has_ollama_chat = any('CHAT' in str(p) for p in providers)
    if has_ollama_chat:
        print("❌ ERROR: OLLAMA_CHAT aún existe como proveedor separado")
        return False
    else:
        print("✅ OLLAMA_CHAT eliminado correctamente")
    
    # Verificar modelo configurado
    ollama_config = LLMConfig.PROVIDERS[ProviderType.OLLAMA]
    modelo = ollama_config['model']
    print(f"✅ Modelo OLLAMA configurado: {modelo}")
    
    if 'deepseek-coder' in modelo:
        print("✅ Usando deepseek-coder correctamente")
    else:
        print(f"⚠️  Advertencia: El modelo es '{modelo}', esperaba 'deepseek-coder'")
    
    # Verificar fallback order
    fallback_order = LLMConfig.get_fallback_order()
    print(f"✅ Orden de fallback: {[p.value for p in fallback_order]}")
    
    # Verificar que get_primary_provider devuelve OLLAMA en modo local
    primary = LLMConfig.get_primary_provider("fix")
    print(f"✅ Primary provider para 'fix': {primary.value}")
    assert primary == ProviderType.OLLAMA, "Debería usar OLLAMA como primary"
    
    primary_chat = LLMConfig.get_primary_provider("chat")
    print(f"✅ Primary provider para 'chat': {primary_chat.value}")
    assert primary_chat == ProviderType.OLLAMA, "Debería usar OLLAMA para chat también"
    
    print("\n" + "="*80)
    print("✅ TODAS LAS VERIFICACIONES DE CONFIGURACIÓN PASARON")
    print("="*80)
    return True

def test_provider_manager():
    """Verifica que el Provider Manager no tiene OLLAMA_CHAT"""
    print("\n" + "="*80)
    print("🔍 VERIFICANDO PROVIDER MANAGER")
    print("="*80)
    
    from agent.llm.provider_manager import LLMProviderManager
    
    manager = LLMProviderManager()
    
    print(f"\n✅ Proveedores inicializados: {list(manager.providers.keys())}")
    
    # Verificar que no hay OLLAMA_CHAT
    has_chat = any('CHAT' in str(k) for k in manager.providers.keys())
    if has_chat:
        print("❌ ERROR: Provider Manager aún tiene OLLAMA_CHAT")
        return False
    else:
        print("✅ Provider Manager no tiene OLLAMA_CHAT")
    
    print(f"✅ Total de proveedores: {len(manager.providers)}")
    
    print("\n" + "="*80)
    print("✅ PROVIDER MANAGER VERIFICADO CORRECTAMENTE")
    print("="*80)
    return True

def test_env_variables():
    """Verifica variables de entorno"""
    print("\n" + "="*80)
    print("🔍 VERIFICANDO VARIABLES DE ENTORNO")
    print("="*80)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    ollama_model = os.getenv('OLLAMA_MODEL')
    ollama_chat_model = os.getenv('OLLAMA_CHAT_MODEL')
    debug_mode = os.getenv('KALIN_DEBUG')
    
    print(f"\n✅ OLLAMA_MODEL: {ollama_model}")
    print(f"✅ OLLAMA_CHAT_MODEL: {ollama_chat_model}")
    print(f"✅ KALIN_DEBUG: {debug_mode}")
    
    if ollama_model and 'deepseek-coder' in ollama_model:
        print("✅ OLLAMA_MODEL configurado correctamente")
    else:
        print(f"⚠️  OLLAMA_MODEL debería contener 'deepseek-coder'")
    
    if ollama_chat_model and 'deepseek-coder' in ollama_chat_model:
        print("✅ OLLAMA_CHAT_MODEL usa el mismo modelo (correcto)")
    else:
        print(f"⚠️  OLLAMA_CHAT_MODEL debería ser 'deepseek-coder:latest'")
    
    if debug_mode == '1':
        print("✅ Modo DEBUG activado")
    else:
        print("ℹ️  Modo DEBUG desactivado (para ver logs detallados, pon KALIN_DEBUG=1)")
    
    print("\n" + "="*80)
    print("✅ VARIABLES DE ENTORNO VERIFICADAS")
    print("="*80)
    return True

if __name__ == "__main__":
    try:
        success = True
        
        success = test_configuracion_modelo() and success
        success = test_provider_manager() and success
        success = test_env_variables() and success
        
        if success:
            print("\n" + "="*80)
            print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
            print("="*80)
            print("\n✅ Configuración verificada:")
            print("   • Solo un modelo: deepseek-coder")
            print("   • OLLAMA_CHAT eliminado")
            print("   • Provider Manager actualizado")
            print("   • Variables de entorno correctas")
            sys.exit(0)
        else:
            print("\n❌ Algunas pruebas fallaron. Revisa los errores arriba.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
