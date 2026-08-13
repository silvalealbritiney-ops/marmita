import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# Configurações do seu Supabase
SUPABASE_URL = "https://dbxntyryjmwrrelpcqnt.supabase.co"
# Cole dentro das aspas abaixo a chave 'Publishable key' (a que começa com sb_publishable_...)
SUPABASE_KEY = "sb_publishable_cvk2Fm5Y3kzAA6r3_9VoHw_teWU5-Sv"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def carregar_cardapio():
    try:
        response = supabase.table("cardapio").select("dados").eq("id", 1).execute()
        if response.data:
            return response.data[0]["dados"]
        else:
            return {}
    except Exception as e:
        print("Erro ao carregar do Supabase:", e)
        return {}

def salvar_cardapio(dados):
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
def salvar():
    novos_dados = request.get_json()
    if salvar_cardapio(novos_dados):
        return jsonify({"status": "sucesso", "mensagem": "Cardápio atualizado com sucesso no Supabase!"})
    else:
        return jsonify({"status": "erro", "mensagem": "Erro ao salvar os dados."}), 500

if __name__ == '__main__':
    app.run(debug=True)