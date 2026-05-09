#!/usr/bin/env python3
"""
Script de prueba rápida para verificar las correcciones de memoria contextual.
Ejecuta este script después de iniciar el servidor web.
"""

import requests
import json
import time

# Configuración
BASE_URL = "http://127.0.0.1:5000"
session_id = None

def send_message(message, expected_keywords=None):
    """Envía un mensaje al chat y muestra la respuesta"""
    global session_id
    
    print(f"\n{'='*70}")
    print(f"📤 Enviando: {message}")
    print(f"{'='*70}")
    
    data = {"mensaje": message}
    if session_id:
        data["session_id"] = session_id
        print(f"📝 Usando session_id: {session_id}")
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=data)
        result = response.json()
        
        # Guardar session_id
        if "session_id" in result:
            session_id = result["session_id"]
            print(f"✅ Session ID recibido: {session_id}")
        
        # Mostrar respuesta
        respuesta = result.get("respuesta", "Sin respuesta")
        print(f"\n📥 Respuesta:\n{respuesta[:500]}...")  # Primeros 500 chars
        
        # Verificar keywords esperadas
        if expected_keywords:
            for keyword in expected_keywords:
                if keyword.lower() in respuesta.lower():
                    print(f"✅ Keyword encontrada: '{keyword}'")
                else:
                    print(f"❌ Keyword NO encontrada: '{keyword}'")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_agenda_personal():
    """Prueba 1: Crear agenda personal (no calendario)"""
    print("\n" + "="*70)
    print("🧪 PRUEBA 1: Agenda Personal vs Calendario")
    print("="*70)
    
    result = send_message(
        "quiero crear una agenda personal en Python",
        expected_keywords=["agenda", "contacto", "class"]
    )
    
    if result:
        respuesta = result.get("respuesta", "")
        if "calendar" in respuesta.lower() or "calendario" in respuesta.lower():
            print("\n❌ FALLO: Generó código de calendario en lugar de agenda")
        else:
            print("\n✅ ÉXITO: No generó código de calendario")

def test_continuacion_codigo():
    """Prueba 2: Continuación de código"""
    print("\n" + "="*70)
    print("🧪 PRUEBA 2: Continuación de Código")
    print("="*70)
    
    send_message(
        "agrega función para eliminar contactos",
        expected_keywords=["eliminar", "delete", "remove"]
    )

def test_inferencia_lenguaje():
    """Prueba 3: Inferencia de lenguaje"""
    print("\n" + "="*70)
    print("🧪 PRUEBA 3: Inferencia de Lenguaje Java")
    print("="*70)
    
    result = send_message(
        "quiero una app en Java",
        expected_keywords=["java", "class", "public"]
    )

def test_memoria_contextual():
    """Prueba 4: Memoria contextual con referencias implícitas"""
    print("\n" + "="*70)
    print("🧪 PRUEBA 4: Memoria Contextual")
    print("="*70)
    
    # Primero analizar algo
    send_message("hola")
    time.sleep(1)
    
    # Luego hacer referencia implícita
    send_message(
        "¿qué puedes hacer?",
        expected_keywords=["puedo", "ayudar", "función"]
    )

def main():
    """Ejecutar todas las pruebas"""
    print("\n" + "="*70)
    print("🚀 INICIANDO PRUEBAS DE MEMORIA CONTEXTUAL")
    print("="*70)
    print(f"📍 Servidor: {BASE_URL}")
    print(f"⏰ Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar que el servidor esté activo
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code == 200:
            print("✅ Servidor está activo")
        else:
            print(f"⚠️  Servidor respondió con código {health.status_code}")
    except:
        print("❌ ERROR: El servidor no está accesible")
        print("   Inicia el servidor con: python web.py")
        return
    
    input("\nPresiona Enter para comenzar las pruebas...")
    
    # Ejecutar pruebas
    test_agenda_personal()
    time.sleep(2)
    
    test_continuacion_codigo()
    time.sleep(2)
    
    test_inferencia_lenguaje()
    time.sleep(2)
    
    test_memoria_contextual()
    
    print("\n" + "="*70)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*70)
    print(f"\n📊 Resumen:")
    print(f"   Session ID final: {session_id}")
    print(f"   Total de mensajes enviados: 5")
    print(f"\n💡 Revisa los resultados arriba para verificar que todo funciona correctamente.")
    print(f"   Si ves ✅ significa que pasó la prueba.")
    print(f"   Si ves ❌ significa que falló y necesita corrección.")

if __name__ == "__main__":
    main()
