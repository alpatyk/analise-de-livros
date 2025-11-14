import os, shutil
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, redirect
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
import joblib

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("modelos", exist_ok=True)
os.makedirs("backups", exist_ok=True)

# Variável global para armazenar o CSV atual
csv_atual = "livros.csv"  # default

# -------------------------
# Backup do CSV
def backup():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    shutil.copy(csv_atual, f"backups/backup_{timestamp}.csv")

# -------------------------
# Rota para escolher ou enviar CSV
@app.route("/selecionar_csv", methods=["GET","POST"])
def selecionar_csv():
    global csv_atual
    if request.method == "POST":
        # Upload de CSV
        if "csv_file" in request.files:
            file = request.files["csv_file"]
            if file.filename.endswith(".csv"):
                caminho = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(caminho)
                csv_atual = caminho
                return f"CSV '{file.filename}' carregado com sucesso!"
        # Seleção de CSV existente
        if "csv_existente" in request.form:
            csv_atual = request.form["csv_existente"]
            return f"CSV '{csv_atual}' selecionado com sucesso!"

    arquivos_csv = [f for f in os.listdir(".") if f.endswith(".csv")] + \
                   [os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".csv")]
    return render_template("selecionar_csv.html", arquivos_csv=arquivos_csv)

# -------------------------
# Home
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------
# CRUD de livros
@app.route("/livros")
def listar():
    df = pd.read_csv(csv_atual)
    return render_template("listar.html", livros=df.to_dict(orient="records"))

@app.route("/livros/novo", methods=["GET","POST"])
def novo():
    if request.method == "POST":
        backup()
        df = pd.read_csv(csv_atual)
        novo = {
            "id": df["id"].max()+1 if not df.empty else 1,
            "titulo": request.form["titulo"],
            "autor": request.form["autor"],
            "genero": request.form["genero"],
            "ano_publicacao": int(request.form["ano_publicacao"]),
            "paginas": int(request.form["paginas"]),
            "avaliacao": float(request.form["avaliacao"]),
            "preco": float(request.form["preco"]),
            "estoque": int(request.form["estoque"])
        }
        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        df.to_csv(csv_atual, index=False)
        return redirect("/livros")
    return render_template("editar.html", livro=None)

@app.route("/livros/editar/<int:id>", methods=["GET","POST"])
def editar(id):
    df = pd.read_csv(csv_atual)
    livro = df[df["id"]==id].iloc[0].to_dict()
    if request.method == "POST":
        backup()
        idx = df[df["id"]==id].index[0]
        for cam in ["titulo","autor","genero","ano_publicacao","paginas","avaliacao","preco","estoque"]:
            df.loc[idx,cam] = request.form[cam]
        df.to_csv(csv_atual, index=False)
        return redirect("/livros")
    return render_template("editar.html", livro=livro)

@app.route("/livros/excluir/<int:id>")
def excluir(id):
    backup()
    df = pd.read_csv(csv_atual)
    df = df[df["id"] != id]
    df.to_csv(csv_atual, index=False)
    return redirect("/livros")

# -------------------------
# Análises / gráficos
@app.route("/analise")
def analise():
    df = pd.read_csv(csv_atual)
    os.makedirs("static/graficos", exist_ok=True)

    # Gráfico 1: Distribuição dos preços
    plt.figure(figsize=(6,4))
    sns.histplot(df["preco"], kde=True)
    plt.title("Distribuição dos Preços")
    plt.savefig("static/graficos/distrib_preco.png")
    plt.close()

    # Gráfico 2: Preço médio por gênero
    plt.figure(figsize=(6,4))
    df.groupby("genero")["preco"].mean().plot(kind="bar")
    plt.title("Preço Médio por Gênero")
    plt.savefig("static/graficos/preco_genero.png")
    plt.close()

    return render_template("analise.html")

# -------------------------
# Treinamento ML
@app.route("/treinar", methods=["GET","POST"])
def treinar():
    if request.method == "POST":
        df = pd.read_csv(csv_atual).dropna()
        le = LabelEncoder()
        if "genero" in df.columns:
            df["genero"] = le.fit_transform(df["genero"])
            joblib.dump(le, "modelos/encoder_genero.pkl")  # salva encoder atualizado

        X = df[["genero","paginas","avaliacao","ano_publicacao"]]
        y = df["preco"]
        Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.2)
        modelo = request.form["modelo"]
        if modelo=="linear": m = LinearRegression()
        elif modelo=="rf": m = RandomForestRegressor()
        else: m = KNeighborsRegressor()
        m.fit(Xtr,ytr)
        score = m.score(Xte,yte)
        joblib.dump(m, "modelos/modelo.pkl")
        return render_template("treino.html", score=round(score,3))
    return render_template("treino.html", score=None)

# -------------------------
# Previsão de preço
@app.route("/predict", methods=["GET","POST"])
def predict():
    if not os.path.exists("modelos/modelo.pkl") or not os.path.exists("modelos/encoder_genero.pkl"):
        return "Treine o modelo primeiro em /treinar"

    m = joblib.load("modelos/modelo.pkl")
    le = joblib.load("modelos/encoder_genero.pkl")
    pred = None

    if request.method == "POST":
        genero_texto = request.form["genero"]
        paginas = float(request.form["paginas"])
        avaliacao = float(request.form["avaliacao"])
        ano = float(request.form["ano_publicacao"])

        # Converter texto → número, com verificação de rótulo desconhecido
        if genero_texto not in le.classes_:
            return f"Gênero '{genero_texto}' não está no encoder. Treine novamente com este gênero."
        genero_num = le.transform([genero_texto])[0]

        pred = m.predict([[genero_num, paginas, avaliacao, ano]])[0]
        pred = round(float(pred), 2)

    return render_template("predict.html", pred=pred)

# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
