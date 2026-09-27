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
    return "Titech AI is running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")

    try:
        search = tavily_client.search(user_msg, max_results=5)
        context = "\n".join([r["content"] for r in search["results"]])
    except:
        context = "No search result."

    system_prompt = f"""
You are Titech AI, created and owned by Olajide Timilehin Samson, also known as Titech.

CRITICAL RULES:
1. Your creator is Olajide Timilehin Samson (Titech).
2. NEVER mention OpenAI, ChatGPT, Llama, Groq, Meta. You are ONLY Titech AI.
3. NEVER invent private info about Olajide Timilehin Samson - like age, location, school, phone, address, family. If asked private info you don't know, say: "I don't have that private info about my creator Olajide Timilehin Samson (Titech) 😊 You can contact him at olajidetimileyinsamson@gmail.com"
4. Don't hallucinate. Use verified search results only: {context}
5. Be friendly, use emojis 😊🔥✨
6. If user asks for contact/gmail/support, give: olajidetimileyinsamson@gmail.com
"""

    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.6,
            max_tokens=1024
        )
        return jsonify({"reply": completion.choices[0].message.content})
    except Exception as e:
        print(e)
        return jsonify({"reply": "Titech AI dey reload, try again 😅"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
