import os, requests, urllib.parse
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY","").strip()
URL = "https://api.groq.com/openai/v1/chat/completions"

def get_wiki_image(query):
    try:
        low = query.lower()
        skip_wiki = ["iphone","samsung","galaxy","hilux","benz","tesla","laptop","sneaker","car","airplane","aeroplane"]
        if any(w in low for w in skip_wiki):
            return None

        s_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&srlimit=1"
        r = requests.get(s_url, timeout=10, headers={"User-Agent":"TitechAI/1.0"}).json()
        if not r.get("query", {}).get("search"):
            return None
        title = r["query"]["search"][0]["title"]

        p_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=1000"
        r2 = requests.get(p_url, timeout=10, headers={"User-Agent":"TitechAI/1.0"}).json()
        pages = r2.get("query", {}).get("pages", {})
        for pid in pages:
            thumb = pages[pid].get("thumbnail", {}).get("source")
            if thumb:
                if ".svg" in thumb.lower():
                    return None
                return thumb, title
    except Exception:
        return None
    return None

HTML = """
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Titech AI</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;font-family:Inter,system-ui}
body{margin:0;background:#070a14;color:#e8eaff;display:flex;flex-direction:column;height:100vh}
header{padding:12px 16px;display:flex;align-items:center;gap:12px;background:#0d1120;border-bottom:1px solid #1e294d;position:sticky;top:0;z-index:10}
.logo{width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#4f46e5,#06b6d4);display:flex;align-items:center;justify-content:center;font-weight:900;color:white;overflow:hidden}
.logo img{width:100%;height:100%;object-fit:cover}
.brand{font-weight:800;font-size:18px}.brand span{color:#60a5fa}
#chat{flex:1;overflow:auto;padding:16px 16px 120px 16px;max-width:900px;margin:0 auto;width:100%;display:flex;flex-direction:column;gap:12px}
.msg{padding:14px 18px;border-radius:20px;max-width:82%;line-height:1.5;font-size:15px;word-wrap:break
