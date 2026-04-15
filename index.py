from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'purochancho2025'
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')

# Base de datos simple en JSON (sin necesitar SQL)
DB_FILE = 'data/clientes.json'

def load_db():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump([], f)
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── PÁGINAS ──────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('home.html')

# ── API: GUARDAR CLIENTE ─────────────────────────────────────
@app.route('/api/cliente', methods=['POST'])
def guardar_cliente():
    datos = request.get_json()
    clientes = load_db()
    nuevo = {
        'id': len(clientes) + 1,
        'nombre':   datos.get('nombre', ''),
        'telefono': datos.get('telefono', ''),
        'sector':   datos.get('sector', ''),
        'producto': datos.get('producto', ''),
        'nota':     datos.get('nota', ''),
        'fecha':    datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    clientes.append(nuevo)
    save_db(clientes)
    return jsonify({'ok': True, 'id': nuevo['id']})

# ── API: OBTENER CLIENTES (admin) ────────────────────────────
@app.route('/api/clientes', methods=['GET'])
def obtener_clientes():
    clientes = load_db()
    return jsonify(clientes)

# ── API: LOGIN ADMIN ─────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login_admin():
    datos = request.get_json() or {}
    password = datos.get('password', '')
    return jsonify({'success': bool(ADMIN_PASSWORD and password == ADMIN_PASSWORD)})

# ── API: GUARDAR PRECIOS (admin) ─────────────────────────────
@app.route('/api/precios', methods=['POST'])
def guardar_precios():
    datos = request.get_json()
    with open('data/precios.json', 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    return jsonify({'ok': True})

# ── API: OBTENER PRECIOS ─────────────────────────────────────
@app.route('/api/precios', methods=['GET'])
def obtener_precios():
    try:
        with open('data/precios.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        # Precios por defecto
        return jsonify({
            'lechon': {'min': 70,   'max': 110},
            'pie':    {'min': 0.95, 'max': 1.20},
            'cortes': {
                'pierna':   {'min': 2.60, 'max': 2.90},
                'lomo':     {'min': 3.20, 'max': 3.80},
                'costilla': {'min': 2.80, 'max': 3.40},
                'panceta':  {'min': 2.20, 'max': 2.80},
                'paleta':   {'min': 2.30, 'max': 2.70},
                'cabeza':   {'min': 1.50, 'max': 2.00},
            }
        })

if __name__ == '__main__':
    app.run(debug=True)
