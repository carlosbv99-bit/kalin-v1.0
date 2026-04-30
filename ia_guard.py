import subprocess
import os
from agent import app

EXTENSIONES_VALIDAS = [".kt", ".java"]

# 🔍 archivos modificados en git
def obtener_archivos_modificados():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )

    archivos = result.stdout.splitlines()
    archivos_validos = []

    for f in archivos:
        if not any(f.endswith(ext) for ext in EXTENSIONES_VALIDAS):
            continue

        if not f.startswith("mi_app_android1/"):
            continue

        if "src/main" not in f:
            continue

        archivos_validos.append(f)

    return archivos_validos


# 🧠 IA corrige código
def analizar_y_corregir(codigo):
    prompt = f"""
Eres un experto senior en Kotlin.

Corrige el código para que sea 100% funcional y compilable.

REGLAS:
- NO dejes variables sin asignar
- NO dejes funciones vacías
- COMPLETA el código si falta lógica
- SI hay errores, ARRÉGLALOS completamente
- DEVUELVE solo código limpio (sin explicaciones)

CODIGO:
{codigo}
"""
    result = app.invoke({"input": prompt})
    return result["output"]


# 🧹 limpiar salida IA
def limpiar_codigo(texto):
    # 🔥 buscar bloque ```kotlin
    if "```" in texto:
        partes = texto.split("```")

        for parte in partes:
            if "kotlin" in parte.lower():
                # quitar la palabra kotlin
                parte = parte.replace("kotlin", "")
                return parte.strip()

        # fallback: usar segunda parte
        if len(partes) >= 2:
            return partes[1].strip()

    # 🔥 fallback si no hay markdown
    lineas = texto.splitlines()
    limpio = []

    for l in lineas:
        l_strip = l.strip().lower()

        if not l.strip():
            continue
        if "lo siento" in l_strip:
            continue
        if "aquí tienes" in l_strip:
            continue
        if "codigo" in l_strip:
            continue

        limpio.append(l)

    # cortar hasta encontrar código real
    for i, l in enumerate(limpio):
        if l.strip().startswith("package") or l.strip().startswith("import"):
            limpio = limpio[i:]
            break

    return "\n".join(limpio).strip()


# 🛠 procesar archivo (UNA SOLA VEZ)
def procesar_archivo(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        original = f.read()

    print(f"\n🔍 IA revisando: {ruta}")

    corregido = limpiar_codigo(analizar_y_corregir(original))

    if corregido.strip() != original.strip():
        print("🛠 IA corrigió el archivo")

        with open(ruta + ".bak", "w", encoding="utf-8") as f:
            f.write(original)

        with open(ruta, "w", encoding="utf-8") as f:
            f.write(corregido)

        subprocess.run(["git", "add", ruta])

    print("✅ Archivo procesado")
    return True


# 🏗 BUILD REAL ANDROID
def compilar_proyecto():
    print("\n🏗 Ejecutando build Android...")

    result = subprocess.run(
        [".\\gradlew.bat", "build"],
        cwd="E:\\agente\\mi_app_android1",
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ Build exitoso")
        return True
    else:
        print("❌ Error en build:")
        print(result.stderr[:500])
        return False


# 🚀 MAIN
def main():
    archivos = obtener_archivos_modificados()

    if not archivos:
        print("✔️ Sin cambios relevantes")
        return 0

    for archivo in archivos:
        if not procesar_archivo(archivo):
            print(f"❌ Commit bloqueado por IA en: {archivo}")
            return 1

    if not compilar_proyecto():
        print("❌ Commit bloqueado por fallo en build")
        return 1

    print("🚀 Proyecto válido y compilado")
    return 0


if __name__ == "__main__":
    exit(main())