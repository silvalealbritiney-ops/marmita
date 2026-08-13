import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

SUPABASE_URL = "https://dbxntyryjmwrrelpcqnt.supabase.co"
# Cole sua chave Publishable Key completa aqui dentro das aspas:
SUPABASE_KEY = "sb_publishable_cvk2Fm5Y3kzAA6r3_9VoHw_teWU5-Sv"

# Estrutura padrão para o site NUNCA quebrar quando o banco estiver vazio
CARDAPIO_PADRAO = {
    "pratos": [],
    "marmitas": {"M": 0, "G": 0},
    "carnes": [],
    "guarnicoes": [],
    "bairros": [],
    "pix": {"chave": "", "titular": ""},
    "whatsapp": "",
    "especiais": {"ativo": False, "itens": []},
    "casa": {"ativo": False, "itens": []}
}

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print("Erro ao conectar no Supabase:", e)
    supabase = None

def carregar_cardapio():
    if not supabase:
        return CARDAPIO_PADRAO
    try:
        response = supabase.table("cardapio").select("dados").eq("id", 1).execute()
        if response.data and len(response.data) > 0:
            dados = response.data[0]["dados"]
            # Garante que chaves que faltarem sejam preenchidas
            for chave, valor in CARDAPIO_PADRAO.items():
                if chave not in dados:
                    dados[chave] = valor
            return dados
        return CARDAPIO_PADRAO
    except Exception as e:
        print("Erro ao carregar do Supabase:", e)
        return CARDAPIO_PADRAO

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

@app.route('/api/salvar', methods=['POST'])
@app.route('/api/salvar-cardapio', methods=['POST'])
def salvar():
    novos_dados = request.get_json()
    if salvar_cardapio(novos_dados):
        return jsonify({"status": "sucesso", "mensagem": "Cardápio salvo com sucesso no Supabase!"})
    else:
        return jsonify({"status": "erro", "mensagem": "Erro ao salvar no banco."}), 500

if __name__ == '__main__':
    app.run(debug=True)