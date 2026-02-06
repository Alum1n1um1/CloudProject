from flask import Flask, render_template, request, redirect
import redis
import os
import json

app = Flask(__name__)

# Connexion Redis via la variable d'environnement de Render
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
r = redis.from_url(redis_url, decode_responses=True)

@app.route('/')
def index():
    # Récupération des 10 derniers éléments de la liste Redis
    raw_history = r.lrange("imc_history", 0, 9)
    history = [json.loads(item) for item in raw_history]
    return render_template('index.html', history=history)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        weight = float(request.form.get('weight'))
        height = float(request.form.get('height'))
        
        if height > 0:
            imc = round(weight / (height ** 2), 2)
            data = json.dumps({"weight": weight, "height": height, "imc": imc})
            # Ajout en tête de liste et limitation à 50 entrées
            r.lpush("imc_history", data)
            r.ltrim("imc_history", 0, 49)
    except:
        pass
    
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
