import os
from flask import Flask, render_template_string, request, redirect, session, jsonify
from supabase import create_client

app = Flask(__name__)
app.secret_key = "titech-secret-2024"

# Load keys from Render
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TAVILY_KEY = os.getenv("TAVILY_API_KEY")
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===== HTML TEMPLATE WITH LOGIN =====
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TITECH AI</title>
<style>
body{background:#0f0f0f;color:white;font-family:sans-serif;margin:0}
.login-box{max-width:350px;margin:80px auto;background:#1a1a1a;padding:30px;border-radius:15px}
input{width:100%;padding:12px;margin:8px 0;border-radius:8px;border:none;background:#2a2a2a;color:white}
button{width:100%;padding:12px;background:#7c3aed;border:none;border-radius:8px;color:white;font-weight:bold;cursor:pointer}
.chat{max-width:700px;margin:0 auto;padding:20px}
.msg{padding:12px;margin:10px 0;border-radius:10px}
.user{background:#7c3aed;text-align:right}
.ai{background:#222}
#chatbox{height:70vh;overflow-y:auto}
</style>
</head>
<body>
{% if not logged %}
<div class="login-box">
<h2>🔐 TITECH AI Login</h2>
<form method="POST" action="/login">
<input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Password" required>
<button type="submit">Login / Sign Up</button>
</form>
<p style="font-size:12px;color:#888;margin-top:10px">New user? Just enter email & password, we go create account automatically.</p>
</div>
{% else %}
<div class="chat">
<h3>🤖 TITECH AI - Welcome {{user_email}} <a href="/logout" style="color:#888;font-size:12px">Logout</a></h3>
<div id="chatbox"></div>
<div style="display:flex;gap:10px;margin-top:15px">
<input id="q" placeholder="Ask anything..." style="flex:1">
<button onclick="ask()" style="width:80px">Send</button>
</div>
</div>
<script>
async function ask(){
 let q=document.getElementById('q').value;
 if(!q) return;
 let box=document.getElementById('chatbox');
 box.innerHTML+=`<div class='msg user'>${q}</div>`;
 document.getElementById('q').value='';
 let res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q})});
 let data=await res.json();
 box.innerHTML+=`<div class='msg ai'>${data.answer}</div>`;
 box.scrollTop=box.scrollHeight;
}
</script>
{% endif %}
</body>
</html>
"""

@app.route("/")
def home():
    if "user" not in session:
        return render_template_string(HTML, logged=False)
    return render_template_string(HTML, logged=True, user_email=session["user"])

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    try:
        # Try login
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        session["user"] = email
        return redirect("/")
    except:
        try:
            # Try signup if login fails
            res = supabase.auth.sign_up({"email": email, "password": password})
            session["user"] = email
            return redirect("/")
        except Exception as e:
            return f"Login error: {e} <a href='/'>Try again</a>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/ask", methods=["POST"])
def ask():
    q = request.json.get("q","")
    # Here connect your Groq / Tavily logic
    # For now, simple answer
    answer = f"🔥 TITECH AI: You asked '{q}'. Your Supabase login dey work! Now I fit remember you. Connect your AI model here."
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
