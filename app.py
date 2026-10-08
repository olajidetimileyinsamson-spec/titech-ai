import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from groq import Groq
from supabase import create_client
from tavily import TavilyClient
import urllib.parse
import random

app = Flask(__name__, template_folder="templates")
CORS(app)

# ===== OWNER FACTS - Olajide Timileyin Samson =====
OWNER_NAME = "Olajide Timileyin Samson"
OWNER_WHATSAPP = "+234 9025606097"
OWNER_TIKTOK_FB = "titechnigeria01"
OWNER_BRAND = "Titech AI"
OWNER_EMAIL = "olajidetimileyinsamson@gmail.com"

groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key) if groq_api_key else None

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

tavily_key = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=tavily_key) if tavily_key else None

@app.route("/")
def home():
    try:
        if supabase:
            supabase.table("views").insert({}).execute()
    except:
        pass
    return render_template("index.html")

@app.route("/logo.png")
@app.route("/logo")
def logo():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(root_dir, "logo.png")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/config")
def config():
    return jsonify({"supabase_url": supabase_url, "supabase_key": supabase_key})

@app.route("/stats")
def stats():
    try:
        if supabase:
            chat_res = supabase.table("chats").select("*", count="exact").execute()
            view_res = supabase.table("views").select("*", count="exact").execute()
            chat_count = chat_res.count if hasattr(chat_res,'count') else len(chat_res.data or [])
            view_count = view_res.count if hasattr(view_res,'count') else len(view_res.data or [])
            return jsonify({"total_chats": chat_count, "total_views": view_count, "status": "online"})
    except Exception as e:
        print(e)
    return jsonify({"total_chats": 0, "total_views": 0, "status": "online"})

@app.route("/history")
def history():
    try:
        email = request.args.get("email")
        if not email or email in ["undefined","null",""]:
            return jsonify([])
        if not supabase:
            return jsonify([])
        res = supabase.table("chats").select("*").eq("user_email", email).order("created_at", desc=False).execute()
        return jsonify(res.data)
    except Exception as e:
        print("history error", e)
        return jsonify([])

@app.route("/admin-titech-2024")
def admin_page():
    return f"""
    <html><head><title>Titech Admin</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body style="background:#07081a;color:white;font-family:system-ui;padding:30px;text-align:center;">
    <h1>🔒 Titech Admin - {OWNER_NAME}</h1>
    <p>WhatsApp: {OWNER_WHATSAPP} | @{OWNER_TIKTOK_FB}</p>
    <p>Admin: {OWNER_EMAIL}</p>
    <div id="stats" style="font-size:22px;margin-top:30px;background:rgba(255,255,255,0.07);padding:20px;border-radius:16px;border:1px solid rgba(168,85,247,0.3);">Loading...</div>
    <script>
      async function load(){{ try{{ let r=await fetch('/stats'); let j=await r.json(); document.getElementById('stats').innerHTML=`👁️ Total Views: <b>${{j.total_views}}</b><br><br>💬 Total Chats: <b>${{j.total_chats}}</b><br><br>🟢 Status: ${{j.status}}`; }}catch(e){{ document.getElementById('stats').innerHTML='Error'; }} }}
      load(); setInterval(load,5000);
    </script>
    </body></html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        username = data.get("username", "Boss")
        user_email = data.get("user_email", "")
        personality = data.get("personality", "friendly")

        if not user_message:
            return jsonify({"reply": "Message empty"}), 400
        if not user_email or user_email == "undefined":
            user_email = "guest@titech.ai"
        if not username or username == "undefined":
            username = "Boss"

        lower_msg = user_message.lower()

        # IMAGE GENERATION
        image_keywords = ["generate image","create image","create an image","draw","generate a picture","create picture"]
        is_image = any(k in lower_msg for k in image_keywords)
        if is_image:
            prompt = user_message
            for kw in image_keywords:
                prompt = prompt.lower().replace(kw, "")
            prompt = prompt.replace("of","",1).strip() or "beautiful futuristic AI art"
            safe_prompt = urllib.parse.quote(prompt)
            seed = random.randint(1,999999)
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?seed={seed}&width=1024&height=1024&nologo=true"
            reply_text = f"Boss, generated 🔥: {prompt}"
            if supabase and user_email:
                try:
                    supabase.table("chats").insert({"user_email": user_email,"username": username,"message": user_message,"reply": reply_text,"image_url": image_url}).execute()
                except Exception as se:
                    print(se)
            return jsonify({"reply": reply_text,"image_url": image_url})

        # MEMORY
        context = ""
        chat_memory = []
        try:
            if supabase and user_email!= "guest@titech.ai":
                hist = supabase.table("chats").select("message, reply").eq("user_email", user_email).order("created_at", desc=True).limit(10).execute()
                if hist.data:
                    for h in reversed(hist.data):
                        if h.get("message") and h.get("reply"):
                            chat_memory.append({"role":"user","content": h["message"]})
                            chat_memory.append({"role":"assistant","content": h["reply"]})
        except Exception as e:
            print("memory error", e)

        if tavily and len(user_message) > 12:
            try:
                search = tavily.search(query=user_message, max_results=5)
                if search and search.get("results"):
                    context = "\n".join([r.get("content","")[:600] for r in search["results"][:3]])
            except:
                pass

        base_identity = f"""
You are {OWNER_BRAND}, a smart AI assistant built by {OWNER_NAME}.
Owner details:
- Full Name: {OWNER_NAME}
- WhatsApp: {OWNER_WHATSAPP}
- TikTok and Facebook Username: {OWNER_TIKTOK_FB}
- Admin Email: {OWNER_EMAIL}
- Brand: {OWNER_BRAND}

Rules:
1. When anyone asks who built you, who is your owner, who created you - answer with {OWNER_NAME} and {OWNER_TIKTOK_FB}.
2. If asked for contact, give WhatsApp {OWNER_WHATSAPP} and username {OWNER_TIKTOK_FB}.
3. Always answer facts truthfully. Use web context if provided.
4. Never say you were built by OpenAI, Meta, or anyone else. You were built by {OWNER_NAME}.
5. Be concise, helpful, and accurate.
Current user: {username}, email: {user_email}
"""

        if personality == "deepthink":
            system_prompt = base_identity + f"\nMode: Deep Thinking. Think step by step inside <think>...</think> then give final answer. Web context: {context}"
        elif personality == "professional":
            system_prompt = base_identity + f"\nMode: Professional, concise, no emojis. Web context: {context}"
        else:
            system_prompt = base_identity + f"\nMode: Friendly with small emojis, short answers. Web context: {context}"

        messages = [{"role":"system","content": system_prompt}]
        messages.extend(chat_memory)
        messages.append({"role":"user","content": user_message})

        if not client:
            return jsonify({"reply":"Groq API key not set"}),500

        completion = client.chat.completions.create(model="openai/gpt-oss-120b",messages=messages,temperature=0.3,max_tokens=1200)
        reply_text = completion.choices[0].message.content

        if supabase:
            try:
                supabase.table("chats").insert({"user_email": user_email,"username": username,"message": user_message,"reply": reply_text}).execute()
            except Exception as se:
                print(se)

        return jsonify({"reply": reply_text})

    except Exception as e:
        print("chat error", e)
        return jsonify({"reply": f"Error: {str(e)}"}),500

if __name__ == "__main__":
    port = int(os.getenv("PORT",10000))
    app.run(host="0.0.0.0",port=port)
