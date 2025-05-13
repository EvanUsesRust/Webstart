from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "your-username/your-repo-name"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

@app.route("/start", methods=["POST"])
def start_codespace():
    # Step 1: Check if codespace is running
    resp = requests.get("https://api.github.com/user/codespaces", headers=HEADERS)
    codespaces = resp.json().get("codespaces", [])
    
    running = next((c for c in codespaces if c["repository"]["full_name"] == REPO), None)
    
    if running:
        codespace_name = running["name"]
    else:
        # Step 2: Create new codespace
        create_resp = requests.post(
            "https://api.github.com/user/codespaces",
            headers=HEADERS,
            json={"repository": REPO, "location": "WestUs2"}  # adjust location as needed
        )
        if create_resp.status_code >= 400:
            return jsonify({"error": "Failed to create Codespace", "details": create_resp.json()}), 500
        codespace_name = create_resp.json()["name"]

    # Step 3: Run your command in the Codespace
    exec_resp = requests.post(
        f"https://api.github.com/user/codespaces/{codespace_name}/machines/0/exec",
        headers=HEADERS,
        json={
            "command": "PORT=6969 pnpm start"
        }
    )

    return jsonify({"status": "Codespace started and command executed", "details": exec_resp.json()})
