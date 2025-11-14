from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import pickle
import os

app = Flask(__name__)
app.secret_key = "123"

# ---------------------------
# BANCO DE DADOS SIMPLES
# ---------------------------
livros = []
next_id = 1

# ---------------------------
# CARREGAR MODELO SE EXISTIR
# ---------------------------
modelo_carregado = None
modelo_path = "modelo_preco.pkl"

if os.path.exists(modelo_path):
    with open(modelo_path, "rb") as f:
        modelo_carregado = pickle.load(f)
    print("Modelo carregado com sucesso!")
else:
    print("ATENÇÃO: Nenhum modelo encontrado. Treine um modelo em /treinar")


# ---------------------------
# ROTA PRINCIPAL
# ---------------------------
@app.route('/')
def home():
    return render_template("home.html")  # extends index.html


# ---------------------------
# LISTAR LIVROS
# ---------------------------
@app.route('/livros')
def listar_livros():
    return render_template("livros.html", livros=livros)


# ---------------------------
# NOVO LIVRO
# ---------------------------
@app.route('/livros/novo', methods=['GET', 'POST'])
def novo_livro():
    global next_id

    if request.method == 'POST':
        livro = {
            "id": next_id,
            "titulo": request.form['titulo'],
            "autor": request.form['autor'],
            "genero": request.form['genero'],
            "ano_publicacao": request.form['ano_publicacao'],
            "paginas": request.form['paginas'],
            "avaliacao": request.form['avaliacao'],
            "preco": request.form['preco'],
            "estoque": request.form['estoque'],
        }
        livros.append(livro)
        next_id += 1
        flash("Livro cadastrado com sucesso!", "success")
        return redirect(url_for('listar_livros'))

    return render_template("form_livro.html", livro=None)


# ---------------------------
# EDITAR LIVRO
# ---------------------------
@app.route('/livros/editar/<int:id>', methods=['GET', 'POST'])
def editar_livro(id):
    livro = next((l for l in livros if l["id"] == id), None)
    if not livro:
        flash("Livro não encontrado!", "danger")
        return redirect(url_for("listar_livros"))

    if request.method == 'POST':
        livro["titulo"] = request.form['titulo']
        livro["autor"] = request.form['autor']
        livro["genero"] = request.form['genero']
        livro["ano_publicacao"] = request.form['ano_publicacao']
        livro["paginas"] = request.form['paginas']
        livro["avaliacao"] = request.form['avaliacao']
        livro["preco"] = request.form['preco']
        livro["estoque"] = request.form['estoque']

        flash("Livro atualizado com sucesso!", "success")
        return redirect(url_for('listar_livros'))

    return render_template("form_livro.html", livro=livro)


# ---------------------------
# EXCLUIR LIVRO
# ---------------------------
@app.route('/livros/excluir/<int:id>')
def excluir_livro(id):
    global livros
    livros = [l for l in livros if l["id"] != id]
    flash("Livro removido!", "warning")
    return redirect(url_for('listar_livros'))


# ---------------------------
# ANÁLISE DE DADOS
# ---------------------------
@app.route('/analise')
def analise():
    return render_template("analise.html")  # extends index.html


# ---------------------------
# TREINAR MODELO
# ---------------------------
@app.route("/treinar", methods=["GET", "POST"])
def treinar():
    if request.method == "POST":

        if not os.path.exists("dados.csv"):
            flash("Nenhum CSV encontrado! Faça upload em /selecionar_csv", "danger")
            return redirect("/treinar")

        df = pd.read_csv("dados.csv")

        from sklearn.ensemble import RandomForestRegressor

        X = df[["paginas", "avaliacao", "ano_publicacao"]]
        y = df["preco"]

        modelo = RandomForestRegressor()
        modelo.fit(X, y)

        with open("modelo_preco.pkl", "wb") as f:
            pickle.dump(modelo, f)

        flash("Modelo treinado usando o CSV carregado!", "success")

        return redirect("/treinar")

    return render_template("treinar.html")

# ---------------------------
# PREVISÃO
# ---------------------------
@app.route("/predict", methods=["GET", "POST"])
def predict():
    global modelo_carregado

    if request.method == "POST":

        # Recarregar modelo na hora
        if os.path.exists("modelo_preco.pkl"):
            with open("modelo_preco.pkl", "rb") as f:
                modelo_carregado = pickle.load(f)
        else:
            flash("Nenhum modelo encontrado! Treine primeiro em /treinar", "danger")
            return redirect("/predict")

        genero = request.form["genero"]
        paginas = int(request.form["paginas"])
        avaliacao = float(request.form["avaliacao"])
        ano_publicacao = int(request.form["ano_publicacao"])

        X = [[paginas, avaliacao, ano_publicacao]]

        pred = modelo_carregado.predict(X)[0]

        return render_template("predict.html", pred=round(pred, 2))

    return render_template("predict.html", pred=None)



# ---------------------------
# SELECIONAR CSV
# ---------------------------
@app.route('/selecionar_csv', methods=['GET', 'POST'])
def selecionar_csv():
    if request.method == 'POST':
        arquivo = request.files.get('arquivo')

        if arquivo:
            # SALVAR CSV NO PROJETO
            caminho_csv = "dados.csv"
            arquivo.save(caminho_csv)

            df = pd.read_csv(caminho_csv)

            return render_template("mostrar_csv.html", dados=df.to_html())

    return render_template("selecionar_csv.html")

# ---------------------------
# EXECUTAR SERVIDOR
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
