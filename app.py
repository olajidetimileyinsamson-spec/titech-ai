import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from groq import Groq
from supabase import create_client
from tavily import TavilyClient

app = Flask(__name__, template_folder='templates')
CORS(app)

# clients - env keys from Render
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key) if groq_api_key else None

# optional - if you dey use am, keep am
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
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("message","") or data.get("content","")
    personality = data.get("personality","friendly")
    username = data.get("username","Boss")
    user_email = data.get("user_email","")

    tones = {
        "friendly": "You are Titech AI, friendly, warm, helpful. Greet with username.",
        "hype": "You are Titech AI, hype, energetic, use emojis, motivational.",
        "professional": "You are Titech AI, professional, concise, formal.",
        "short": "You are Titech AI, short replies only, no long explanation.",
        "teacher": "You are Titech AI, teacher mode, explain step-by-step clearly."
    }
    system_prompt = tones.get(personality, tones["friendly"]) + f" User name is {username}. Email is {user_email}. Timezone Africa/Lagos."

    if not client:
        return jsonify({"reply": "Groq API key not set on server"}), 500

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            temperature=0.3,
            messages=[
                {"role":"system","content": system_prompt},
                {"role":"user","content": msg}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
