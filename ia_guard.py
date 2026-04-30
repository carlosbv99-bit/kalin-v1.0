import subprocess
import os
from agent import app

EXTENSIONES_VALIDAS = [".kt", ".java"]

def obtener_archivos_modificados():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    archivos = result.stdout.splitlines()
    return [f for f in archivos if any(f.endswith(ext) for ext in EXTENSIONES_VALIDAS)]


def analizar_y_corregir(codigo):
    prompt = f"""
Eres un experto senior en Kotlin.

Corrige el código para que sea 100% funcional y compilable.

REGLAS:
- NO dejes variables sin asignar
- NO dejes funciones vacías
- COMPLETA el código si falta lógica
- SI hay errores, ARRÉGLALOS completamente
- DEVUELVE solo código limpio

CODIGO:
{codigo}
"""
    result = app.invoke({"input": prompt})
    return result["output"]


def es_codigo_valido(codigo):
    prompt = f"""
Eres un compilador estricto.

Responde SOLO:

OK → si el código compilaría correctamente
ERROR → si hay cualquier problema

CODIGO:
{codigo}
"""
    result = app.invoke({"input": prompt})
    return result["output"].strip().upper() == "OK"


def procesar_archivo(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        original = f.read()

    print(f"\n🔍 IA revisando: {ruta}")

    corregido = analizar_y_corregir(original)

    if corregido.strip() != original.strip():
        print("🛠 IA corrigió el archivo")

        # backup
        with open(ruta + ".bak", "w", encoding="utf-8") as f:
            f.write(original)

        # guardar corregido
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(corregido)

        # volver a añadir al commit
        subprocess.run(["git", "add", ruta])

    # validar resultado final
    if not es_codigo_valido(corregido):
        print("❌ Código sigue con errores")
        return False

    print("✅ Código válido")
    return True


def main():
    archivos = obtener_archivos_modificados()

    if not archivos:
        print("✔️ Sin cambios relevantes")
        return 0

    for archivo in archivos:
        if not procesar_archivo(archivo):
            print(f"❌ Commit bloqueado por IA en: {archivo}")
            return 1

    print("🚀 Todo corregido automáticamente")
    return 0


if __name__ == "__main__":
    exit(main())