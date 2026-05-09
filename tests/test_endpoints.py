"""Test de endpoints REST del agente"""
import requests
import json
import sys

base = 'http://127.0.0.1:5000'
passed = 0
failed = 0

# Verificar si el servidor está corriendo
try:
    r = requests.get(f"{base}/health", timeout=2)
    print("✅ Servidor detectado en http://127.0.0.1:5000")
except:
    print("❌ ERROR: El servidor no está corriendo en http://127.0.0.1:5000")
    print("   Para ejecutar este test, primero inicia el servidor con:")
    print("   python run.py")
    print("\n   O usa los otros tests que no requieren servidor:")
    print("   - test_funcional.py")
    print("   - test_llm_providers.py")
    print("   - test_new_architecture.py")
    print("   - test_new_components.py")
    sys.exit(1)

def test_endpoint(name, method, path, json_data=None, expect_status=200, timeout=10):
    global passed, failed
    try:
        if method == "GET":
            r = requests.get(f"{base}{path}", timeout=timeout)
        else:
            r = requests.post(f"{base}{path}", json=json_data or {}, timeout=timeout)
        
        status_ok = r.status_code == expect_status
        emoji = "✅" if status_ok else "❌"
        
        try:
            body = r.json()
            body_str = json.dumps(body, indent=2, ensure_ascii=False)[:300]
        except:
            body_str = r.text[:200]
        
        print(f"   {emoji} [{r.status_code}] {name}")
        if not status_ok:
            print(f"      Esperado: {expect_status}, Obtenido: {r.status_code}")
            print(f"      Body: {body_str}")
            failed += 1
        else:
            print(f"      {body_str[:150]}...")
            passed += 1
        
        return r
    except Exception as e:
        print(f"   ❌ {name}: {e}")
        failed += 1
        return None

def test_command(name, command, timeout=60):
    """Envía un comando via /chat y verifica respuesta"""
    global passed, failed
    try:
        r = requests.post(f"{base}/chat", json={"message": command}, timeout=timeout)
        body = r.json()
        respuesta = body.get("respuesta", "")
        
        is_error = "❌" in respuesta or "Error" in respuesta
        emoji = "✅" if r.status_code == 200 and not is_error else "⚠️"
        
        print(f"   {emoji} [{r.status_code}] {name}")
        print(f"      Comando: {command}")
        print(f"      Respuesta: {respuesta[:150]}")
        
        if r.status_code == 200:
            passed += 1
        else:
            failed += 1
        
        return body
    except Exception as e:
        print(f"   ❌ {name}: {e}")
        failed += 1
        return None

print("=" * 60)
print("TEST COMPLETO DE ENDPOINTS")
print("=" * 60)

# ─── ENDPOINTS ESTÁTICOS ───
print("\n📡 ENDPOINTS ESTÁTICOS:")
test_endpoint("Health check", "GET", "/health")
test_endpoint("LLM Status", "GET", "/llm-status")
test_endpoint("Help page", "GET", "/help")
test_endpoint("Home page", "GET", "/", expect_status=200)

# ─── COMANDOS VIA /chat ───
print("\n🧠 COMANDOS VIA /chat:")

# Help
test_command("Help", "/help")

# Setpath
test_command("Setpath", "/setpath E:\\kalin")

# Scan
test_command("Scan", "/scan", timeout=30)

# Fix (archivo simple)
test_command("Fix", "/fix agent/core/brain.py", timeout=120)

# Apply (sin cambios pendientes)
test_command("Apply (no changes)", "/apply")

# Chat normal
test_command("Chat normal", "Hola, ¿qué puedes hacer?", timeout=60)

# ─── RESUMEN ───
print("\n" + "=" * 60)
print(f"RESULTADOS: {passed} ✅ / {failed} ❌ / {passed + failed} total")
print("=" * 60)
