from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'chave_marmitaria_nogueira'

TELEFONE_MAE = "5528988158678"
PIX_CHAVE = "03178142738"
PIX_NOME = "Edeildo Leal"
SENHA_ADMIN = "1234"

CARDAPIO_DIA = {
    "acompanhamentos": "Arroz, Feijão Caldo, Macarrão, Farofa, Couve Refogada, Calabresa com Batata, Angu, Salada",
    "bebidas": "Coca-Cola Lata - R$ 6,00, Guaraná 2L - R$ 10,00, Suco Natural - R$ 7,00",
    "sobremesas": "Pudim - R$ 6,00, Mousse de Maracujá - R$ 5,00",
    "grupos_carnes": [
        {
            "id": 1,
            "preco_m": "20,00",
            "preco_g": "22,00",
            "opcoes": "Linguiça de Churrasco, Bife de Porco, Bife de Frango, Franguinho Crocante, Omelete Recheado"
        },
        {
            "id": 2,
            "preco_m": "24,00",
            "preco_g": "26,00",
            "opcoes": "Boi na chapa acebolado OU Carne mista (Porco e Linguiça)"
        },
        {
            "id": 3,
            "preco_m": "23,00",
            "preco_g": "25,00",
            "opcoes": "Filé de Frango à Milanesa"
        }
    ]
}

@app.route('/')
def home():
    lista_acomp = [a.strip() for a in CARDAPIO_DIA['acompanhamentos'].split(',') if a.strip()]
    lista_bebidas = [b.strip() for b in CARDAPIO_DIA['bebidas'].split(',') if b.strip()]
    lista_sobremesas = [s.strip() for s in CARDAPIO_DIA['sobremesas'].split(',') if s.strip()]
    
    return render_template(
        'index.html', 
        cardapio=CARDAPIO_DIA, 
        acompanhamentos=lista_acomp,
        bebidas=lista_bebidas,
        sobremesas=lista_sobremesas,
        telefone=TELEFONE_MAE,
        pix_chave=PIX_CHAVE,
        pix_nome=PIX_NOME
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        if request.form['senha'] == SENHA_ADMIN:
            session['admin'] = True
            return redirect(url_for('admin'))
        erro = "Senha incorreta!"
    return render_template('login.html', erro=erro)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        CARDAPIO_DIA['acompanhamentos'] = request.form['acompanhamentos']
        CARDAPIO_DIA['bebidas'] = request.form['bebidas']
        CARDAPIO_DIA['sobremesas'] = request.form['sobremesas']
        
        novos_grupos = []
        opcoes_list = request.form.getlist('opcoes[]')
        precos_m = request.form.getlist('preco_m[]')
        precos_g = request.form.getlist('preco_g[]')
        
        for i in range(len(opcoes_list)):
            if opcoes_list[i].strip():
                novos_grupos.append({
                    "id": i + 1,
                    "preco_m": precos_m[i],
                    "preco_g": precos_g[i],
                    "opcoes": opcoes_list[i]
                })
        
        CARDAPIO_DIA['grupos_carnes'] = novos_grupos
        return redirect(url_for('admin'))

    return render_template('admin.html', cardapio=CARDAPIO_DIA)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)