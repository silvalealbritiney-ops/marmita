import json
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DATA_FILE = 'cardapio.json'

# Cardápio inicial padrão
def carregar_cardapio():
    if not os.path.exists(DATA_FILE):
        dados_padrao = {
            "chave_pix": "03178142738 - Edeildo",
            "whatsapp": "+55 28 98815-8678",
            "especiais": {
                "ativo": True,
                "preco_m": "22,00",
                "preco_g": "25,00",
                "carnes": ["Filet Mignon", "Picanha na Chapa"],
                "guarnicoes": ["Arroz Soltinho", "Feijão Tropeiro", "Batata Frita", "Salada"]
            },
            "casa": {
                "ativo": True,
                "preco_m": "18,00",
                "preco_g": "20,00",
                "carnes": ["Bife Acebolado", "Frango Grelhado", "Linguiça"],
                "guarnicoes": ["Arroz", "Feijão", "Macarrão", "Salada"]
            },
            "pratos_casa": [
                {"nome": "Filé à Parmegiana", "preco_m": "25,00", "preco_g": "28,00"},
                {"nome": "Strogonoff de Frango", "preco_m": "20,00", "preco_g": "23,00"}
            ],
            "bebidas": [
                {"nome": "Coca-Cola Lata 350ml", "preco": "6,00"},
                {"nome": "Guaraná 2 Litros", "preco": "12,00"}
            ],
            "sobremesas": [
                {"nome": "Pudim de Leite Condensado", "preco": "8,00"}
            ]
        }
        salvar_cardapio(dados_padrao)
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

@app.route('/admin')
def admin():
    cardapio = carregar_cardapio()
    return render_template('admin.html', cardapio=cardapio)

@app.route('/api/salvar-cardapio', methods=['POST'])
def api_salvar_cardapio():
    dados = request.json
    salvar_cardapio(dados)
    return jsonify({"status": "sucesso"})

if __name__ == '__main__':
    app.run(debug=True)