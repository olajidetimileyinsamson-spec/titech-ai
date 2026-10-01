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
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    personality = data.get("personality", "friendly")
    username = data.get("username", "User")
    user_email = data.get("user_email", "")
    lower_msg = user_message.lower()
    if "generate image" in lower_msg or "create image" in lower_msg or "flux" in lower_msg or lower_msg.startswith("draw "):
        prompt = user_message
        for w in ["generate image of", "generate image", "create image of", "create image", "flux", "draw"]:
            prompt = prompt.lower().replace(w, "")
        prompt = prompt.strip() or "a goat"
        encoded = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?model=flux&width=1024&height=1024&nologo=true&seed={os.urandom(2).hex()}"
        return jsonify({"reply": f"FLUX result for '{prompt}':![image]({image_url})"})
    tones = {"friendly": "You are Titech AI, friendly and helpful.", "hype": "You are Titech AI, hype and energetic with emojis.", "professional": "You are Titech AI, professional and concise.", "short": "You are Titech AI, short replies only.", "teacher": "You are Titech AI, teacher mode, explain clearly step-by-step."}
    system_prompt = tones.get(personality, tones["friendly"]) + f" User name is {username}. Email is {user_email}. Timezone Africa/Nigeria. STRICT IDENTITY: You were built SOLELY by Olajide Timileyin Samson, founder of Titech. You are Titech AI only. NOT OpenAI."
    if not client:
        return jsonify({"reply": "Groq API key not set"}), 500
    try:
        response = client.chat.completions.create(model="openai/gpt-oss-120b", temperature=0.3, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}])
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
