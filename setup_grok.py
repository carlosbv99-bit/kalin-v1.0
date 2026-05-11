import os
import sys

def setup_grok_api():
    """Configura automáticamente la API de Grok (xAI) en Kalin"""
    print("🚀 Iniciando configuración automática de Grok (xAI)...")
    
    # 1. Solicitar la API Key al usuario
    api_key = input("🔑 Por favor, introduce tu API Key de xAI (Grok): ").strip()
    
    if not api_key:
        print("❌ Error: La API Key no puede estar vacía.")
        return

    # 2. Definir el modelo por defecto
    model = "grok-beta"
    
    # 3. Actualizar o crear el archivo .env
    env_path = ".env"
    env_lines = []
    grok_config_updated = False
    
    # Leer contenido actual si existe
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            if line.startswith("GROK_API_KEY="):
                env_lines.append(f"GROK_API_KEY={api_key}\n")
                grok_config_updated = True
            elif line.startswith("GROK_MODEL="):
                env_lines.append(f"GROK_MODEL={model}\n")
                grok_config_updated = True
            else:
                env_lines.append(line)
    
    # Si no se encontraron las variables, agregarlas al final
    if not grok_config_updated:
        env_lines.append(f"\n# Configuración de Grok (xAI)\n")
        env_lines.append(f"GROK_API_KEY={api_key}\n")
        env_lines.append(f"GROK_MODEL={model}\n")

    # Guardar cambios
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(env_lines)
    
    print(f"✅ Archivo .env actualizado correctamente en: {os.path.abspath(env_path)}")

    # 4. Verificar configuración en agent/llm/config.py
    config_path = os.path.join("agent", "llm", "config.py")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "ProviderType.GROK" not in content and "x.ai" not in content:
            print("⚠️  Nota: Revisa manualmente agent/llm/config.py para asegurar que el endpoint de xAI esté definido.")
            print("   Endpoint esperado: https://api.x.ai/v1/chat/completions")
        else:
            print("✅ Configuración de proveedor Grok detectada en config.py")
    
    print("\n" + "="*50)
    print("🎉 ¡Configuración de Grok completada!")
    print("="*50)
    print("💡 Siguientes pasos:")
    print("1. Reinicia Kalin si ya lo tenías abierto.")
    print("2. Asegúrate de seleccionar Grok como tu modelo activo.")
    print("3. ¡Empieza a chatear con Grok!")

if __name__ == "__main__":
    try:
        setup_grok_api()
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuración cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Ocurrió un error: {e}")
