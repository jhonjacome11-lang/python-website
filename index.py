from flask import Flask, render_template, request, jsonify, Response
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'purochancho2025')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')

# ── HELPERS JSON ───────────────────────────────────────────────
def _ensure_data():
    os.makedirs('data', exist_ok=True)

def _read(path, default):
    _ensure_data()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def _write(path, data):
    _ensure_data()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── PÁGINA PRINCIPAL ───────────────────────────────────────────────
@app.route('/')
def home():
    return Response(render_template('home.html'), mimetype='text/html')

# ── LOGIN ADMIN ────────────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login_admin():
    d = request.get_json() or {}
    ok = bool(ADMIN_PASSWORD and d.get('password','') == ADMIN_PASSWORD)
    return jsonify({'success': ok})

# ── CLIENTES ──────────────────────────────────────────────────
@app.route('/api/cliente', methods=['POST'])
def guardar_cliente():
    d = request.get_json() or {}
    clientes = _read('data/clientes.json', [])
    nuevo = {
        'id':       len(clientes) + 1,
        'nombre':   d.get('nombre', ''),
        'telefono': d.get('telefono', ''),
        'sector':   d.get('sector', ''),
        'producto': d.get('producto', ''),
        'nota':     d.get('nota', ''),
        'fecha':    datetime.now().strftime('%Y-%m-%d %H:%M'),
    }
    clientes.append(nuevo)
    _write('data/clientes.json', clientes)
    return jsonify({'ok': True, 'id': nuevo['id']})

@app.route('/api/clientes', methods=['GET'])
def obtener_clientes():
    return jsonify(_read('data/clientes.json', []))

@app.route('/api/cliente/<int:cid>', methods=['DELETE'])
def eliminar_cliente(cid):
    clientes = _read('data/clientes.json', [])
    clientes = [c for c in clientes if c.get('id') != cid]
    _write('data/clientes.json', clientes)
    return jsonify({'ok': True})

# ── PRECIOS ───────────────────────────────────────────────────
DEFAULT_PRICES = {
    'lechon':      {'min': 70, 'max': 110},
    'pie':         {'min': 2.5, 'max': 2.5},
    'cuts_status': {
        'pierna':'disponible','lomo':'disponible','costilla':'disponible',
        'panceta':'disponible','paleta':'disponible','cabeza':'disponible',
    },
}

@app.route('/api/precios', methods=['GET'])
def obtener_precios():
    return jsonify(_read('data/precios.json', DEFAULT_PRICES))

@app.route('/api/precios', methods=['POST'])
def guardar_precios():
    _write('data/precios.json', request.get_json() or {})
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(debug=True)
