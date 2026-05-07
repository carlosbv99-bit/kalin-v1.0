import requests
import sys

BASE_URL = "http://127.0.0.1:5000/chat"

# Obtener comando completo
message = " ".join(sys.argv[1:])

if not message:
    print("Uso:")
    print("python cli.py /fix main.dart")
    exit()

try:
    response = requests.post(
        BASE_URL,
        json={"message": message}
    )

    data = response.json()

    print("\n🤖 RESPUESTA DEL AGENTE:\n")

    if "respuesta" in data:
        print(data["respuesta"])

    if "preview" in data and data["preview"]:
        print("\n📄 PREVIEW:\n")
        print(data["preview"])

except Exception as e:
    print(f"❌ Error: {e}")