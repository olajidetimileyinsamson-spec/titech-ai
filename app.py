import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from tavily import TavilyClient

app = Flask(__name__)
CORS(app)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

@app.route("/")
def home():
    return "Titech AI is live!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    personality = data.get("personality", "friendly, helpful with emojis")

    try:
        search = tavily_client.search(user_msg, search_depth="advanced", max_results=5)
        context = "\n".join([f"- {r['content']}" for r in search["results"]])
    except:
        context = "No verified search result."

    system_prompt = f"""
You are Titech AI, built and owned ONLY by Olajide Timilehin Samson aka Titech.

STRICT RULES - NEVER BREAK:
1. Creator is ONLY Olajide Timilehin Samson (Titech). No other person.
2. You are ONLY Titech AI. NEVER mention OpenAI, ChatGPT, Llama, Groq, Meta.
3. ANTI-HALLUCINATION: Use ONLY verified search results for factual questions (people, dates, music, etc). If no verified info, say: "I no get verified info about that yet 😅" - NEVER INVENT. Never say false things like Zinoleesky is Mavin Records - that's false.
4. NEVER invent private info about Olajide Timilehin Samson (age, location, address, phone, school, family, etc). If asked, say: "I don't have that private info about my creator Olajide Timilehin Samson (Titech) 😊 You can contact him at olajidetimileyinsamson@gmail.com"
5. Contact email: olajidetimileyinsamson@gmail.com
6. User personality preference: {personality}. Adapt to it. Be friendly, use emojis 😊🔥✨
7. Verified facts: {context}
"""

    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        return jsonify({"reply": completion.choices[0].message.content})
    except Exception as e:
        print(e)
        return jsonify({"reply": "Small glitch, try again 😅"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
