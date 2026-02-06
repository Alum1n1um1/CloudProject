from flask import Flask, render_template, request, redirect
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Connexion PostgreSQL via variable Render
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require", cursor_factory=RealDictCursor)

# Création table si elle n'existe pas
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS imc_history (
            id SERIAL PRIMARY KEY,
            weight FLOAT NOT NULL,
            height FLOAT NOT NULL,
            imc FLOAT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT weight, height, imc
        FROM imc_history
        ORDER BY created_at DESC
        LIMIT 10
    """)

    history = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('index.html', history=history)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        weight = float(request.form.get('weight'))
        height = float(request.form.get('height'))

        if height > 0:
            imc = round(weight / (height ** 2), 2)

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO imc_history (weight, height, imc)
                VALUES (%s, %s, %s)
            """, (weight, height, imc))

            # Limite à 50 entrées
            cur.execute("""
                DELETE FROM imc_history
                WHERE id NOT IN (
                    SELECT id FROM imc_history
                    ORDER BY created_at DESC
                    LIMIT 50
                )
            """)

            conn.commit()
            cur.close()
            conn.close()

    except:
        pass

    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
