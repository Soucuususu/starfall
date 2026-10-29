
import json
import os
import time
from pathlib import Path

import requests

HOST = "Starfall-t6RL.aternos.me"
PORT = 19132
STATE_FILE = Path("status.json")
WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]

API_URL = (
    "https://api.mcstatus.io/v2/status/bedrock/"
    f"{HOST}:{PORT}"
)


def check_server():
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data.get("online"), bool):
            return None

        if data["online"]:
            return "online"

        # Confirma o offline para reduzir falsos alarmes.
        time.sleep(15)

        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        second = response.json()

        if not isinstance(second.get("online"), bool):
            return None

        if second["online"]:
            return None

        return "offline"

    except (requests.RequestException, ValueError) as error:
        print(f"Falha na consulta: {error}")
        return None


def notify(status):
    online = status == "online"

    title = (
        "Starfall está ONLINE!"
        if online else
        "Starfall está OFFLINE!"
    )

    description = (
        "O servidor está disponível. "
        "Entre no Minecraft Bedrock e venha jogar!"
        if online else
        "O servidor não respondeu em duas verificações. "
        "A Staff verificará quando ele voltar."
    )

    color = 3066993 if online else 15158332

    payload = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "fields": [
                {
                    "name": "Endereço",
                    "value": f"`{HOST}:{PORT}`",
                    "inline": False
                },
                {
                    "name": "Edição",
                    "value": "Minecraft Bedrock",
                    "inline": True
                }
            ],
            "footer": {
                "text": "Starfall • Monitoramento automático"
            }
        }]
    }

    response = requests.post(
        WEBHOOK,
        json=payload,
        timeout=15
    )
    response.raise_for_status()


def main():
    if STATE_FILE.exists():
        previous = json.loads(
            STATE_FILE.read_text(encoding="utf-8")
        ).get("status", "unknown")
    else:
        previous = "unknown"

    current = check_server()

    if current is None:
        print("Estado inconclusivo; sem alterar o registro.")
        return

    if current == previous:
        print(f"Sem mudança: {current}")
        return

    # Só registra a mudança depois de enviar o aviso.
    notify(current)

    STATE_FILE.write_text(
        json.dumps({"status": current}, indent=2) + "\n",
        encoding="utf-8"
    )

    print(f"Estado atualizado: {previous} -> {current}")


if __name__ == "__main__":
    main()
      
