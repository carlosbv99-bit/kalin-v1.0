import subprocess
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


def validar_codigo(codigo):
    prompt = f"""
Eres un revisor de código MUY ESTRICTO.

Analiza el código y decide:

Si el código es correcto → responde SOLO: OK
Si hay errores → responde SOLO: ERROR

CODIGO:
{codigo}
"""

    result = app.invoke({"input": prompt})
    respuesta = result["output"].strip().upper()

    return respuesta == "OK"


def main():
    archivos = obtener_archivos_modificados()

    if not archivos:
        print("✔️ Sin cambios relevantes")
        return 0

    for archivo in archivos:
        with open(archivo, "r", encoding="utf-8") as f:
            codigo = f.read()

        print(f"🔍 Revisando con IA: {archivo}")

        if not validar_codigo(codigo):
            print(f"❌ IA bloqueó el commit en: {archivo}")
            return 1

    print("✅ Código aprobado por IA")
    return 0


if __name__ == "__main__":
    exit(main())