import json
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

# Arquivo onde o cardápio fica salvo
DATA_FILE = 'cardapio.json'

def carregar_cardapio():
    if not os.path.exists(DATA_FILE):
        dados_padrao = {
            "tamanho_m": "20.00",
            "tamanho_g": "22.00",
            "carnes": [
                "Linguiça de Churrasco",
                "Bife de Porco",
                "Bife de Frango",
                "Franguinho Crocante",
                "Omelete Recheado"
            ]
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados_padrao, f, ensure_ascii=False, indent=4)
        return dados_padrao
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_cardapio(dados):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    cardapio = carregar_cardapio()
    return render_template('index.html', cardapio=cardapio)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/admin')
def admin():
    cardapio = carregar_cardapio()
    return render_template('admin.html', cardapio=cardapio)

@app.route('/api/salvar-cardapio', methods=['POST'])
def api_salvar_cardapio():
    req = request.json
    salvar_cardapio(req)
    return jsonify({"status": "sucesso"})

if __name__ == '__main__':
    app.run(debug=True)