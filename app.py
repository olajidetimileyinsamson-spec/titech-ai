from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

# --- HTML WITH CHAT ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Titech AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:#000; color:#fff; font-family:Arial; height:100vh; display:flex; flex-direction:column; }
        header { display:flex; align-items:center; gap:12px; padding:12px 20px; border-bottom:2px solid #00d4ff; background:#0a0a0a; }
        header img { width:45px; height:45px; border-radius:8px; border:1px solid #00d4ff; }
        header h1 { color:#00d4ff; font-size:22px; letter-spacing:1px; }
        .chat-container { flex:1; overflow-y:auto; padding:20px; display:flex; flex-direction:column; gap:12px; }
        .msg { max-width:85%; padding:12px 15px; border-radius:15px; line-height:1.4; }
        .user { background:#00d4ff; color:#000; align-self:flex-end; border-bottom-right-radius:3px; }
        .ai { background:#1a1a1a; border:1px solid #333; align-self:flex-start; border-bottom-left-radius:3px; }
        .input-area { display:flex; padding:12px; gap:10px; background:#0a0a0a; border-top:1px solid #222; }
        input { flex:1; padding:14px; border-radius:25px; border:1px solid #333; background:#1a1a1a; color:#fff; outline:none; }
        button { padding:14px 22px; border-radius:25px; border:none; background:#00d4ff; color:#000; font-weight:bold; cursor:pointer; }
        .welcome { text-align:center; margin-top:60px; }
        .welcome h2 { font-size:28px; margin-bottom:10px; }
        .welcome p { color:#888; }
    </style>
</head>
<body>
    <header>
        <img src="/logo.jpg" onerror="this.style.display='none'">
        <h1>TITECH AI</h1>
    </header>
    
    <div class="chat-container" id="chat">
        <div class="welcome" id="welcome">
            <h2>Welcome to Titech AI 🚀</h2>
            <p>Building the future with AI</p>
            <p style="margin-top:20px; color:#00d4ff;">Ask me anything!</p>
        </div>
    </div>

    <div class="input-area">
        <input id="userInput" placeholder="Chat with Titech AI..." onkeypress="if(event.key==='Enter')send()">
        <button onclick="send()">Send</button>
    </div>

<script>
async function send(){
    let input = document.getElementById('userInput');
    let text = input.value.trim();
    if(!text) return;
    
    document.getElementById('welcome')?.remove();
    let chat = document.getElementById('chat');
    
    chat.innerHTML += `<div class="msg user">${text}</div>`;
    input.value = '';
    chat.scrollTop = chat.scrollHeight;
    
    chat.innerHTML += `<div class="msg ai" id="typing">Titech AI is typing...</div>`;
    
    let res = await fetch('/chat', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({message:text})
    });
    let data = await res.json();
    
    document.getElementById('typing').remove();
    chat.innerHTML += `<div class="msg ai">${data.reply}</div>`;
    chat.scrollTop = chat.scrollHeight;
}
</script>
</body>
</html>
"""

def get_ai_reply(user_msg):
    msg = user_msg.lower()
    
    if "who are you" in msg or "what are you" in msg:
        return "I am Titech AI 🚀, built by Titech to help you build the future with AI! Ask me anything - business, coding, school, life!"
    if "titech" in msg:
        return "Titech AI is your Nigerian AI assistant! We dey help businesses and students use AI to make money and work faster 💎"
    if "business" in msg or "money" in msg:
        return "For business, use AI to: 1) Write faster proposals 2) Generate logos & ads 3) Auto-reply customers on WhatsApp. Want me to write a business plan for you?"
    if "logo" in msg or "design" in msg:
        return "I fit help you design logo ideas! Tell me your business name and what you sell, I go give you 3 AI logo prompts wey you fit use for Canva."
    if "code" in msg or "website" in msg:
        return "I sabi code! I built this site with Flask. Tell me wetin you want build - I go give you the code sharp sharp!"
    if "jamb" in msg or "school" in msg:
        return "For school, I fit summarize notes, explain topics for JAMB/WAEC, and write assignments. Which subject you need help?"
    if "hello" in msg or "hi" in msg:
        return "Hello! 👋 Welcome to Titech AI! How I fit help you today?"
    
    # Default smart reply
    return f"You asked: '{user_msg}' - That's a great question! As Titech AI, I dey here to help you solve am. Tell me more about wetin you wan achieve, make I break am down for you in simple steps. 🚀"

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/logo.jpg")
def logo():
    # Serve logo from root
    if os.path.exists("logo.jpg"):
        return app.send_static_file("../logo.jpg") if False else open("logo.jpg","rb").read(), 200, {'Content-Type':'image/jpeg'}
    return "", 404

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data.get("message","")
    reply = get_ai_reply(user_text)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
