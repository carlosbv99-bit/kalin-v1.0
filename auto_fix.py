import os
from agent import app

CARPETA_PROYECTO = "E:\\agente\\mi_app"

IGNORAR = ["agent.py", "main.py", "auto_fix.py"]
EXCLUIR_CARPETAS = ["build", ".gradle", ".idea"]

def procesar_archivo(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        codigo = f.read()

    print(f"\n🔍 Analizando: {ruta}")

    result = app.invoke({"input": codigo})
    corregido = result["output"]

    # 🔒 backup antes de sobrescribir
    with open(ruta + ".bak", "w", encoding="utf-8") as f:
        f.write(codigo)

    # guardar archivo corregido
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(corregido)

    print(f"✅ Corregido: {ruta}")


def recorrer_proyecto():
    for root, dirs, files in os.walk(CARPETA_PROYECTO):

        # evitar carpetas basura
        dirs[:] = [d for d in dirs if d not in EXCLUIR_CARPETAS]

        for file in files:
            if file not in IGNORAR and (file.endswith(".kt") or file.endswith(".java")):
                ruta = os.path.join(root, file)
                procesar_archivo(ruta)


if __name__ == "__main__":
    recorrer_proyecto()