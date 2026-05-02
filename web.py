MODO_SEGURO = True
ULTIMO_FIX = None

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import difflib

# 🧠 agente
from agent.brain import construir_contexto, planificar
from agent.executor import ejecutar

# 🤖 módulos IA
from agent.scanner import escanear_proyecto
from agent.analyzer import analizar_codigo
from agent.fixer import reparar_codigo

app = Flask(__name__)
CORS(app)

# ==============================
# 🌐 RUTA WEB
# ==============================
@app.route("/")
def home():
    return render_template("index.html")

# ==============================
# 📂 CONFIG
# ==============================
RUTA_PROYECTO = ""

# ==============================
# 📁 FUNCIONES ARCHIVOS
# ==============================
def leer_archivo(ruta):
    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except:
        return None


def buscar_archivo_inteligente(query, ruta_base):
    query = query.lower()
    candidatos = []

    for root, dirs, files in os.walk(ruta_base):
        for f in files:
            nombre = f.lower()
            ruta = os.path.join(root, f)

            if query in nombre:
                score = 0

                if nombre == query:
                    score += 100
                if query in nombre:
                    score += 50
                if "main" in nombre:
                    score += 20
                if "app" in nombre:
                    score += 10
                if "test" in nombre:
                    score -= 10

                candidatos.append((score, ruta))

    if not candidatos:
        return None

    candidatos.sort(reverse=True)
    return candidatos[0][1]


def guardar_backup(ruta, contenido):
    with open(ruta + ".bak", "w", encoding="utf-8") as f:
        f.write(contenido)


def escribir_archivo(ruta, contenido):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)


def es_codigo_valido(codigo):
    if not codigo or len(codigo.strip()) < 10:
        return False

    try:
        compile(codigo, "<string>", "exec")
        return True
    except Exception as e:
        print("⚠️ Error compilando:", str(e))
        return False


def limpiar_codigo(texto):
    if not texto:
        return ""

    # 🔒 1. intentar <code>
    if "<code>" in texto and "</code>" in texto:
        texto = texto.split("<code>")[1].split("</code>")[0]

    # 🔁 2. quitar markdown
    texto = texto.replace("```python", "").replace("```", "")

    # 🔥 3. eliminar TODO lo que no sea código al inicio
    lineas = texto.splitlines()

    inicio = None
    for i, l in enumerate(lineas):
        l_strip = l.strip()
        if (
            l_strip.startswith("import ")
            or l_strip.startswith("from ")
            or l_strip.startswith("def ")
            or l_strip.startswith("class ")
            or l_strip.startswith("@")
        ):
            inicio = i
            break

    if inicio is not None:
        lineas = lineas[inicio:]

    texto = "\n".join(lineas)

    # 🔥 4. cortar basura al final (explicaciones)
    fin = len(texto)
    for marcador in [
        "\nEl código",
        "\nEste código",
        "\nExplicación",
        "\nNota:",
    ]:
        idx = texto.find(marcador)
        if idx != -1:
            fin = min(fin, idx)

    texto = texto[:fin]

    return texto.strip()


def generar_diff(original, nuevo):
    diff = difflib.unified_diff(
        original.splitlines(),
        nuevo.splitlines(),
        lineterm=""
    )
    return "\n".join(diff)


# ==============================
# 🧠 API CHAT (AGENTE REAL)
# ==============================
@app.route("/chat", methods=["POST"])
def chat():
    global RUTA_PROYECTO
    global ULTIMO_FIX

    data = request.json
    mensaje = (data.get("mensaje") or "").strip()

    print("📩 MENSAJE:", mensaje)

    # ==========================
    # 🧠 CONTEXTO
    # ==========================
    estado = {
        "ruta_proyecto": RUTA_PROYECTO,
        "ultimo_fix": ULTIMO_FIX
    }

    contexto = construir_contexto(mensaje, estado)
    contexto = planificar(contexto)

    intencion = contexto["intencion"]
    args = contexto.get("args", {})

    print("🧠 INTENCIÓN:", intencion)

    # ==========================
    # 📂 SETPATH
    # ==========================
    if intencion == "setpath":
        ruta = args.get("arg")

        if not ruta:
            return jsonify({"respuesta": "❌ Usa: /setpath ruta"})

        RUTA_PROYECTO = ruta
        return jsonify({"respuesta": f"📂 Ruta configurada: {RUTA_PROYECTO}"})

    # ==========================
    # 📊 SCAN
    # ==========================
    if intencion == "scan":
        if not RUTA_PROYECTO:
            return jsonify({"respuesta": "⚠️ Primero usa /setpath"})

        data_scan = escanear_proyecto(RUTA_PROYECTO)

        return jsonify({
            "respuesta": "📊 Escaneo completado",
            "data": data_scan
        })

    # ==========================
    # 💾 APPLY
    # ==========================
    if intencion == "apply":
        if not ULTIMO_FIX:
            return jsonify({"respuesta": "❌ No hay cambios pendientes"})

        ruta = ULTIMO_FIX["ruta"]
        original = ULTIMO_FIX["codigo_original"]
        nuevo = ULTIMO_FIX["codigo_nuevo"]

        if not es_codigo_valido(nuevo):
            return jsonify({
                "respuesta": "❌ Código inválido"
            })

        guardar_backup(ruta, original)
        escribir_archivo(ruta, nuevo)

        ULTIMO_FIX = None

        return jsonify({"respuesta": "✅ Cambios aplicados correctamente"})

    # ==========================
    # 🤖 AGENTE (FIX / CREATE / ETC)
    # ==========================
    utils = {
        "leer_archivo": leer_archivo,
        "buscar_archivo_inteligente": buscar_archivo_inteligente,
        "limpiar_codigo": limpiar_codigo,
        "generar_diff": generar_diff,
        "es_codigo_valido": es_codigo_valido,
        "guardar_backup": guardar_backup,
        "escribir_archivo": escribir_archivo,

        # 🧠 IA
        "analizar_codigo": analizar_codigo,
        "reparar_codigo": reparar_codigo,

        # 🔥 NUEVO (CLAVE)
        "agente_fix_codigo": agente_fix_codigo
    }

    response = ejecutar(contexto, utils)

    # 🔄 sincronizar estado
    ULTIMO_FIX = contexto["estado"].get("ultimo_fix", ULTIMO_FIX)

    return response


# ==============================
# 🚀 START
# ==============================
if __name__ == "__main__":
    app.run(port=5000)