import os
from copy import deepcopy

from flask import Flask, render_template, request, jsonify, make_response
from supabase import create_client, Client

app = Flask(__name__)

# ==========================================================
# SUPABASE
# ==========================================================
# O ideal é colocar a chave no ambiente da hospedagem.
# Se SUPABASE_SERVICE_ROLE_KEY existir, ela será usada para o
# backend poder gravar no banco sem depender de policy de escrita.
#
# A chave publishable/anon fica apenas como fallback.
SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "https://dbxntyryjmwrrelpcqnt.supabase.co"
)

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    "sb_publishable_cvk2Fm5Y3kzAA6r3_9VoHw_teWU5-Sv"
)

SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

CHAVE_USADA = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY

supabase: Client | None = None

try:
    supabase = create_client(SUPABASE_URL, CHAVE_USADA)
    print("Supabase conectado com sucesso.")
    print(
        "Tipo de chave usada:",
        "SERVICE ROLE" if SUPABASE_SERVICE_ROLE_KEY else "PUBLISHABLE/ANON"
    )
except Exception as e:
    print("ERRO AO CONECTAR AO SUPABASE:", repr(e))
    supabase = None


# ==========================================================
# DADOS PADRÃO
# ==========================================================
DADOS_PADRAO = {
    "chave_pix": "03178142738 - Edeildo",
    "whatsapp": "5528988158678",

    "bairros": [
        {"nome": "Centro", "taxa": "3,00"}
    ],

    "especiais": {
        "ativo": True,
        "preco_m": "22,00",
        "preco_g": "25,00",
        "carnes": [
            "Filet Mignon",
            "Picanha na Chapa"
        ],
        "guarnicoes": [
            "Arroz Soltinho",
            "Feijão Tropeiro",
            "Batata Frita",
            "Salada"
        ]
    },

    "casa": {
        "ativo": True,
        "preco_m": "18,00",
        "preco_g": "20,00",
        "carnes": [
            "Bife Acebolado",
            "Frango Grelhado",
            "Linguiça"
        ],
        "guarnicoes": [
            "Arroz",
            "Feijão",
            "Macarrão",
            "Salada"
        ]
    },

    "pratos_casa": [
        {
            "nome": "Filé à Parmegiana",
            "preco_m": "25,00",
            "preco_g": "28,00"
        },
        {
            "nome": "Strogonoff de Frango",
            "preco_m": "20,00",
            "preco_g": "23,00"
        }
    ],

    "bebidas": [
        {
            "nome": "Coca-Cola Lata 350ml",
            "preco": "6,00"
        },
        {
            "nome": "Guaraná 2 Litros",
            "preco": "12,00"
        }
    ],

    "sobremesas": [
        {
            "nome": "Pudim de Leite Condensado",
            "preco": "8,00"
        }
    ]
}


# ==========================================================
# FUNÇÕES DO SUPABASE
# ==========================================================
def carregar_cardapio():
    """
    Busca SEMPRE o cardápio mais recente no Supabase.
    Não usa cache local.
    """
    if supabase is None:
        print("Supabase indisponível. Usando dados padrão.")
        return deepcopy(DADOS_PADRAO)

    try:
        response = (
            supabase
            .table("cardapio")
            .select("dados")
            .eq("id", 1)
            .limit(1)
            .execute()
        )

        if response.data:
            dados = response.data[0].get("dados")

            if isinstance(dados, dict):
                return dados

            print("Registro encontrado, mas o campo 'dados' não é um objeto JSON válido.")

        # Se não existir registro, cria o cardápio padrão.
        salvar_resultado = salvar_cardapio(DADOS_PADRAO)

        if not salvar_resultado["sucesso"]:
            print(
                "Não foi possível criar o cardápio padrão:",
                salvar_resultado["erro"]
            )

        return deepcopy(DADOS_PADRAO)

    except Exception as e:
        print("ERRO AO CARREGAR CARDÁPIO DO SUPABASE:", repr(e))
        return deepcopy(DADOS_PADRAO)


def salvar_cardapio(dados):
    """
    Salva o cardápio inteiro em um único registro:
    id = 1
    dados = JSON completo
    """
    if supabase is None:
        return {
            "sucesso": False,
            "erro": "Supabase não está conectado."
        }

    try:
        if not isinstance(dados, dict):
            return {
                "sucesso": False,
                "erro": "Os dados recebidos não estão no formato correto."
            }

        payload = {
            "id": 1,
            "dados": dados
        }

        response = (
            supabase
            .table("cardapio")
            .upsert(payload)
            .execute()
        )

        print("CARDÁPIO SALVO COM SUCESSO.")
        print("Resposta do Supabase:", response.data)

        return {
            "sucesso": True,
            "erro": None
        }

    except Exception as e:
        erro = repr(e)
        print("ERRO REAL AO SALVAR NO SUPABASE:", erro)

        return {
            "sucesso": False,
            "erro": erro
        }


# ==========================================================
# EVITA CACHE DA PÁGINA DO CLIENTE E DO PAINEL
# ==========================================================
@app.after_request
def impedir_cache(response):
    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0, "
        "post-check=0, pre-check=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ==========================================================
# PÁGINA DO CLIENTE
# ==========================================================
@app.route("/")
def index():
    cardapio = carregar_cardapio()
    return render_template("index.html", cardapio=cardapio)


# ==========================================================
# PAINEL DA MAMÃE
# ==========================================================
@app.route("/admin")
def admin():
    cardapio = carregar_cardapio()
    return render_template("admin.html", cardapio=cardapio)


# ==========================================================
# API PARA SALVAR O CARDÁPIO
# ==========================================================
@app.route("/api/salvar-cardapio", methods=["POST"])
def api_salvar_cardapio():
    try:
        dados = request.get_json(silent=True)

        if not dados:
            return jsonify({
                "status": "erro",
                "erro": "Nenhum dado foi recebido pelo servidor."
            }), 400

        resultado = salvar_cardapio(dados)

        if resultado["sucesso"]:
            return jsonify({
                "status": "sucesso",
                "mensagem": "Cardápio salvo no Supabase."
            }), 200

        return jsonify({
            "status": "erro",
            "erro": resultado["erro"]
        }), 500

    except Exception as e:
        print("ERRO NA API /api/salvar-cardapio:", repr(e))

        return jsonify({
            "status": "erro",
            "erro": repr(e)
        }), 500


# ==========================================================
# ROTA DE TESTE
# ==========================================================
@app.route("/api/teste-supabase")
def teste_supabase():
    if supabase is None:
        return jsonify({
            "status": "erro",
            "mensagem": "Não foi possível criar a conexão com o Supabase."
        }), 500

    try:
        response = (
            supabase
            .table("cardapio")
            .select("id")
            .eq("id", 1)
            .limit(1)
            .execute()
        )

        return jsonify({
            "status": "ok",
            "registro_existe": bool(response.data),
            "mensagem": "Conexão com Supabase funcionando."
        })

    except Exception as e:
        print("ERRO NO TESTE DO SUPABASE:", repr(e))

        return jsonify({
            "status": "erro",
            "mensagem": repr(e)
        }), 500


# ==========================================================
# INICIALIZAÇÃO
# ==========================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
