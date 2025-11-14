#!/bin/bash
# Script para criar venv, instalar dependências e rodar a app (Linux/Mac)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
