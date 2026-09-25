from flask import Flask, request, jsonify, render_template_string, send_file
import os

app = Flask(__name__)

def get_ai_reply(message):
    msg = message.lower()
    
    if "hello" in msg or "hi" in msg or "hey" in msg:
        return "Hello! 👋 Welcome to Titech AI! How I fit help you today?"
    
    if "who are you" in msg:
        return "I am Titech AI 🚀, built by Titech to help you build the future with AI! Ask me anything - business, coding, school, life!"
    
    if "titech" in msg:
        return "Titech AI is your Nigerian AI assistant! We dey help businesses and students use AI to make money and work faster 💎"
    
    if "develop" in msg or "creator" in msg or "created" in msg or "built" in msg or "owner" in msg or "who made" in msg:
        return "I was developed by Timileyin Samson, the founder of Titech AI! 🚀 He built me to help Nigerians use AI to build the future! One man, one vision!"

    # Default reply
    return f"You asked: '{message}' - That's a great question! As Titech AI, I dey here to help you solve am. Tell me more about wetin you wan achieve, make I break am down for you in simple steps. 🚀"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Titech AI</title>
    <style>
        body { background: #000; color: white; font-family: sans-serif; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
        .header { background: #111; padding: 15px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #333; }
        .header img { width: 35px; height: 35px; border-radius: 50%; }
        .chat-box { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
        .msg { max-width: 80%; padding: 12px 15px; border-radius: 18px; line-height: 1.4; }
        .user { background: #0ab3ff; color: black; align-self: flex-end; border-bottom-right-radius: 4px; }
        .ai { background: #222; align-self: flex-start; border-bottom-left-radius: 4px; }
        .input-area { padding: 10px; background: #111; display: flex; gap: 10px; border-top: 1px solid #333; }
        input { flex: 1; background: #222; border: 1px solid #333; color: white; padding: 12px 15px; border-radius: 25px; outline: none; }
        button { background: #0ab3ff; border: none; padding: 0 20px; border-radius: 25px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <img src="/logo.jpg" onerror="this.style.display='none'">
        <b>Titech AI 🚀</b>
    </div>
    <div class="chat-box" id="chat">
        <div class="msg ai">Hello! I am Titech AI 🚀 built by Timileyin Samson. How I fit help you today?</div>
    </div>
    <div class="input-area">
        <input id="inp" placeholder="Chat with Titech AI..." onkeypress="if(event.key==='Enter')send()">
        <button onclick="send()">Send</button>
    </div>
    <script>
        async function send(){
            const i=document.getElementById('inp');
            const txt=i.value.trim();
            if(!txt)return;
            const chat=document.getElementById('chat');
            chat.innerHTML+=`<div class="msg user">${txt}</div>`;
            i.value='';
            chat.scrollTop=chat.scrollHeight;
            const res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt})});
            const data=await res.json();
            chat.innerHTML+=`<div class="msg ai">${data.reply}</div>`;
            chat.scrollTop=chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    reply = get_ai_reply(user_msg)
    return jsonify({"reply": reply})

@app.route("/logo.jpg")
def logo():
    for name in ["logo.jpg", "logo.JPG", "logo.jpg.JPG", "Logo.jpg", "LOGO.jpg", "logo.jpeg", "logo.png"]:
        if os.path.exists(name):
            return send_file(name)
    return "", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
