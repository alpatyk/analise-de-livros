import pandas as pd
import random

# Definir listas de dados
generos = ['Ação', 'Comédia', 'Drama', 'Ficção Científica', 'Fantasia', 'Terror', 'Romance']
autores = ['John Smith', 'Jane Doe', 'Carlos Silva', 'Maria Oliveira', 'Lucas Santos', 'Ana Costa']
titulos = ['O Início', 'A Jornada', 'Destino Final', 'No Limite', 'Segredos do Tempo',
           'O Retorno', 'Além das Estrelas', 'Sombras', 'Luz da Esperança', 'Última Chance']

# Lista para armazenar os filmes
filmes = []

for i in range(1, 1001):
    filme = {
        'id': i,
        'titulo': random.choice(titulos) + f" {i}",  # garante título único
        'autor': random.choice(autores),
        'genero': random.choice(generos),
        'ano_publicacao': random.randint(1980, 2025),
        'paginas': random.randint(80, 180),  # duração em minutos
        'avaliacao': round(random.uniform(1, 5), 1),  # nota 1 a 5 com uma casa decimal
        'preco': round(random.uniform(10, 100), 2),
        'estoque': random.randint(0, 50)
    }
    filmes.append(filme)

# Criar DataFrame
df = pd.DataFrame(filmes)

# Salvar CSV
df.to_csv('catalogo_filmes.csv', index=False, sep=',', encoding='utf-8')

print("CSV 'catalogo_filmes.csv' criado com 1000 filmes!")
