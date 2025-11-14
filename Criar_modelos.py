import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.dummy import DummyClassifier
import os

# Caminho do CSV
csv_path = "dados/livros.csv"  # ajuste conforme seu projeto

# Lê os dados
df = pd.read_csv(csv_path)

# Cria a pasta 'modelos' se não existir
if not os.path.exists("modelos"):
    os.makedirs("modelos")

# -------------------------
# 1. Encoder de gênero
df['genero'] = df['genero'].astype(str)
encoder_genero = LabelEncoder()
encoder_genero.fit(df['genero'].unique())

with open("modelos/encoder_genero.pkl", "wb") as f:
    pickle.dump(encoder_genero, f)

print("encoder_genero.pkl criado com sucesso.")

# -------------------------
# 2. Encoder de categoria
df['categoria'] = df['categoria'].astype(str)
encoder_categoria = LabelEncoder()
encoder_categoria.fit(df['categoria'].unique())

with open("modelos/encoder_categoria.pkl", "wb") as f:
    pickle.dump(encoder_categoria, f)

print("encoder_categoria.pkl criado com sucesso.")

# -------------------------
# 3. Modelo ML dummy (exemplo)
X_dummy = [[0], [1], [2], [3], [4]]
y_dummy = [0, 1, 0, 1, 0]

modelo_dummy = DummyClassifier(strategy="most_frequent")
modelo_dummy.fit(X_dummy, y_dummy)

with open("modelos/modelo_ml_dummy.pkl", "wb") as f:
    pickle.dump(modelo_dummy, f)

print("modelo_ml_dummy.pkl criado com sucesso.")
