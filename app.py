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

def backup():
    if not os.path.exists("backups"): os.makedirs("backups")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    shutil.copy("livros.csv", f"backups/backup_{timestamp}.csv")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/livros")
def listar():
    df = pd.read_csv("livros.csv")
    return render_template("listar.html", livros=df.to_dict(orient="records"))

@app.route("/livros/novo", methods=["GET","POST"])
def novo():
    if request.method == "POST":
        backup()
        df = pd.read_csv("livros.csv")
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
        df.to_csv("livros.csv", index=False)
        return redirect("/livros")
    return render_template("editar.html", livro=None)

@app.route("/livros/editar/<int:id>", methods=["GET","POST"])
def editar(id):
    df = pd.read_csv("livros.csv")
    livro = df[df["id"]==id].iloc[0].to_dict()
    if request.method == "POST":
        backup()
        idx = df[df["id"]==id].index[0]
        for cam in ["titulo","autor","genero","ano_publicacao","paginas","avaliacao","preco","estoque"]:
            df.loc[idx,cam] = request.form[cam]
        df.to_csv("livros.csv", index=False)
        return redirect("/livros")
    return render_template("editar.html", livro=livro)

@app.route("/livros/excluir/<int:id>")
def excluir(id):
    backup()
    df = pd.read_csv("livros.csv")
    df = df[df["id"] != id]
    df.to_csv("livros.csv", index=False)
    return redirect("/livros")

@app.route("/analise")
def analise():
    df = pd.read_csv("livros.csv")

    os.makedirs("static/graficos", exist_ok=True)

    # grafico 1
    plt.figure(figsize=(6,4))
    sns.histplot(df["preco"], kde=True)
    plt.title("Distribuição dos Preços")
    plt.savefig("static/graficos/distrib_preco.png")
    plt.close()
    # grafico 2
    plt.figure(figsize=(6,4))
    df.groupby("genero")["preco"].mean().plot(kind="bar")
    plt.title("Preço Médio por Gênero")
    plt.savefig("static/graficos/preco_genero.png")
    plt.close()
    return render_template("analise.html")

@app.route("/treinar", methods=["GET","POST"])
def treinar():
    if request.method == "POST":
        df = pd.read_csv("livros.csv")
        df = df.dropna()
        if "genero" in df.columns:
            le = LabelEncoder()
            df["genero"] = le.fit_transform(df["genero"])
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

@app.route("/predict", methods=["GET","POST"])
def predict():
    if not os.path.exists("modelos/modelo.pkl"):
        return "Treine o modelo primeiro em /treinar"

    m = joblib.load("modelos/modelo.pkl")
    le = joblib.load("modelos/encoder_genero.pkl")

    pred = None

    if request.method == "POST":
        genero_texto = request.form["genero"]
        paginas = float(request.form["paginas"])
        avaliacao = float(request.form["avaliacao"])
        ano = float(request.form["ano_publicacao"])

        # converter texto → número
        genero_num = le.transform([genero_texto])[0]

        pred = m.predict([[genero_num, paginas, avaliacao, ano]])[0]
        pred = round(float(pred), 2)

    return render_template("predict.html", pred=pred)

if __name__ == "__main__":
    app.run(debug=True)
