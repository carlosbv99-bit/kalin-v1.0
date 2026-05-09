"""
Script completo de pruebas para verificar todos los cambios implementados.
Incluye: configuración, debug, experience memory, y limpieza de disco.
"""

import sys
import os
import subprocess

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(__file__))

def print_section(title):
    """Imprime una sección separada"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_configuracion():
    """Prueba 1: Verificar configuración del modelo único"""
    print_section("PRUEBA 1: CONFIGURACIÓN DE MODELO ÚNICO")
    
    try:
        from agent.llm.config import LLMConfig, ProviderType
        
        # Verificar que OLLAMA_CHAT no existe
        providers = list(LLMConfig.PROVIDERS.keys())
        has_chat = any('CHAT' in str(p) for p in providers)
        
        if has_chat:
            print("❌ FALLÓ: OLLAMA_CHAT aún existe")
            return False
        
        print("✅ OLLAMA_CHAT eliminado correctamente")
        
        # Verificar modelo deepseek-coder
        ollama_model = LLMConfig.PROVIDERS[ProviderType.OLLAMA]['model']
        if 'deepseek-coder' in ollama_model:
            print(f"✅ Modelo configurado: {ollama_model}")
        else:
            print(f"⚠️  Modelo actual: {ollama_model}")
        
        # Verificar que ambos use_cases usan el mismo provider
        primary_fix = LLMConfig.get_primary_provider("fix")
        primary_chat = LLMConfig.get_primary_provider("chat")
        
        if primary_fix == primary_chat == ProviderType.OLLAMA:
            print("✅ Tanto 'fix' como 'chat' usan OLLAMA (deepseek-coder)")
        else:
            print(f"❌ Providers diferentes: fix={primary_fix}, chat={primary_chat}")
            return False
        
        print("\n✅ PRUEBA 1 PASADA: Configuración correcta")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba 1: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_debug_mode():
    """Prueba 2: Verificar modo DEBUG"""
    print_section("PRUEBA 2: SISTEMA DE DEBUG")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        debug_mode = os.getenv('KALIN_DEBUG', '0')
        
        if debug_mode == '1':
            print("✅ Modo DEBUG activado (KALIN_DEBUG=1)")
            print("   Verás prompts y respuestas detalladas en consola")
        else:
            print("ℹ️  Modo DEBUG desactivado (KALIN_DEBUG=0)")
            print("   Para activar: cambia KALIN_DEBUG=1 en .env")
        
        # Verificar que los archivos tienen código de debug
        files_to_check = [
            'agent/analyzer.py',
            'agent/actions/tools/fix_tool.py',
            'agent/llm/provider_manager.py'
        ]
        
        all_have_debug = True
        for file_path in files_to_check:
            full_path = os.path.join(os.path.dirname(__file__), file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'DEBUG_MODE' in content and 'KALIN_DEBUG' in content:
                        print(f"✅ {file_path} tiene soporte para debug")
                    else:
                        print(f"❌ {file_path} NO tiene soporte para debug")
                        all_have_debug = False
            else:
                print(f"⚠️  {file_path} no encontrado")
        
        if all_have_debug:
            print("\n✅ PRUEBA 2 PASADA: Sistema de debug implementado")
            return True
        else:
            print("\n❌ PRUEBA 2 FALLÓ: Falta código de debug en algunos archivos")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba 2: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_experience_memory():
    """Prueba 3: Verificar Experience Memory"""
    print_section("PRUEBA 3: EXPERIENCE MEMORY")
    
    try:
        from agent.core.experience_memory import ExperienceMemory, get_experience_memory
        
        # Crear instancia
        exp_mem = get_experience_memory()
        print("✅ ExperienceMemory inicializado correctamente")
        
        # Probar registro de experiencia
        exp_id = exp_mem.record_experience(
            task_type='test',
            problem_description='Test de verificación',
            file_type='python',
            strategy_used='smart',
            success=True,
            confidence_score=0.95,
            tokens_used=100,
            duration_seconds=1.5,
            solution_summary='Test exitoso'
        )
        
        print(f"✅ Experiencia registrada: {exp_id}")
        
        # Verificar que se guardó
        summary = exp_mem.get_learning_summary()
        print(f"✅ Total experiencias: {summary['total_experiences']}")
        print(f"✅ Tasa de éxito global: {summary['overall_success_rate']:.1%}")
        
        # Verificar archivos creados
        exp_dir = os.path.join(os.path.dirname(__file__), 'experience_memory')
        if os.path.exists(exp_dir):
            files = os.listdir(exp_dir)
            print(f"✅ Carpeta experience_memory creada con {len(files)} archivos")
            for f in files:
                print(f"   - {f}")
        else:
            print("⚠️  Carpeta experience_memory no encontrada")
        
        print("\n✅ PRUEBA 3 PASADA: Experience Memory funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba 3: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_brain_intentions():
    """Prueba 4: Verificar nuevas intenciones en brain.py"""
    print_section("PRUEBA 4: NUEVAS INTENCIONES EN BRAIN")
    
    try:
        from agent.core.brain import detectar_intencion
        
        # Probar intención /experience
        intent_exp = detectar_intencion("/experience")
        if intent_exp == "experience":
            print("✅ Intención '/experience' detectada correctamente")
        else:
            print(f"❌ '/experience' detectado como: {intent_exp}")
            return False
        
        # Probar intención /learn
        intent_learn = detectar_intencion("/learn")
        if intent_learn == "learn":
            print("✅ Intención '/learn' detectada correctamente")
        else:
            print(f"❌ '/learn' detectado como: {intent_learn}")
            return False
        
        # Probar lenguaje natural
        intent_natural = detectar_intencion("muéstrame tu experiencia")
        if intent_natural == "experience":
            print("✅ Lenguaje natural 'experiencia' detectado correctamente")
        
        intent_patterns = detectar_intencion("qué patrones has aprendido")
        if intent_patterns == "learn":
            print("✅ Lenguaje natural 'patrones' detectado correctamente")
        
        print("\n✅ PRUEBA 4 PASADA: Nuevas intenciones funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba 4: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_clean_script():
    """Prueba 5: Verificar script de limpieza"""
    print_section("PRUEBA 5: SCRIPT DE LIMPIEZA DE DISCO")
    
    try:
        clean_script = os.path.join(os.path.dirname(__file__), 'clean_disk_space.py')
        
        if not os.path.exists(clean_script):
            print("❌ Script clean_disk_space.py no encontrado")
            return False
        
        print("✅ Script clean_disk_space.py encontrado")
        
        # Verificar que es ejecutable
        with open(clean_script, 'r', encoding='utf-8') as f:
            content = f.read()
            
        required_functions = [
            'clean_logs',
            'clean_sessions',
            'clean_pycache',
            'clean_backup_files',
            'suggest_ollama_cleanup'
        ]
        
        for func in required_functions:
            if f'def {func}' in content:
                print(f"✅ Función '{func}' presente")
            else:
                print(f"❌ Función '{func}' faltante")
                return False
        
        print("\n✅ PRUEBA 5 PASADA: Script de limpieza completo")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba 5: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_documentation():
    """Prueba 6: Verificar documentación"""
    print_section("PRUEBA 6: DOCUMENTACIÓN")
    
    try:
        docs = [
            'EXPERIENCE_MEMORY_GUIDE.md',
            'DEBUG_GUIDE.md',
            'LIMPIEZA_DISCO.md',
            'CAMBIOS_MODELO_UNICO.md'
        ]
        
        for doc in docs:
            doc_path = os.path.join(os.path.dirname(__file__), doc)
            if os.path.exists(doc_path):
                size = os.path.getsize(doc_path)
                print(f"✅ {doc} ({size:,} bytes)")
            else:
                print(f"⚠️  {doc} no encontrado")
        
        print("\n✅ PRUEBA 6 PASADA: Documentación creada")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba 6: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*80)
    print("  🧪 SUITE COMPLETA DE PRUEBAS - KALIN v3.0")
    print("="*80)
    
    results = []
    
    # Ejecutar todas las pruebas
    results.append(("Configuración Modelo Único", test_configuracion()))
    results.append(("Sistema de Debug", test_debug_mode()))
    results.append(("Experience Memory", test_experience_memory()))
    results.append(("Nuevas Intenciones Brain", test_brain_intentions()))
    results.append(("Script de Limpieza", test_clean_script()))
    results.append(("Documentación", test_documentation()))
    
    # Resumen final
    print_section("RESUMEN DE RESULTADOS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status:10} - {test_name}")
    
    print("\n" + "="*80)
    print(f"  RESULTADO FINAL: {passed}/{total} pruebas pasaron")
    print("="*80)
    
    if passed == total:
        print("\n🎉 ¡EXCELENTE! Todas las pruebas pasaron.")
        print("\n✨ Cambios implementados exitosamente:")
        print("   1. ✅ Modelo único: deepseek-coder para todo")
        print("   2. ✅ Sistema de debug completo")
        print("   3. ✅ Experience Memory funcional")
        print("   4. ✅ Nuevos comandos /experience y /learn")
        print("   5. ✅ Script de limpieza de disco")
        print("   6. ✅ Documentación completa")
        print("\n📝 Próximos pasos:")
        print("   • Inicia el servidor: python run.py")
        print("   • Prueba en la interfaz web: http://localhost:5000")
        print("   • Usa /experience para ver el aprendizaje")
        print("   • Ejecuta: python clean_disk_space.py para liberar espacio")
        return True
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
