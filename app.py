import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from groq import Groq
from supabase import create_client
from tavily import TavilyClient

app = Flask(__name__, template_folder='templates')
CORS(app)

# --- ENV ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
FEEDBACK_EMAIL = "olajidetimileyinsamson@gmail.com"

# Personality you asked - NO FORGET
VALID_PERSONALITIES = ["friendly", "hype", "professional", "short", "teacher"]

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
tavily = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/logo.png")
def logo():
    return send_from_directory('.', 'logo.png')

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "model": "openai/gpt-oss-120b",
        "groq": bool(groq_client),
        "supabase": bool(supabase),
        "tavily": bool(tavily)
    })

@app.route("/chat", methods=["POST"])
def chat_api():
    data = request.get_json()
    messages = data.get("messages")
    personality = data.get("personality", "friendly").lower()
    username = data.get("username", "Boss")
    user_email = data.get("user_email", "")

    # Validate personality
    if personality not in VALID_PERSONALITIES:
        personality = "friendly"

    if not messages:
        single = data.get("message","").strip()
        if not single:
            return jsonify({"reply": "Talk something na 😅"})
        messages = [{"role": "user", "content": single}]

    last_msg = messages[-1]["content"] if messages else ""

    # Greeting save credit
    if last_msg.lower().strip() in ["hey","hi","hello","yo","hii","helo","sup","hey!","hi!"]:
        return jsonify({"reply": f"Yo {username}! I be Titech AI 👋 created by Olajide Timileyin Samson. How I fit help you today?"})

    if not groq_client:
        return jsonify({"reply": "Groq key never set"}), 500

    # Tavily search
    search_context = ""
    if tavily and any(w in last_msg.lower() for w in ["who is","what is","news","latest","current","today","price","2026"]):
        try:
            res = tavily.search(query=last_msg, max_results=3)
            search_context = "\nWEB SEARCH:\n" + "\n".join([r["content"][:500] for r in res.get("results",[])])
        except:
            pass

    # SYSTEM PROMPT WITH ALL RULES
    system_prompt = f"""
You are Titech AI (Titech-120b) 🚀, built by Olajide Timileyin Samson.
Contact: {FEEDBACK_EMAIL} - clickable gmail for feedback.
User info: Username={username}, Email={user_email}
Personality: {personality}
- friendly: warm, small pidgin
- hype: energetic, GenZ
- professional: formal, CEO style
- short: ultra concise 1-2 lines
- teacher: explain step-by-step

RULES:
- NEVER say Meta AI, ChatGPT, Llama, Groq. You are Titech AI.
- Who built you: Olajide Timileyin Samson ({FEEDBACK_EMAIL})
- Model: Titech-120b (titech-ai-120b)
- Always remember username {username} and greet with it.
- Free Tier 💎 badge is shown under Titech AI logo - you are free tier.
- Be concise and explain in details when user ask,use emojis sometimes.
- You have memory and can remember chats
- Web search facts 
- {search_context}
"""

    final_messages = [{"role": "system", "content": system_prompt}] + [m for m in messages if m["role"]!="system"]

    try:
        comp = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=final_messages,
            temperature=0.3, # YOU ASKED 0.3
            max_tokens=1500
        )
        reply = comp.choices[0].message.content

        if supabase:
            try:
                supabase.table("chats").insert({
                    "user_msg": last_msg,
                    "ai_reply": reply,
                    "personality": personality,
                    "username": username,
                    "user_email": user_email
                }).execute()
            except:
                pass

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {e}"}), 500

@app.route("/generate-image", methods=["POST"])
def gen_image():
    prompt = request.json.get("prompt","").strip()
    if not prompt:
        return jsonify({"error":"No prompt"}), 400
    try:
        import fal_client
        result = fal_client.subscribe("fal-ai/flux/schnell", {"prompt": prompt})
        return jsonify({"image_url": result["images"][0]["url"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
