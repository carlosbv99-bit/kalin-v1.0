import os

EXTENSIONES = {
    ".py": "python",
    ".dart": "flutter",
    ".kt": "kotlin",
    ".java": "java",
}

def escanear_proyecto(ruta_base):
    resultado = {
        "archivos": [],
        "resumen": {},
        "tipo_proyecto": "desconocido",
        "indicadores": []
    }

    ignore_dirs = {".git", ".venv", "build", ".gradle", "__pycache__", ".idea", ".dart_tool", "node_modules", ".github", "dist", "venv"}

    for root, dirs, files in os.walk(ruta_base):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for f in files:
            ruta = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()

            tipo = EXTENSIONES.get(ext)

            if tipo:
                resultado["archivos"].append(ruta)

                if tipo not in resultado["resumen"]:
                    resultado["resumen"][tipo] = 0

                resultado["resumen"][tipo] += 1

            # 🔍 detectar cosas importantes
            if f == "pubspec.yaml":
                resultado["indicadores"].append("flutter")
            if f == "requirements.txt":
                resultado["indicadores"].append("python")
            if f == "build.gradle":
                resultado["indicadores"].append("android")

    # 🧠 detectar tipo de proyecto
    # 🧠 detectar tipo de proyecto (mejorado)

    if "flutter" in resultado["indicadores"]:
        resultado["tipo_proyecto"] = "Flutter"

    elif ".kt" in resultado["resumen"] and ".py" in resultado["resumen"]:
        resultado["tipo_proyecto"] = "Mixto (Python + Android)"

    elif ".kt" in resultado["resumen"]:
        resultado["tipo_proyecto"] = "Android (Kotlin)"

    elif ".py" in resultado["resumen"]:
        resultado["tipo_proyecto"] = "Python"

    else:
        resultado["tipo_proyecto"] = "Desconocido"

    return resultado