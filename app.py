import os, urllib.parse
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from groq import Groq
from supabase import create_client
from tavily import TavilyClient

app = Flask(__name__, template_folder="templates")
CORS(app)

groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key) if groq_api_key else None

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

tavily_key = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=tavily_key) if tavily_key else None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/logo.png")
def logo():
    return send_from_directory(".", "logo.png")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/config")
def config():
    return jsonify({"supabase_url": os.getenv("SUPABASE_URL"), "supabase_key": os.getenv("SUPABASE_KEY")})

@app.route("/history")
def history():
    email = request.args.get("email")
    if not supabase or not email:
        return jsonify([])
    try:
        res = supabase.table("chats").select("*").eq("user_email", email).order("created_at", desc=False).limit(50).execute()
        return jsonify(res.data)
    except Exception as e:
        print(e)
        return jsonify([])

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    personality = data.get("personality", "friendly")
    username = data.get("username", "User")
    user_email = data.get("user_email", "")
    lower_msg = user_message.lower()

        if "generate image" in lower_msg or "create image" in lower_msg or "generate picture" in lower_msg or "create picture" in lower_msg or "flux" in lower_msg or "picture of" in lower_msg or "image of" in lower_msg:
        prompt = user_message
        for w in ["generate image of", "generate image", "create image of", "create image", "generate picture of", "generate picture", "create picture of", "create picture", "picture of", "image of", "flux"]:
            prompt = prompt.lower().replace(w, "")
        prompt = prompt.strip() or "a goat"
        # remove extra words like 'a', 'the'
        prompt = prompt.strip()
        encoded = urllib.parse.quote(prompt)
        import random
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?model=flux&width=1024&height=1024&nologo=true&seed={random.randint(1,999999)}"
        reply_text = f"Here is your **{prompt}** — Boss, generated 🔥"
        if supabase and user_email:
            try:
                supabase.table("chats").insert({"user_email": user_email, "username": user_message, "message": prompt}).execute()
            except:
                pass
        return jsonify({"reply": reply_text, "image_url": image_url})

    tones = {
        "friendly": "You are Titech AI, friendly and helpful.",
        "hype": "You are Titech AI, hype and energetic with emojis.",
        "professional": "You are Titech AI, professional and concise.",
        "short": "You are Titech AI, short replies only.",
        "teacher": "You are Titech AI, teacher mode, explain simply."
    }
    system_prompt = tones.get(personality, tones["friendly"]) + f""" User name is {username}. Email is {user_email}. You are Titech AI created by Olajide Timileyin Samson, Founder of Titech. When user ask for contact, Give olajidetimileyinsamson@gmail.com. You are not openai or chat gpt, Never mention chat gpt or openai, You are Titech AI (titech-ai-120b) developed by Olajide Timileyin Samson (Titech)."""

    if tavily and len(user_message) > 15:
        try:
            search = tavily.search(query=user_message, max_results=3)
            if search.get("results"):
                context = "\n".join([r["content"] for r in search["results"]])
                system_prompt += f"\nUse this web info if relevant:\n{context}"
        except:
            pass

    try:
        if not client:
            return jsonify({"reply": "Groq API key not set"}), 500
        response = client.chat.completions.create(model="openai/gpt-oss-120b", temperature=0.3, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}])
        reply_text = response.choices[0].message.content
        if supabase and user_email:
            try:
                supabase.table("chats").insert({"user_email": user_email, "username": username, "message": user_message, "reply": reply_text, "personality": personality}).execute()
            except Exception as e:
                print("save error", e)
        return jsonify({"reply": reply_text})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
