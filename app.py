import os
from flask import Flask, Response, send_from_directory
app = Flask(__name__)

@app.route("/")
def home():
    return Response("""
<!DOCTYPE html><html><head><title>Titech AI 🚀</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box;font-family:system-ui}body{margin:0;background:#101014;color:#fff;min-height:100vh;display:flex;flex-direction:column}
#welcome{position:fixed;inset:0;z-index:9999;background:#0e0e10;display:flex;align-items:center;justify-content:center;padding:24px}
.wel-center{width:100%;max-width:360px;display:flex;flex-direction:column;align-items:center;text-align:center}
.wel-logo{width:100px;height:100px;background:#fff;border-radius:22px;display:flex;align-items:center;justify-content:center;margin:0 auto 18px}
.wel-logo img{width:72px;height:72px;object-fit:contain}
.wel-title{font-size:30px;font-weight:800;color:#fff !important;margin:0 0 6px}
.wel-sub{font-size:15px;color:#a1a1aa !important;margin:0 0 26px}
.login-box{width:100%;display:flex;flex-direction:column;gap:12px}
.login-box input{width:100%;padding:15px 16px;border-radius:14px;border:1px solid #2a2a2e;background:#1e1e22;color:#fff;font-size:15px}
.login-box button{width:100%;padding:15px;border-radius:14px;border:none;background:#3b82f6;color:#fff;font-weight:700;font-size:16px}
#topbar{display:flex;justify-content:space-between;padding:12px 16px;background:#18181b;border-bottom:1px solid #27272a}
#chat{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:14px}
#bar{position:sticky;bottom:0;background:#18181b;border-top:1px solid #27272a;padding:10px;display:flex}
#bar input{flex:1;background:#27272a;border:none;color:#fff;padding:14px 18px;border-radius:24px}
#welcome.hide{display:none}
</style></head><body>

<div id=welcome>
 <div class=wel-center>
   <div class=wel-logo><img src="/logo.png"></div>
   <div class=wel-title id=greetTitle>Good Morning</div>
   <div class=wel-sub>Titech AI 🚀</div>
   <div class=login-box>
     <input id=username placeholder="Username (e.g Tosin)">
     <input id=email placeholder="Email">
     <input id=password type=password placeholder="Password">
     <button onclick="enterChat()">Continue</button>
   </div>
 </div>
</div>

<div id=topbar><b>Titech AI 🚀</b></div>
<div id=chat></div>
<div id=bar><input placeholder="Ask Titech AI 🚀..."></div>

<script>
function getGreeting(){const h=new Date().getHours();if(h<12)return"Good Morning";if(h<18)return"Good Afternoon";return"Good Evening"}
document.getElementById('greetTitle').textContent=getGreeting();
function enterChat(){
 const u=document.getElementById('username').value.trim();
 const e=document.getElementById('email').value.trim();
 const p=document.getElementById('password').value.trim();
 if(!u||!e||!p){alert("Fill all fields");return}
 const g=getGreeting();
 document.getElementById('greetTitle').textContent=g+" "+u+" 🚀";
 setTimeout(()=>{document.getElementById('welcome').classList.add('hide')},3000);
}
</script>
</body></html>
""", mimetype="text/html")

@app.route("/logo.png")
def logo(): return send_from_directory(".", "logo.png")
@app.route("/health")
def health(): return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
