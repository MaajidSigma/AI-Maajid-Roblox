import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

GROQ_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# Kata kunci model yang diabaikan (bukan LLM teks biasa / butuh lisensi khusus)
EXCLUDED_KEYWORDS = ["whisper", "guard", "canopylabs", "vision", "arabic", "safetensors"]

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

    try:
        # Ambil seluruh daftar model aktif dari Groq
        models_data = client.models.list()
        
        # Filter hanya model teks biasa
        candidate_models = []
        for m in models_data.data:
            model_id = m.id.lower()
            if not any(keyword in model_id for keyword in EXCLUDED_KEYWORDS):
                candidate_models.append(m.id)

        # Prioritaskan model populer (llama/gemma/mixtral)
        candidate_models.sort(
            key=lambda name: 0 if ("llama" in name.lower() or "gemma" in name.lower() or "mixtral" in name.lower()) else 1
        )

        if not candidate_models:
            return jsonify({"reply": "Tidak ada model teks standar yang ditemukan di Groq."}), 500

        last_error = None

        # Coba kirim request ke setiap model satu per satu sampai ada yang berhasil
        for model_name in candidate_models:
            try:
                print(f"[MEMCOBA MODEL]: {model_name}")
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
                print(f"[SUKSES BERHASIL DENGAN MODEL]: {model_name}")
                return jsonify({"reply": reply})
            except Exception as e:
                print(f"[GAGAL DENGAN MODEL {model_name}]: {e}")
                last_error = e
                continue

        return jsonify({"reply": f"Semua model gagal dikontak. Error: {str(last_error)}"}), 500

    except Exception as e:
        print(f"[ERROR GROQ SYSTEM]: {e}")
        return jsonify({"reply": f"Terjadi error sistem: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
