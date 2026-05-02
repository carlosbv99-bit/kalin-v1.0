# agent/executor.py

from flask import jsonify

# tools existentes
from agent.analyzer import analizar_codigo
from agent.fixer import reparar_codigo


def ejecutar(contexto, utils):
    """
    Ejecuta la acción decidida por el brain.

    utils = {
        leer_archivo,
        buscar_archivo_inteligente,
        limpiar_codigo,
        generar_diff,
        es_codigo_valido,
        guardar_backup,
        escribir_archivo
    }
    """

    intencion = contexto["intencion"]
    args = contexto.get("args", {})
    estado = contexto.get("estado", {})

    RUTA_PROYECTO = estado.get("ruta_proyecto")
    ULTIMO_FIX = estado.get("ultimo_fix")

    # ==========================
    # 🔧 FIX
    # ==========================
    if intencion == "fix":
        try:
            nombre = args.get("arg")

            if not nombre:
                return jsonify({"respuesta": "❌ Usa: /fix archivo"})

            if not RUTA_PROYECTO:
                return jsonify({"respuesta": "⚠️ Primero usa /setpath"})

            ruta = utils["buscar_archivo_inteligente"](nombre, RUTA_PROYECTO)

            if not ruta:
                return jsonify({"respuesta": "❌ Archivo no encontrado"})

            codigo = utils["leer_archivo"](ruta)

            if not codigo:
                return jsonify({"respuesta": "❌ No se pudo leer el archivo"})

            print("🧠 Analizando...")
            analisis = analizar_codigo(codigo)

            print("🛠 Reparando...")
            nuevo = reparar_codigo(codigo, analisis, ruta.endswith(".dart"))

            # ======================
            # 🧪 DEBUG + LIMPIEZA
            # ======================
            nuevo_raw = nuevo
            print("🧪 RAW:", repr(nuevo_raw))

            nuevo = utils["limpiar_codigo"](nuevo_raw)

            print("📏 ORIGINAL:", len(codigo))
            print("📏 NUEVO LIMPIO:", len(nuevo))
            print("🧹 LIMPIO:", repr(nuevo))

            # fallback si limpiar rompe
            if not nuevo:
                print("⚠️ usando RAW")
                nuevo = nuevo_raw

            if not nuevo:
                return jsonify({
                    "respuesta": "❌ IA devolvió vacío",
                    "preview": (nuevo_raw or "")[:500]
                })

            # ⚠️ solo aviso
            if len(nuevo) < len(codigo) * 0.3:
                print("⚠️ IA redujo mucho el código")

            # 🚫 bloquear chatbot
            if "Lo siento" in nuevo or "explicación" in nuevo:
                return jsonify({
                    "respuesta": "❌ IA respondió como chatbot"
                })

            # 🧠 validación real
            valido = utils["es_codigo_valido"](nuevo)

            if not valido:
                print("⚠️ Código no compila, pero se permite en modo seguro")

            # 💾 guardar en estado
            contexto["estado"]["ultimo_fix"] = {
                "ruta": ruta,
                "codigo_original": codigo,
                "codigo_nuevo": nuevo
            }

            diff = utils["generar_diff"](codigo, nuevo)

            return jsonify({
                "respuesta": "⚠️ Modo seguro activo (usa /apply para confirmar)",
                "preview": nuevo[:800],
                "diff": diff,
                "valido": valido
            })

        except Exception as e:
            print("💥 ERROR:", str(e))
            return jsonify({
                "respuesta": f"❌ Error interno: {str(e)}"
            })

    # ==========================
    # 🏗 CREATE (básico)
    # ==========================
    if intencion == "create":
        try:
            prompt = contexto["mensaje"]

            print("🏗 Generando aplicación...")

            nuevo = reparar_codigo("", prompt, False)

            if not nuevo:
                return jsonify({
                    "respuesta": "❌ No se pudo generar código",
                    "preview": ""
                })

            return jsonify({
                "respuesta": "✅ Código generado",
                "preview": nuevo[:800]
            })

        except Exception as e:
            return jsonify({
                "respuesta": f"❌ Error creando código: {str(e)}"
            })

    # ==========================
    # ❓ DEFAULT
    # ==========================
    return jsonify({
        "respuesta": "❓ Acción no soportada aún"
    })