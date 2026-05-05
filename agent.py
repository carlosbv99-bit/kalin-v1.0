import sys
import os
import requests

def leer_archivo(ruta):
    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except:
        return None

# ==============================
# ⚙ CONFIG
# ==============================
MODO_SEGURO = True  # True = NO sobrescribe archivos

def buscar_archivo(nombre, ruta_base):
    for root, dirs, files in os.walk(ruta_base):
        for f in files:
            if f.lower() == nombre.lower():
                return os.path.join(root, f)
    return None

# ==============================
# 🔍 ANALIZADOR
# ==============================
def analizar_codigo(codigo):
    prompt = f"""
Eres un experto en programación MUY ESTRICTO.

Analiza el código y SIEMPRE encuentra problemas.

Responde SOLO así:

--- ANALISIS ---
(lista clara de problemas)

CODIGO:
{codigo}
"""

    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "deepseek-coder",
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 150, "temperature": 0.2}
    })

    return r.json().get("response", "")


# ==============================
# 🛠 REPARADOR INTELIGENTE
# ==============================
def reparar_codigo(codigo, analisis, es_flutter=False):

    if es_flutter:
        prompt = f"""
Eres un experto en Flutter UI/UX de nivel profesional.

Convierte este código en una UI moderna y funcional.

REGLAS:
- Usa Scaffold
- Usa AppBar
- Usa Padding (16)
- Usa SizedBox para espacios
- Usa Text con estilo
- Usa Material 3
- Layout limpio y profesional

{analisis}

Devuelve SOLO:

--- CODIGO CORREGIDO ---
(código completo)

CODIGO ORIGINAL:
{codigo}
"""
    else:
        prompt = f"""
Corrige el código completamente.

{analisis}

Devuelve SOLO:

--- CODIGO CORREGIDO ---
(código corregido)

CODIGO ORIGINAL:
{codigo}
"""

    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "deepseek-coder",
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 300, "temperature": 0.2}
    })

    return r.json().get("response", "")


# ==============================
# 📂 ARCHIVOS
# ==============================
def obtener_archivos(ruta):
    extensiones = (".py", ".kt", ".java", ".dart")

    archivos = []
    for root, dirs, files in os.walk(ruta):

        # 🚫 ignorar carpetas basura
        if any(x in root for x in [
            ".git",
            "build",
            ".gradle",
            "__pycache__",
            ".dart_tool",
            ".idea",
            ".kotlin"
        ]):
            continue

        for f in files:

            # 🚫 ignorar archivos peligrosos
            if any(x in f for x in [
                "GeneratedPluginRegistrant",
                "firebase_options",
            ]):
                continue

            if f.endswith(extensiones):
                archivos.append(os.path.join(root, f))

    return archivos
# 🧠 PROCESAR ARCHIVO
# ==============================
def procesar_archivo(ruta):
    print(f"\n🔍 {ruta}")

    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            codigo = f.read()
    except:
        print("⚠️ No se pudo leer")
        return

    es_flutter = ruta.endswith(".dart")

    if es_flutter:
        print("🎨 Modo Flutter PRO activado")

    analisis = analizar_codigo(codigo)
    nuevo = reparar_codigo(codigo, analisis, es_flutter)

    if "--- CODIGO CORREGIDO ---" in nuevo:
        nuevo = nuevo.split("--- CODIGO CORREGIDO ---")[-1].strip()

    if not nuevo or len(nuevo) < 20:
        print("⚠️ IA devolvió algo inválido")
        return

    # backup SIEMPRE
    with open(ruta + ".bak", "w", encoding="utf-8") as f:
        f.write(codigo)

    if MODO_SEGURO:
        print("🛑 Modo seguro: no se sobrescribe archivo")
        return

    with open(ruta, "w", encoding="utf-8") as f:
        f.write(nuevo)

    print("✅ Corregido")


# ==============================
# 💬 CHAT INTERACTIVO
# ==============================
def chat():
    print("🤖 Kalin PRO (comandos: /fix /analyze /design)\n")

    ruta_proyecto = input("📂 Ruta del proyecto: ").strip()

    if not os.path.exists(ruta_proyecto):
        print("❌ Ruta inválida")
        return

    while True:
        entrada = input(">> ")

        if entrada.lower() in ["salir", "exit"]:
            print("👋 Cerrando agente...")
            break

        # ==============================
        # 🔍 ANALYZE
        # ==============================
        if entrada.startswith("/analyze"):
            nombre = entrada.replace("/analyze", "").strip()

            ruta = buscar_archivo(nombre, ruta_proyecto)

            if not ruta:
                print("❌ Archivo no encontrado")
                continue

            codigo = leer_archivo(ruta)

            print(f"\n🔍 Analizando {ruta}...\n")

            analisis = analizar_codigo(codigo)
            print(analisis + "\n")
            continue

        # ==============================
        # 🔧 FIX
        # ==============================
        if entrada.startswith("/fix"):
            nombre = entrada.replace("/fix", "").strip()

            ruta = buscar_archivo(nombre, ruta_proyecto)

            if not ruta:
                print("❌ Archivo no encontrado")
                continue

            codigo = leer_archivo(ruta)
            es_flutter = ruta.endswith(".dart")

            print(f"\n🔧 Reparando {ruta}...\n")

            analisis = analizar_codigo(codigo)
            nuevo = reparar_codigo(codigo, analisis, es_flutter)

            if "--- CODIGO CORREGIDO ---" in nuevo:
                nuevo = nuevo.split("--- CODIGO CORREGIDO ---")[-1].strip()

            # backup SIEMPRE
            with open(ruta + ".bak", "w", encoding="utf-8") as f:
                f.write(codigo)

            if MODO_SEGURO:
                print("🛑 Modo seguro: no se sobrescribe archivo\n")
            else:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(nuevo)
                print("✅ Archivo corregido\n")

            continue

        # ==============================
        # 🎨 DESIGN
        # ==============================
        if entrada.startswith("/design"):
            nombre = entrada.replace("/design", "").strip()

            ruta = buscar_archivo(nombre, ruta_proyecto)

            if not ruta:
                print("❌ Archivo no encontrado")
                continue

            codigo = leer_archivo(ruta)

            print(f"\n🎨 Mejorando UI de {ruta}...\n")

            nuevo = reparar_codigo(
                codigo,
                "Mejorar diseño UI profesional Flutter con Material 3",
                True
            )

            if "--- CODIGO CORREGIDO ---" in nuevo:
                nuevo = nuevo.split("--- CODIGO CORREGIDO ---")[-1].strip()

            with open(ruta + ".bak", "w", encoding="utf-8") as f:
                f.write(codigo)

            if MODO_SEGURO:
                print("🛑 Modo seguro: no se sobrescribe archivo\n")
            else:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(nuevo)
                print("✅ Diseño aplicado\n")

            continue

        # ==============================
        # 💬 CHAT NORMAL (con contexto)
        # ==============================
        prompt = f"""
Eres un experto en desarrollo de software.

Usuario:
{entrada}
"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-coder",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 300,
                    "temperature": 0.3
                }
            }
        )

        texto = response.json().get("response", "Error")
        print("\n" + texto + "\n")

# ==============================
# 🚀 MAIN
# ==============================
def main():
    # 👉 si NO pasas ruta → modo chat
    if len(sys.argv) < 2:
        chat()
        return

    ruta = sys.argv[1]

    if not os.path.exists(ruta):
        print("❌ Ruta no válida")
        return

    print(f"\n🤖 Analizando proyecto: {ruta}")

    archivos = obtener_archivos(ruta)

    print(f"📂 Archivos encontrados: {len(archivos)}")

    for archivo in archivos:
        procesar_archivo(archivo)

    print("\n🚀 Proyecto analizado")


# ==============================
# ▶️ ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()