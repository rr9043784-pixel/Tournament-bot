import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

UNB_TOKEN = os.environ.get("UNB_TOKEN")
GUILD_ID = os.environ.get("UNB_GUILD_ID")

API_BASE = "https://unbelievaboat.com/api/v1"


def unb_headers():
    return {
        "Authorization": UNB_TOKEN or "",
        "Content-Type": "application/json",
    }


@app.route("/", methods=["GET"])
def home():
    return "Tournament Bot API is online", 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/tags/<user_id>", methods=["GET"])
def get_tags(user_id):
    if not UNB_TOKEN or not GUILD_ID:
        return jsonify({
            "error": "UNB_TOKEN or UNB_GUILD_ID is not configured"
        }), 500

    try:
        response = requests.get(
            f"{API_BASE}/guilds/{GUILD_ID}/items",
            headers=unb_headers(),
            params={"query": "[TAG]", "limit": 100},
            timeout=15
        )

        if response.status_code != 200:
            return jsonify({
                "error": "Failed to get store items",
                "status": response.status_code
            }), 502

        data = response.json()

        if isinstance(data, dict):
            items = data.get("items", [])
        else:
            items = data

        result = []

        for item in items:
            name = str(item.get("name", ""))

            if not name.startswith("[TAG]"):
                continue

            item_id = item.get("id")

            if not item_id:
                continue

            inventory = requests.get(
                f"{API_BASE}/guilds/{GUILD_ID}/users/{user_id}/inventory/{item_id}",
                headers=unb_headers(),
                timeout=15
            )

            if inventory.status_code == 200:
                result.append({
                    "name": name[len("[TAG]"):].strip(),
                    "item_id": str(item_id),
                    "owned": True
                })

        return jsonify({
            "user_id": str(user_id),
            "tags": result
        })

    except requests.RequestException as e:
        return jsonify({
            "error": "UnbelievaBoat API request failed",
            "details": str(e)
        }), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))

    print(f"Starting Tournament Bot API on port {port}", flush=True)

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
        )
