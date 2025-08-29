from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
TISSUE_SLIDES_DB = os.environ.get("TISSUE_SLIDES_DB")
HEADERS = {"Authorization": f"Bearer {NOTION_API_KEY}",
           "Notion-Version": "2022-06-28",
           "Content-Type": "application/json"}

@app.route("/")
def home():
    return "Serial Numbering Service is Running"

@app.route("/create_slide", methods=["POST"])
def create_slide():
    data = request.json
    session_id = data.get("session_id")

    # 1. Query existing slides for this session
    query_url = f"https://api.notion.com/v1/databases/{TISSUE_SLIDES_DB}/query"
    body = {
        "filter": {
            "property": "Staining Session",
            "relation": {
                "contains": session_id
            }
        }
    }
    r = requests.post(query_url, headers=HEADERS, json=body)
    results = r.json().get("results", [])
    next_serial = len(results) + 1

    # 2. Create new slide page
    create_url = "https://api.notion.com/v1/pages"
    new_page = {
        "parent": {"database_id": TISSUE_SLIDES_DB},
        "properties": {
            "Name": {"title": [{"text": {"content": f"Slide {next_serial}"}}]},
            "Serial Number": {"number": next_serial},
            "Staining Session": {
                "relation": [{"id": session_id}]
            }
        }
    }
    r = requests.post(create_url, headers=HEADERS, json=new_page)

    return jsonify(r.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
