@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("message","") or data.get("content","")
    personality = data.get("personality","friendly")
    username = data.get("username","Boss")
    user_email = data.get("user_email","")

    # personality prompt map
    tones = {
        "friendly": "You are Titech AI, friendly, warm, helpful. Always greet with username.",
        "hype": "You are Titech AI, hype, energetic, use emojis, motivational.",
        "professional": "You are Titech AI, professional, concise, formal.",
        "short": "You are Titech AI, short replies only, no long explanation.",
        "teacher": "You are Titech AI, teacher mode, explain step-by-step clearly."
    }
    system_prompt = tones.get(personality, tones["friendly"]) + f" User name is {username}. User email is {user_email}. Current time zone is Africa/Lagos."

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b", # your 120b model
            temperature=0.3, # your requested temp
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500
