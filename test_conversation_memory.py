"""
Test del Sistema de Memoria Conversacional Avanzado
"""

import sys
import os
import tempfile
import shutil

# Agregar ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agent.core.conversation_memory import ConversationMemory


def test_conversation_memory_basic():
    """Test básico de la memoria conversacional"""
    print("\n" + "="*70)
    print("🧪 TEST 1: Inicialización y Persistencia")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Crear instancia
        cm = ConversationMemory(
            session_id="test_session_001",
            max_history=20,
            storage_dir=tmpdir
        )
        
        print(f"✅ Session ID: {cm.session_id}")
        print(f"✅ Storage dir: {cm.storage_dir}")
        print(f"✅ Max history: {cm.max_history}")
        
        # Verificar que se creó el archivo de sesión
        session_file = os.path.join(tmpdir, "test_session_001.json")
        assert os.path.exists(session_file), "Session file should be created"
        print(f"✅ Session file created: {session_file}")


def test_update_context():
    """Test de actualización de contexto"""
    print("\n" + "="*70)
    print("🧪 TEST 2: Actualización de Contexto")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cm = ConversationMemory(
            session_id="test_session_002",
            storage_dir=tmpdir
        )
        
        # Simular análisis de archivo
        cm.update_context(
            intention="analyze",
            args={"arg": "main.py"},
            result="Análisis completado: 3 errores encontrados",
            metadata={"duration": 2.5, "file_type": "python"}
        )
        
        print(f"✅ Context updated: analyze main.py")
        print(f"   Last analyzed file: {cm.get_last_analyzed_file()}")
        print(f"   History length: {len(cm.conversation_history)}")
        
        # Simular corrección
        cm.update_context(
            intention="fix",
            args={"arg": "main.py"},
            result="Código corregido exitosamente",
            metadata={"duration": 3.2, "valid": True}
        )
        
        print(f"✅ Context updated: fix main.py")
        print(f"   Last fixed file: {cm.get_last_fixed_file()}")
        print(f"   History length: {len(cm.conversation_history)}")
        
        # Verificar métricas
        print(f"\n✅ Metrics:")
        print(f"   Total interactions: {cm.metrics['total_interactions']}")
        print(f"   Intention counts: {cm.metrics['intention_counts']}")


def test_infer_missing_context():
    """Test de inferencia de contexto"""
    print("\n" + "="*70)
    print("🧪 TEST 3: Inferencia de Contexto")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cm = ConversationMemory(
            session_id="test_session_003",
            storage_dir=tmpdir
        )
        
        # Primero establecer contexto
        cm.update_context(
            intention="analyze",
            args={"arg": "utils.py"},
            result="Análisis completado"
        )
        
        print(f"✅ Context established: utils.py analyzed")
        
        # Caso 1: Referencia implícita
        improved_args = cm.infer_missing_context(
            mensaje="ahora corrígelo",
            detected_intention="fix",
            args={}
        )
        
        print(f"\n✅ Test 1 - Implicit reference:")
        print(f"   Message: 'ahora corrígelo'")
        print(f"   Inferred args: {improved_args}")
        assert "arg" in improved_args, "Should infer file from context"
        assert improved_args["arg"] == "utils.py", "Should infer utils.py"
        print(f"   ✓ Correctly inferred: {improved_args['arg']}")
        
        # Caso 2: Archivo mencionado en mensaje
        improved_args = cm.infer_missing_context(
            mensaje="analiza main.py",
            detected_intention="analyze",
            args={}
        )
        
        print(f"\n✅ Test 2 - File in message:")
        print(f"   Message: 'analiza main.py'")
        print(f"   Inferred args: {improved_args}")
        assert improved_args.get("arg") == "main.py", "Should extract main.py from message"
        print(f"   ✓ Correctly extracted: {improved_args['arg']}")
        
        # Caso 3: Referencia a proyecto
        cm.update_context(
            intention="setpath",
            args={"arg": "/home/user/project"},
            result="Project set"
        )
        
        improved_args = cm.infer_missing_context(
            mensaje="escanea mi proyecto",
            detected_intention="scan",
            args={}
        )
        
        print(f"\n✅ Test 3 - Project reference:")
        print(f"   Message: 'escanea mi proyecto'")
        print(f"   Inferred args: {improved_args}")
        assert "project_path" in improved_args, "Should infer project path"
        print(f"   ✓ Correctly inferred project: {improved_args['project_path']}")


def test_file_tracking():
    """Test de rastreo de archivos"""
    print("\n" + "="*70)
    print("🧪 TEST 4: Rastreo de Archivos")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cm = ConversationMemory(
            session_id="test_session_004",
            storage_dir=tmpdir
        )
        
        # Simular múltiples acciones en diferentes archivos
        cm.update_context("analyze", {"arg": "main.py"}, "Analysis 1")
        cm.update_context("analyze", {"arg": "utils.py"}, "Analysis 2")
        cm.update_context("fix", {"arg": "main.py"}, "Fix 1")
        cm.update_context("create", {"arg": "test_main.py"}, "Created")
        cm.update_context("analyze", {"arg": "main.py"}, "Analysis 3")
        
        print(f"✅ Multiple actions recorded")
        print(f"   Total interactions: {cm.metrics['total_interactions']}")
        
        # Verificar archivos más usados
        most_used = cm.metrics['most_used_files']
        print(f"\n✅ Most used files ({len(most_used)}):")
        for entry in most_used[:5]:
            print(f"   - {entry['file']}: {entry['count']} times, last: {entry['last_action']}")
        
        # main.py debería ser el más usado
        if most_used:
            top_file = most_used[0]['file']
            print(f"\n✅ Top file: {top_file}")


def test_persistence():
    """Test de persistencia"""
    print("\n" + "="*70)
    print("🧪 TEST 5: Persistencia")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Crear primera instancia y agregar datos
        cm1 = ConversationMemory(
            session_id="test_session_005",
            storage_dir=tmpdir
        )
        
        cm1.update_context("analyze", {"arg": "test.py"}, "Analysis")
        cm1.update_context("fix", {"arg": "test.py"}, "Fix")
        
        session_file = os.path.join(tmpdir, "test_session_005.json")
        print(f"✅ Data saved to: {session_file}")
        print(f"   Interactions: {cm1.metrics['total_interactions']}")
        
        # Crear segunda instancia (debería cargar datos)
        cm2 = ConversationMemory(
            session_id="test_session_005",
            storage_dir=tmpdir
        )
        
        print(f"\n✅ New instance loaded:")
        print(f"   Interactions: {cm2.metrics['total_interactions']}")
        print(f"   History length: {len(cm2.conversation_history)}")
        print(f"   Last analyzed: {cm2.get_last_analyzed_file()}")
        print(f"   Last fixed: {cm2.get_last_fixed_file()}")
        
        # Verificar que los datos se cargaron correctamente
        assert cm2.metrics['total_interactions'] == 2, "Should load 2 interactions"
        assert len(cm2.conversation_history) == 2, "Should have 2 history entries"
        assert cm2.get_last_analyzed_file() == "test.py", "Should remember analyzed file"
        
        print(f"\n✅ Persistence verified successfully!")


def test_project_detection():
    """Test de detección de tipo de proyecto"""
    print("\n" + "="*70)
    print("🧪 TEST 6: Detección de Tipo de Proyecto")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cm = ConversationMemory(
            session_id="test_session_006",
            storage_dir=tmpdir
        )
        
        # Crear estructura de proyecto Python
        python_project = os.path.join(tmpdir, "python_app")
        os.makedirs(python_project)
        with open(os.path.join(python_project, "requirements.txt"), "w") as f:
            f.write("flask==2.0\n")
        
        project_type = cm._detect_project_type(python_project)
        print(f"✅ Python project detected: {project_type}")
        assert project_type == "python", "Should detect Python project"
        
        # Crear estructura de proyecto Node.js
        node_project = os.path.join(tmpdir, "node_app")
        os.makedirs(node_project)
        with open(os.path.join(node_project, "package.json"), "w") as f:
            f.write('{"name": "test"}')
        
        project_type = cm._detect_project_type(node_project)
        print(f"✅ Node.js project detected: {project_type}")
        assert project_type == "nodejs", "Should detect Node.js project"


def test_summary():
    """Test de resumen conversacional"""
    print("\n" + "="*70)
    print("🧪 TEST 7: Resumen Conversacional")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cm = ConversationMemory(
            session_id="test_session_007",
            storage_dir=tmpdir
        )
        
        # Agregar varias interacciones
        cm.update_context("setpath", {"arg": "/home/user/project"}, "Path set")
        cm.update_context("analyze", {"arg": "main.py"}, "Analysis")
        cm.update_context("fix", {"arg": "main.py"}, "Fix")
        cm.update_context("create", {"arg": "test.py"}, "Created")
        
        # Obtener resumen
        summary = cm.get_conversation_summary()
        
        print(f"✅ Conversation Summary:")
        print(f"   Session ID: {summary['session_id']}")
        print(f"   Total interactions: {summary['total_interactions']}")
        print(f"   History count: {summary['recent_history_count']}")
        print(f"   Current file: {summary['file_context'].get('last_analyzed_file')}")
        print(f"   Project path: {summary['project_context'].get('current_project_path')}")
        
        assert summary['total_interactions'] == 4, "Should have 4 interactions"
        assert summary['recent_history_count'] == 4, "Should have 4 history entries"


def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print("🧪 SUITE DE TESTS: SISTEMA DE MEMORIA CONVERSACIONAL")
    print("="*70)
    
    try:
        test_conversation_memory_basic()
        test_update_context()
        test_infer_missing_context()
        test_file_tracking()
        test_persistence()
        test_project_detection()
        test_summary()
        
        print("\n" + "="*70)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*70)
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLÓ: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
