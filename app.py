import os
import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Récupération du Cookie
SUNO_COOKIE = os.environ.get("SUNO_COOKIE")

def get_auth_token(cookie):
    """
    Cette fonction cherche le jeton caché (__client) dans le cookie
    pour créer l'en-tête 'Authorization: Bearer ...'
    """
    if not cookie:
        return None
    # On cherche la partie qui commence par __client=eyJ...
    match = re.search(r"__client=(eyJ[^;]+)", cookie)
    if match:
        return match.group(1)
    return None

@app.route('/')
def home():
    return "L'API Suno V2 (Smart Auth) est en ligne ! 🎵"

@app.route('/generate', methods=['POST'])
def generate_music():
    if not SUNO_COOKIE:
        return jsonify({"error": "Erreur Render: Variable SUNO_COOKIE manquante"}), 500

    # 1. Préparation des En-têtes (Headers)
    headers = {
        "Cookie": SUNO_COOKIE,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Origin": "https://suno.com",
        "Referer": "https://suno.com/"
    }

    # 2. Extraction et Ajout du Jeton (C'est souvent ça qui règle l'erreur 401)
    token = get_auth_token(SUNO_COOKIE)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        # Si on ne trouve pas le jeton, on prévient (mais on essaie quand même)
        print("Attention: Jeton __client introuvable dans le cookie")

    # 3. Récupération des données du Bot
    data = request.json
    prompt = data.get('prompt', '')
    is_instrumental = data.get('instrumental', False)

    # URL de génération V3 (plus stable)
    url = "https://studio-api.prod.suno.com/api/generate/v2/"

    payload = {
        "prompt": prompt,
        "mv": "chirp-v3-0",
        "title": "",
        "tags": "",
        "make_instrumental": is_instrumental
    }

    try:
        print(f"Envoi de la commande à Suno: {prompt[:50]}...")
        response = requests.post(url, headers=headers, json=payload)
        
        # Si Suno répond 200 (OK)
        if response.status_code == 200:
            return jsonify(response.json())
        
        # Si Suno répond 401 (Toujours bloqué)
        elif response.status_code == 401:
            print("Erreur 401: Le cookie est probablement expiré ou mal copié.")
            return jsonify({
                "error": "Suno Auth Failed (401)", 
                "details": "Le cookie est invalide ou expiré. Vérifie la variable Render."
            }), 401
            
        else:
            return jsonify({"error": f"Erreur Suno {response.status_code}", "details": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
