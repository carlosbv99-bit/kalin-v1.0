from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import difflib

from agent.core.orchestrator import Orchestrator
from agent.actions.tools.scan_tool import escanear_proyecto
from agent.analyzer import analizar_codigo
from agent.core.brain import construir_contexto, planificar

app = Flask(__name__)
CORS(app)

orchestrator = Orchestrator()

MODO_SEGURO = True
RUTA_PROYECTO = ""
ULTIMO_FIX = None

# ==============================
# 🌐 WEB
# ==============================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/help")
def help_page():
    return jsonify({
        "respuesta": "Comandos disponibles: /setpath <ruta>, /scan, /fix <archivo>, /apply, /analyze <archivo>, /create <requerimiento>, /refactor <archivo>"
    })

# ==============================
# 📁 UTILS
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
    for root, _, files in os.walk(ruta_base):
        for f in files:
            nombre = f.lower()
            ruta = os.path.join(root, f)

            if query in nombre:
                score = 0
                if nombre == query:
                    score += 100
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
    except:
        return False

def limpiar_codigo(texto):
    if not texto:
        return ""
    texto = texto.replace("`python", "").replace("`", "")
    return texto.strip()

def generar_diff(original, nuevo):
    diff = difflib.unified_diff(
        original.splitlines(),
        nuevo.splitlines(),
        lineterm=""
    )
    return "\n".join(diff)

# ==============================
# 🧠 API
# ==============================

@app.route("/chat", methods=["POST"])
def chat():
    global RUTA_PROYECTO, ULTIMO_FIX

    data = request.json or {}
    mensaje = (data.get("mensaje") or data.get("command") or data.get("message") or "").strip()

    estado = {
        "ruta_proyecto": RUTA_PROYECTO,
        "ultimo_fix": ULTIMO_FIX
    }

    utils = {
        "leer_archivo": leer_archivo,
        "buscar_archivo_inteligente": buscar_archivo_inteligente,
        "limpiar_codigo": limpiar_codigo,
        "generar_diff": generar_diff,
        "es_codigo_valido": es_codigo_valido,
        "guardar_backup": guardar_backup,
        "escribir_archivo": escribir_archivo,
        "analizar_codigo": analizar_codigo
    }

    try:
        response = orchestrator.handle(mensaje, estado, utils)
    except Exception as exc:
        return jsonify({"respuesta": f"❌ Error interno: {str(exc)}"}), 500

    RUTA_PROYECTO = estado.get("ruta_proyecto", RUTA_PROYECTO)
    ULTIMO_FIX = estado.get("ultimo_fix", ULTIMO_FIX)

    return response

# ==============================
# 🚀 START
# ==============================

if __name__ == "__main__":
    print("🚀 Iniciando servidor...")
    app.run(host="0.0.0.0", port=5000, debug=False)