import subprocess
import os
from agent import app

EXTENSIONES_VALIDAS = [".kt", ".java"]

def obtener_archivos_modificados():
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True
    )

    archivos = result.stdout.splitlines()
    return [f for f in archivos if any(f.endswith(ext) for ext in EXTENSIONES_VALIDAS)]


def procesar_archivo(ruta):
    if not os.path.exists(ruta):
        return

    with open(ruta, "r", encoding="utf-8") as f:
        codigo = f.read()

    print(f"\n🔍 IA analizando: {ruta}")

    result = app.invoke({"input": codigo})
    corregido = result["output"]

    # backup
    with open(ruta + ".bak", "w", encoding="utf-8") as f:
        f.write(codigo)

    # guardar corregido
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(corregido)

    print(f"✅ IA corrigió: {ruta}")


def main():
    archivos = obtener_archivos_modificados()

    if not archivos:
        print("✔️ No hay cambios para procesar")
        return

    for archivo in archivos:
        procesar_archivo(archivo)


if __name__ == "__main__":
    main()