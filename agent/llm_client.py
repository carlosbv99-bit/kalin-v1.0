import requests

def generar_respuesta(prompt, max_tokens=80):
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-coder",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.2
                }
            },
            timeout=60
        )

        return r.json().get("response", "")

    except Exception as e:
        return f"❌ Error IA: {str(e)}"