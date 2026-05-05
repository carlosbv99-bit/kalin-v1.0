"""
Test funcional mínimo - Verifica que el sistema funciona
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_brain_basico():
    """Test básico del brain"""
    print("\n🧪 Test 1: Brain - Detección de intenciones")
    
    from agent.core.brain import detectar_intencion
    
    tests = [
        ("/fix main.py", "fix"),
        ("/scan", "scan"),
        ("/help", "help"),
        ("hola", "chat"),
        ("/setpath E:\\test", "setpath"),
    ]
    
    passed = 0
    for mensaje, esperado in tests:
        resultado = detectar_intencion(mensaje)
        if resultado == esperado:
            print(f"  ✅ '{mensaje}' -> '{resultado}'")
            passed += 1
        else:
            print(f"  ❌ '{mensaje}' -> '{resultado}' (esperado: '{esperado}')")
    
    return passed == len(tests)


def test_state_manager_basico():
    """Test básico del state manager"""
    print("\n🧪 Test 2: State Manager")
    
    from agent.core.state_manager import StateManager
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = StateManager(base_path=tmpdir)
        
        # Test estado inicial
        assert sm.get_ruta() is None
        print("  ✅ Estado inicial correcto")
        
        # Test set_ruta
        result = sm.set_ruta(tmpdir)
        assert result == True
        print("  ✅ Set ruta válido")
        
        # Test ruta inválida
        result = sm.set_ruta("Z:\\no_existe_99999")
        assert result == False
        print("  ✅ Validación ruta inválida")
        
        # Test stats
        stats = sm.get_stats()
        assert "exitos" in stats
        assert "fallos" in stats
        print("  ✅ Stats disponibles")
        
        # Test get_ultimo_archivo (método nuevo)
        archivo = sm.get_ultimo_archivo()
        assert archivo is None
        print("  ✅ get_ultimo_archivo disponible")
    
    return True


def test_web_app_basico():
    """Test básico de la app web"""
    print("\n🧪 Test 3: Web App Flask")
    
    from web import app
    
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        # Test home
        response = client.get('/')
        assert response.status_code == 200
        print("  ✅ GET / funciona")
        
        # Test help
        response = client.get('/help')
        assert response.status_code == 200
        data = response.get_json()
        assert "respuesta" in data
        print("  ✅ GET /help funciona")
        
        # Test health
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert "status" in data
        print("  ✅ GET /health funciona")
        
        # Test chat
        response = client.post('/chat', json={"mensaje": "/help"})
        assert response.status_code == 200
        data = response.get_json()
        assert "respuesta" in data
        print("  ✅ POST /chat funciona")
    
    return True


def test_orchestrator():
    """Test del orchestrator"""
    print("\n🧪 Test 4: Orchestrator")
    
    from agent.core.orchestrator import Orchestrator
    from web import app
    
    orch = Orchestrator()
    
    # Necesitamos contexto de Flask para jsonify
    with app.app_context():
        utils = {
            "leer_archivo": lambda x: None,
            "buscar_archivo_inteligente": lambda x, y: None,
            "limpiar_codigo": lambda x: x,
            "generar_diff": lambda x, y: "",
            "es_codigo_valido": lambda x: True,
            "guardar_backup": lambda x, y: None,
            "escribir_archivo": lambda x, y: None,
            "analizar_codigo": lambda x: {}
        }
        
        estado = {"ruta_proyecto": None, "ultimo_fix": None}
        
        response = orch.handle("/help", estado, utils)
        assert response.status_code == 200
        print("  ✅ Orchestrator procesa comandos")
    
    return True


def main():
    """Ejecutar todos los tests"""
    print("="*70)
    print("  TESTS FUNCIONALES BÁSICOS")
    print("="*70)
    
    results = []
    
    try:
        results.append(("Brain", test_brain_basico()))
    except Exception as e:
        print(f"\n❌ Brain falló: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Brain", False))
    
    try:
        results.append(("State Manager", test_state_manager_basico()))
    except Exception as e:
        print(f"\n❌ State Manager falló: {e}")
        import traceback
        traceback.print_exc()
        results.append(("State Manager", False))
    
    try:
        results.append(("Web App", test_web_app_basico()))
    except Exception as e:
        print(f"\n❌ Web App falló: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Web App", False))
    
    try:
        results.append(("Orchestrator", test_orchestrator()))
    except Exception as e:
        print(f"\n❌ Orchestrator falló: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Orchestrator", False))
    
    # Resumen
    print("\n" + "="*70)
    print("  RESUMEN")
    print("="*70)
    
    for name, passed in results:
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"  {name:20} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n  Total: {passed}/{total} tests pasaron")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("\n✅ El proyecto está funcionando correctamente")
        print("🚀 Puedes iniciar el servidor con: python run.py")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
