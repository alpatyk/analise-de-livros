# 📚 Sistema de Previsão de Preços de Livros — Flask + Machine Learning

Este projeto é uma aplicação web desenvolvida em **Flask**, que permite:

- 📤 Fazer upload de arquivos CSV  
- 🔎 Visualizar uma prévia dos dados enviados  
- 📊 Gerar gráficos de análise exploratória  
- 🤖 Treinar um modelo de Machine Learning (Random Forest)  
- 💰 Prever o preço de livros com base em seus atributos  
- 📘 Cadastrar, editar e excluir livros manualmente  

O sistema foi criado para fins acadêmicos, demonstrando integração entre backend, frontend e modelo preditivo.

---

## 🧠 **Funcionalidades**

### 🔹 1. Upload de CSV (`/selecionar_csv`)
O usuário envia um arquivo CSV contendo dados de livros.  
O sistema salva esse arquivo como **`dados.csv`** e mostra uma prévia dos dados.

---

### 🔹 2. Visualização do CSV (`/mostrar_csv`)
Exibe as primeiras linhas do arquivo enviado para conferência.

---

### 🔹 3. Treinamento do Modelo (`/treinar`)
- Lê o arquivo `dados.csv`
- Treina um modelo **RandomForestRegressor**
- Gera gráficos exploratórios
- Salva o modelo como **`modelo_preco.pkl`**

Esse modelo será usado na previsão de preços.

---

### 🔹 4. Previsão de Preço (`/predict`)
O usuário informa:

- gênero  
- páginas  
- avaliação  
- ano de publicação  

O sistema usa o modelo treinado para prever o **preço estimado do livro**.

---

### 🔹 5. CRUD de Livros (`/livros`)
Permite:

- 📘 Cadastrar novo livro  
- ✏ Editar livro  
- ❌ Excluir livro  
- 📄 Listar todos os livros  

Os dados ficam armazenados temporariamente (em memória).

---

## 📁 **Estrutura do Projeto**

