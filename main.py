import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

# Mengambil API Key dari Environment Variable Render
GROQ_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

@app.route('/', methods=['GET'])
def home():
    return "Server AI Roblox Berhasil Aktif!"

@app.route('/v1/chat', methods=['POST'])
def chat():
    # Cek apakah API Key sudah terpasang
    if not client:
        return jsonify({"reply": "Error: GROQ_API_KEY belum dipasang di Render!"}), 500

    data = request.json or {}
    user_message = data.get("message", "")
    system_prompt = data.get(
        "system_instruction", 
        "Kamu adalah NPC santai di Roblox. Jawab singkat dan ramah."
    )

    try:
        # Menggunakan model llama-3.1-8b-instant yang cepat dan stabil
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        reply = completion.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        # Mencetak detail error ke tab Logs di Render
        print(f"[ERROR GROQ]: {e}")
        return jsonify({"reply": f"Terjadi error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
