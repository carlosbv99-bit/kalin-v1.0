import os

EXTENSIONES = [".py", ".dart", ".kt", ".java"]

def escanear_proyecto(ruta_base):
    resultado = {
        "archivos": [],
        "resumen": {},
        "tipo_proyecto": "desconocido",
        "indicadores": []
    }

    for root, dirs, files in os.walk(ruta_base):
        for f in files:
            ruta = os.path.join(root, f)
            ext = os.path.splitext(f)[1]

            if ext in EXTENSIONES:
                resultado["archivos"].append(ruta)

                if ext not in resultado["resumen"]:
                    resultado["resumen"][ext] = 0

                resultado["resumen"][ext] += 1

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