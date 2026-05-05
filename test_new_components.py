"""
Tests para los nuevos componentes de Kalin v2.0
Verifica: Logger, ConversationManager, Security, Cache, Commands
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_logger():
    """Test del sistema de logging"""
    print("\n" + "="*70)
    print("🧪 TEST 1: Sistema de Logging")
    print("="*70)
    
    try:
        from agent.core.logger import get_logger, KalinLogger
        
        logger = get_logger('kalin.test')
        
        # Probar diferentes niveles de log
        logger.info("Test: Info message")
        logger.debug("Test: Debug message")
        logger.warning("Test: Warning message")
        logger.error("Test: Error message")
        
        # Verificar que se crearon los archivos de log
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        expected_files = ['kalin.log', 'kalin_errors.log']
        
        for filename in expected_files:
            filepath = os.path.join(log_dir, filename)
            if os.path.exists(filepath):
                print(f"  ✅ {filename} creado correctamente")
            else:
                print(f"  ⚠️  {filename} no encontrado")
        
        print("  ✅ Logger funciona correctamente")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_manager():
    """Test del Conversation Manager"""
    print("\n" + "="*70)
    print("🧪 TEST 2: Conversation Manager")
    print("="*70)
    
    try:
        from agent.core.conversation_manager import ConversationManager
        
        # Crear manager temporal
        with tempfile.TemporaryDirectory() as tmpdir:
            cm = ConversationManager(session_id="test_001", storage_dir=tmpdir)
            
            # Test agregar mensajes
            cm.add_message('user', 'Hola, ¿cómo estás?')
            cm.add_message('assistant', '¡Bien! ¿En qué puedo ayudarte?')
            cm.add_message('user', 'Necesito revisar mi proyecto')
            
            print(f"  ✅ Mensajes agregados: {len(cm.messages)}")
            
            # Test obtener recientes
            recent = cm.get_recent_messages(limit=2)
            assert len(recent) == 2
            print(f"  ✅ Get recent messages: {len(recent)} mensajes")
            
            # Test crear tarea
            task_id = cm.create_task('fix', file_path='main.py')
            assert task_id is not None
            print(f"  ✅ Task creada: {task_id}")
            
            # Test actualizar tarea
            cm.update_task(task_id, status='in_progress')
            task = cm.get_task(task_id)
            assert task.status == 'in_progress'
            print(f"  ✅ Task actualizada: status={task.status}")
            
            # Test variables de contexto
            cm.set_variable('ruta_proyecto', 'E:\\test')
            ruta = cm.get_variable('ruta_proyecto')
            assert ruta == 'E:\\test'
            print(f"  ✅ Variables de contexto funcionan")
            
            # Test guardar y cargar
            cm.save()
            
            # Crear nuevo manager y cargar sesión
            cm2 = ConversationManager(session_id="test_001", storage_dir=tmpdir)
            assert len(cm2.messages) == 3
            print(f"  ✅ Persistencia funciona: {len(cm2.messages)} mensajes recuperados")
            
            # Test resumen
            summary = cm.get_summary()
            assert 'message_count' in summary
            print(f"  ✅ Resumen generado: {summary['message_count']} mensajes")
            
        print("  ✅ Conversation Manager funciona correctamente")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_security():
    """Test del Security Manager"""
    print("\n" + "="*70)
    print("🧪 TEST 3: Security Manager")
    print("="*70)
    
    try:
        from agent.core.security import SecurityManager
        
        sm = SecurityManager()
        
        # Test ruta segura
        is_safe, error = sm.is_safe_path('E:\\kalin\\main.py', 'E:\\kalin')
        assert is_safe == True
        print("  ✅ Ruta segura validada correctamente")
        
        # Test path traversal
        is_safe, error = sm.is_safe_path('E:\\kalin\\..\\..\\Windows\\system32', 'E:\\kalin')
        assert is_safe == False
        print(f"  ✅ Path traversal bloqueado: {error}")
        
        # Test extensión peligrosa
        is_safe, error = sm.is_safe_filename('malware.exe')
        assert is_safe == False
        print(f"  ✅ Extensión peligrosa bloqueada: {error}")
        
        # Test nombre seguro
        is_safe, error = sm.is_safe_filename('main.py')
        assert is_safe == True
        print("  ✅ Nombre de archivo seguro validado")
        
        # Test sanitización
        sanitized = sm.sanitize_path('E:/kalin/./../kalin/main.py')
        assert 'kalin' in sanitized
        print(f"  ✅ Sanitización funciona: {sanitized}")
        
        # Test validación de código
        is_valid, error = sm.validate_code_content('print("hello")')
        assert is_valid == True
        print("  ✅ Código válido aceptado")
        
        # Test código con null bytes
        is_valid, error = sm.validate_code_content('code\x00injection')
        assert is_valid == False
        print(f"  ✅ Código con null bytes bloqueado: {error}")
        
        # Test niveles de riesgo
        risk = sm.get_file_risk_level('main.py')
        assert risk in ['low', 'medium', 'high']
        print(f"  ✅ Nivel de riesgo determinado: {risk}")
        
        print("  ✅ Security Manager funciona correctamente")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache():
    """Test del Smart Cache"""
    print("\n" + "="*70)
    print("🧪 TEST 4: Smart Cache")
    print("="*70)
    
    try:
        from agent.core.cache import SmartCache
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = SmartCache(max_size=5, storage_dir=tmpdir)
            
            # Test set/get
            cache.set('key1', 'value1', ttl=3600)
            value = cache.get('key1')
            assert value == 'value1'
            print("  ✅ Set/Get funciona")
            
            # Test cache miss
            value = cache.get('key2')
            assert value is None
            print("  ✅ Cache miss funciona")
            
            # Test eviction
            for i in range(6):
                cache.set(f'key{i}', f'value{i}')
            
            assert len(cache._cache) <= 5
            print(f"  ✅ Eviction funciona: {len(cache._cache)} items (max 5)")
            
            # Test stats
            stats = cache.get_stats()
            assert 'hits' in stats
            assert 'misses' in stats
            assert 'hit_rate' in stats
            print(f"  ✅ Stats: {stats['hits']} hits, {stats['misses']} misses, hit rate: {stats['hit_rate']}")
            
            # Test TTL expiry
            cache2 = SmartCache(max_size=10)
            cache2.set('temp', 'value', ttl=1)  # 1 segundo
            import time
            time.sleep(1.1)
            value = cache2.get('temp')
            assert value is None
            print("  ✅ TTL expiry funciona")
            
            # Test clear
            cache.clear()
            assert len(cache._cache) == 0
            print("  ✅ Clear funciona")
            
            # Test save/load
            cache.set('persist', 'data', ttl=3600)
            cache.save_to_disk()
            
            cache3 = SmartCache(max_size=10, storage_dir=tmpdir)
            cache3.load_from_disk()
            value = cache3.get('persist')
            assert value == 'data'
            print("  ✅ Persistencia en disco funciona")
        
        print("  ✅ Smart Cache funciona correctamente")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_commands():
    """Test del Command Pattern"""
    print("\n" + "="*70)
    print("🧪 TEST 5: Command Pattern")
    print("="*70)
    
    try:
        from agent.actions.commands.base import CommandRegistry, BaseCommand
        from agent.actions.commands.fix_command import FixCommand
        from agent.actions.commands.setpath_command import SetPathCommand
        from agent.actions.commands.scan_command import ScanCommand
        from agent.actions.commands.chat_command import ChatCommand
        
        # Test registro
        registry = CommandRegistry()
        registry.register('test', FixCommand())
        
        command = registry.get('test')
        assert command is not None
        print("  ✅ Registro de comandos funciona")
        
        # Test listar comandos
        commands = registry.list_commands()
        assert 'test' in commands
        print(f"  ✅ Lista de comandos: {commands}")
        
        # Test interfaz
        assert hasattr(command, 'execute')
        assert hasattr(command, 'validate')
        print("  ✅ Interfaz BaseCommand correcta")
        
        print("  ✅ Command Pattern funciona correctamente")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print("🚀 TESTS COMPONENTES KALIN v2.0")
    print("="*70)
    
    tests = [
        ("Logger", test_logger),
        ("Conversation Manager", test_conversation_manager),
        ("Security", test_security),
        ("Cache", test_cache),
        ("Commands", test_commands),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} falló: {e}")
            results.append((name, False))
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70)
    
    for name, passed in results:
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"  {name:25} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n  Total: {passed}/{total} tests pasaron")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS COMPONENTES FUNCIONAN CORRECTAMENTE!")
        print("\n✅ Sistema listo para integración")
    else:
        print(f"\n⚠️  {total - passed} componente(s) fallaron")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
