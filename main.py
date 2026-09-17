import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

GROQ_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# Daftar pilihan model dari yang utama sampai cadangan
CANDIDATE_MODELS = [
    "llama-3.2-3b-preview",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
    "llama-3.1-8b-instant"
]

@app.route('/', methods=['GET'])
def home():
    return "Server AI Roblox Berhasil Aktif!"

@app.route('/v1/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({"reply": "Error: GROQ_API_KEY belum dipasang di Render!"}), 500

    data = request.json or {}
    user_message = data.get("message", "")
    system_prompt = data.get(
        "system_instruction", 
        "Kamu adalah NPC santai di game Roblox. Hanya boleh mengobrol ramah dan menyapa. DILARANG menjawab koding, tugas sekolah rumit, atau hal tidak pantas."
    )

    last_error = None

    # Coba satu per satu model sampai ada yang berhasil membalas
    for model_name in CANDIDATE_MODELS:
        try:
            completion = client.chat.completions.create(
                model=model_name,
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
            last_error = e
            print(f"[GAGAL DENGAN MODEL {model_name}]: {e}")
            continue

    return jsonify({"reply": f"Semua model gagal: {str(last_error)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
