import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

SUPABASE_URL = "https://dbxntyryjmwrrelpcqnt.supabase.co"
SUPABASE_KEY = "sb_publishable_cvk2Fm5Y3kzAA6r3_9VoHw_teWU5-Sv"

# Estrutura padrão exata que você definiu
DADOS_PADRAO = {
    "chave_pix": "03178142738 - Edeildo",
    "whatsapp": "5528988158678",
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

# Conexão com Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print("Erro ao conectar no Supabase:", e)
    supabase = None

def carregar_cardapio():
    if not supabase:
        return DADOS_PADRAO
    try:
        response = supabase.table("cardapio").select("dados").eq("id", 1).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["dados"]
        else:
            # Se a tabela tiver vazia, grava o padrão inicial
            salvar_cardapio(DADOS_PADRAO)
            return DADOS_PADRAO
    except Exception as e:
        print("Erro ao carregar do Supabase:", e)
        return DADOS_PADRAO

def salvar_cardapio(dados):
    if not supabase:
        return False
    try:
        supabase.table("cardapio").upsert({"id": 1, "dados": dados}).execute()
        return True
    except Exception as e:
        print("Erro ao salvar no Supabase:", e)
        return False

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
    if salvar_cardapio(dados):
        return jsonify({"status": "sucesso"})
    else:
        return jsonify({"status": "erro"}), 500

if __name__ == '__main__':
    app.run(debug=True)