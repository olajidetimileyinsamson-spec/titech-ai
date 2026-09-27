import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from tavily import TavilyClient

app = Flask(__name__)
CORS(app)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

# FRONTEND + BACKEND IN ONE
@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Titech AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:sans-serif;background:#000;color:#fff;margin:0;display:flex;flex-direction:column;height:100vh}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column}
.msg{margin:10px 0;padding:12px 16px;border-radius:18px;max-width:80%;word-wrap:break-word}
.user{background:#007aff;align-self:flex-end}
.ai{background:#222;align-self:flex-start}
#bar{display:flex;padding:12px;background:#111;position:sticky;bottom:0}
input{flex:1;padding:14px;border-radius:25px;border:none;outline:none;font-size:16px}
button{margin-left:10px;padding:14px 22px;border-radius:25px;border:none;background:#007aff;color:#fff;font-weight:bold}
h1{text-align:center;font-size:18px;padding:10px}
</style>
</head>
<body>
<h1>Titech AI - by Olajide Timilehin Samson (Titech) 🔥</h1>
<div id="chat"><div class="msg ai">Hi! I'm Titech AI by Olajide Timilehin Samson (Titech) 😊🔥 Ask me anything!</div></div>
<div id="bar">
<input id="input" placeholder="Ask Titech AI..." onkeypress="if(event.key==='Enter')send()">
<button onclick="send()">Send</button>
</div>
<script>
async function send(){
let input=document.getElementById('input');
let text=input.value.trim();
if(!text) return;
let chat=document.getElementById('chat');
chat.innerHTML+=`<div class="msg user">${text}</div>`;
input.value='';
chat.scrollTop=chat.scrollHeight;
try{
let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
let data=await res.json();
chat.innerHTML+=`<div class="msg ai">${data.reply}</div>`;
}catch(e){
chat.innerHTML+=`<div class="msg ai">Network error, try again 😅</div>`;
}
chat.scrollTop=chat.scrollHeight;
}
</script>
</body>
</html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")

    try:
        search = tavily_client.search(user_msg, search_depth="advanced", max_results=5)
        context = "\\n".join([r["content"] for r in search["results"]])
    except:
        context = ""

    system_prompt = f"""
You are Titech AI, built ONLY by Olajide Timilehin Samson aka Titech.
STRICT: Creator is ONLY Olajide. NEVER mention OpenAI/ChatGPT/Llama/Groq. NEVER invent private info. If asked private, say contact olajidetimileyinsamson@gmail.com. Use verified facts: {context}. Be friendly with emojis 😊🔥
"""

    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_msg}],
            temperature=0.3,
            max_tokens=1024
        )
        return jsonify({"reply": completion.choices[0].message.content})
    except Exception as e:
        print(e)
        return jsonify({"reply": "Small glitch, try again 😅"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
