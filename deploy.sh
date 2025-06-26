#!/bin/bash

echo "Ativando ambiente virtual..."
source venv/bin/activate

echo "Fazendo pull do reposit�rio Git..."
git reset --hard
git pull origin main

echo "Instalando depend�ncias..."
pip freeze > requirements.txt
pip install -r requirements.txt

echo "Rodando migra��es..."
python manage.py makemigrations
python manage.py migrate

echo "Coletando arquivos est�ticos..."
python manage.py collectstatic --noinput

echo "Reiniciando Gunicorn e Nginx..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "Deploy conclu�do com sucesso!"