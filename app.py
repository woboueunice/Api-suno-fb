import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# 1. On récupère le cookie depuis les variables de Render (sécurité !)
# Si on ne le trouve pas, le bot ne pourra pas démarrer.
SUNO_COOKIE = os.environ.get("SUNO_COOKIE")

@app.route('/')
def home():
    return "L'API Suno de Joel est en ligne ! 🎵"

@app.route('/generate', methods=['POST'])
def generate_music():
    if not SUNO_COOKIE:
        return jsonify({"error": "Erreur config: Cookie manquant sur Render"}), 500

    # Récupérer les données envoyées par ton bot (le prompt)
    data = request.json
    prompt = data.get('prompt', 'Une musique relaxante')
    is_instrumental = data.get('instrumental', False)

    # L'URL officielle de l'API Suno (celle qu'on a vue dans l'inspecteur)
    url = "https://studio-api.prod.suno.com/api/generate/v2/"

    # Les headers (pour faire croire qu'on est toi)
    headers = {
        "Cookie": SUNO_COOKIE,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }

    # Le corps de la demande
    payload = {
        "prompt": prompt,
        "mv": "chirp-v3-0", # Version du modèle (V3)
        "title": "",
        "tags": "",
        "make_instrumental": is_instrumental
    }

    try:
        # Envoi de la demande à Suno
        response = requests.post(url, headers=headers, json=payload)
        
        # Vérification si Suno a accepté
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Suno a refusé", "details": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Port par défaut pour Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
