from flask import Flask, request, jsonify, render_template_string
import requests, os, base64

app = Flask(__name__)

# === PUT YOUR LOGO IMAGE HERE AS BASE64 (I will add it for you after you send it) ===
# For now using a beautiful AI logo style
LOGO_SVG = """<svg width="40" height="40" viewBox="0 0 40 40"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#a855f7"/><stop offset="100%" stop-color="#6366f1"/></linearGradient></defs><rect width="40" height="40" rx="12" fill="url(#g)"/><text x="20" y="26" font-family="Arial" font-size="20" font-weight="bold" fill="white" text-anchor="middle">T</text></svg>"""

HTML_PAGE = """
<!DOCTYPE html>
<html><head><title>Titech AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:system-ui,sans-serif;background:#0a0a0a;color:white;margin:0;display:flex;flex-direction:column;height:100vh}
.header{padding:14px 18px;border-bottom:1px solid #222;display:flex;align-items:center;gap:12px;background:#0a0a0a;position:sticky;top:0}
.logo-img{width:38px;height:38px;border-radius:10px;object-fit:cover}
.chat{flex:1;overflow-y:auto;padding:20px;padding-bottom:80px}
.msg{margin:12px 0;padding:14px 16px;border-radius:18px;max-width:85%;line-height:1.5;animation:fade.2s}
@keyframes fade{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
.user{background:#a855f7;margin-left:auto;border-bottom-right-radius:4px}
.bot{background:#1e1e1e;border:1px solid #2a2a2a;border-bottom-left-radius:4px}
.input-area{padding:12px 15px;border-top:1px solid #222;display:flex;gap:10px;position:fixed;bottom:0;left:0;right:0;background:#0a0a0a}
input{flex:1;padding:13px 18px;border-radius:28px;border:1px solid #333;background:#151515;color:white;outline:none;font-size:15px}
button{padding:13px 22px;background:linear-gradient(135deg,#a855f7,#6366f1);color:white;border:none;border-radius:28px;cursor:pointer;font-weight:600}
.bot b{color:#c084fc}
</style></head>
<body>
<div class="header">
<img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCI+CiAgICA8ZGVmcz4KICAgICAgICA8bGluZWFyR3JhZGllbnQgaWQ9ImciIHgxPSIwJSIgeTE9IjAlIiB4Mj0iMTAwJSIgeTI9IjEwMCUiPgogICAgICAgICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjYTg1NWY3Ii8+CiAgICAgICAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzYzNjZmMSIvPgogICAgICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgICA8L2RlZnM+CiAgICA8cmVjdCB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHJ4PSIxMiIgZmlsbD0idXJsKCNnKSIvPgogICAgPHRleHQgeD0iMjAiIHk9IjI2IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjAiIGZvbnQtd2VpZ2h0PSJib2xkIiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSI+VDwvdGV4dD4KPC9zdmc+" class="logo-img">
<div><b style="font-size:16px">Titech AI</b><div style="font-size:11px;color:#888;letter-spacing:.5px">By Timileyin Samson • Always friendly</div></div>
</div>
<div class="chat" id="chat">
<div class="msg bot">Hey there! 👋 I'm <b>Titech AI</b> by Timileyin Samson.<br><br>Ask me anything - I can explain topics, write, code, and help you create. How can I help today?</div>
</div>
<div class="input-area">
<input id="q" placeholder="Ask anything..." autocomplete="off" onkeypress="if(event.key==='Enter')ask()">
<button onclick="ask()">Send</button>
</div>
<script>
async function ask(){
 let q=document.getElementById('q').value.trim();
 if(!q)return;
 let chat=document.getElementById('chat');
 chat.innerHTML+='<div class="msg user">'+q.replace(/</g,'&lt;')+'</div>';
 document.getElementById('q').value='';
 let tempId='temp-'+Date.now();
 chat.innerHTML+='<div class="msg bot" id="'+tempId+'">Typing...</div>';
 chat.scrollTop=chat.scrollHeight;
 try{
  let res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
  let data=await res.json();
  document.getElementById(tempId).innerHTML=data.answer.replace(/\\n/g,'<br>').replace(/</g,'&lt;').replace(/&lt;br&gt;/g,'<br>').replace(/\\*\\*(.*?)\\*\\*/g,'<b>$1</b>');
 }catch(e){
  document.getElementById(tempId).innerHTML='Oops, my internet blinked. Try again!';
 }
 chat.scrollTop=chat.scrollHeight;
}
</script></body></html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/ask', methods=['POST'])
def ask_ai():
    user_q = request.json.get('question','').strip()
    low = user_q.lower()

    # FRIENDLY GREETINGS LIKE META AI / CHATGPT
    if low in ['hi', 'hello', 'hey', 'hi there', 'helo', 'hii']:
        return jsonify({'answer': "Hey! 👋 I'm Titech AI, built by Timileyin Samson.\n\nI'm here to help - you can ask me to explain anything, write something, code, or brainstorm ideas. What are we doing today?"})
    if 'how are you' in low:
        return jsonify({'answer': "I'm great, thanks for asking! 😊 Ready to help you. What would you like to know or create today?"})
    if 'who are you' in low or 'who developed you' in low or 'who created you' in low or 'who built you' in low or 'who is your founder' in low:
        return jsonify({'answer': "I'm Titech AI - a friendly AI assistant developed by **Timileyin Samson**, founder of Titech AI in Lagos. I was built to help Africans and the world learn, create and build faster."})

    # REAL BRAIN
    try:
        r = requests.post(
            "https://text.pollinations.ai/openai",
            json={
                "model": "openai",
                "messages": [
                    {"role": "system", "content": "You are Titech AI, a very friendly, warm, concise assistant created by Timileyin Samson. Reply like ChatGPT/Meta AI: friendly, helpful, use emojis sparingly, be conversational. Keep answers clear."},
                    {"role": "user", "content": user_q}
                ],
                "temperature": 0.7
            },
            timeout=30
        )
        if r.status_code == 200:
            ans = r.json()['choices'][0]['message']['content']
            if ans and len(ans) > 5:
                return jsonify({'answer': ans})
    except Exception as e:
        print(e)

    return jsonify({'answer': "I'm having a small network hiccup - please tap Send again, I got you!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',10000)))
