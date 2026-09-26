import os, requests, urllib.parse
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY","").strip()
URL = "https://api.groq.com/openai/v1/chat/completions"

def get_wiki_image(query):
    try:
        low = query.lower()
        # For new products like iPhone, use AI photo - Wiki only gives diagram
        skip_wiki = ["iphone","samsung","galaxy","hilux","benz","tesla","laptop","sneaker","shoe","car","airplane","aeroplane"]
        if any(w in low for w in skip_wiki):
            return None

        s_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&srlimit=1"
        r = requests.get(s_url, timeout=10, headers={"User-Agent":"TitechAI/1.0"}).json()
        if not r.get("query",{}).get("search"):
            return None
        title = r["query"]["search"][0]["title"]

        p_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=1000"
        r2 = requests.get(p_url, timeout=10, headers={"User-Agent":"TitechAI/1.0"}).json()
        pages = r2.get("query",{}).get("pages",{})
        for pid in pages:
