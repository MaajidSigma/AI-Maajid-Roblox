import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

GROQ_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

EXCLUDED_KEYWORDS = ["whisper", "guard", "canopylabs", "vision", "arabic", "safetensors"]

@app.route('/', methods=['GET'])
def home():
    return "Server AI Roblox Berhasil Aktif!"

@app.route('/v1/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({"reply": "Error: GROQ_API_KEY belum dipasang!"}), 500

    data = request.json or {}
    user_message = data.get("message", "")
    system_prompt = data.get("system_instruction", "")
    game_context = data.get("game_context", "")
    history = data.get("history", [])

    full_system_prompt = f"{system_prompt}\n\n[SITUASI GAME SAAT INI]:\n{game_context}"

    messages_payload = [{"role": "system", "content": full_system_prompt}]
    
    for msg in history[-6:]:
        messages_payload.append(msg)
        
    messages_payload.append({"role": "user", "content": user_message})

    try:
        models_data = client.models.list()
        candidate_models = [
            m.id for m in models_data.data 
            if not any(k in m.id.lower() for k in EXCLUDED_KEYWORDS)
        ]
        candidate_models.sort(
            key=lambda n: 0 if any(x in n.lower() for x in ["llama", "gemma", "mixtral"]) else 1
        )

        for model_name in candidate_models:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=messages_payload,
                    temperature=0.7,
                    max_tokens=150 # Tetap 150 (tidak dibatasi)
                )
                reply = completion.choices[0].message.content
                return jsonify({"reply": reply})
            except Exception:
                continue

        return jsonify({"reply": "Gagal terhubung ke model AI."}), 500

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
