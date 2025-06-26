#!/bin/bash

echo "Ativando ambiente virtual..."
source venv/bin/activate

echo "Fazendo pull do repositório Git..."
git reset --hard
git pull origin main

echo "Instalando dependências..."
pip freeze > requirements.txt
pip install -r requirements.txt

echo "Rodando migrações..."
python manage.py makemigrations
python manage.py migrate

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Reiniciando Gunicorn e Nginx..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "Deploy concluído com sucesso!"