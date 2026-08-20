
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

UNB_TOKEN = os.environ.get("UNB_TOKEN")
GUILD_ID = os.environ.get("UNB_GUILD_ID")

API_BASE = "https://unbelievaboat.com/api/v1"


def unb_headers():
    return {
        "Authorization": UNB_TOKEN,
        "Content-Type": "application/json",
    }


@app.get("/")
def home():
    return "Tournament Bot API is online"


@app.get("/tags/<user_id>")
def get_tags(user_id):
    if not UNB_TOKEN or not GUILD_ID:
        return jsonify({
            "error": "UNB_TOKEN or UNB_GUILD_ID is not configured"
        }), 500

    # Получаем предметы магазина с названием [TAG]
    items_response = requests.get(
        f"{API_BASE}/guilds/{GUILD_ID}/items",
        headers=unb_headers(),
        params={
            "query": "[TAG]",
            "limit": 100
        },
        timeout=15
    )

    if items_response.status_code != 200:
        return jsonify({
            "error": "Failed to get store items",
            "status": items_response.status_code
        }), 502

    items_data = items_response.json()

    if isinstance(items_data, dict):
        items = items_data.get("items", [])
    else:
        items = items_data

    result = []

    for item in items:
        name = str(item.get("name", ""))

        if not name.startswith("[TAG]"):
            continue

        item_id = item.get("id")

        if not item_id:
            continue

        # Проверяем наличие предмета у пользователя
        inventory_response = requests.get(
            f"{API_BASE}/guilds/{GUILD_ID}/users/{user_id}/inventory/{item_id}",
            headers=unb_headers(),
            timeout=15
        )

        owned = inventory_response.status_code == 200

        if owned:
            tag_name = name[len("[TAG]"):].strip()

            result.append({
                "name": tag_name,
                "item_id": str(item_id),
                "owned": True
            })

    return jsonify({
        "user_id": str(user_id),
        "tags": result
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
