# API_YaMDB
### Описание
База данных отзывов на художественные произведения - книги, фильмы и музыку.
### Технологии
Python 3.8
Django 3.0.5
Django REST framework 3.11.0
PostgreSQL 12.4
NGINX 1.19.3
Docker
### Установка Docker
Mac: https://docs.docker.com/docker-for-mac/install/
Windows: https://docs.docker.com/docker-for-windows/install/
Ubuntu: https://docs.docker.com/engine/install/ubuntu/
### Загрузка Docker-образа приложения
```bash
docker pull bkvsk/yamdb:v1.0
```
### Заполнение .env
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
### Разворот приложения с помощью Docker
Чтобы развернуть приложение, из корневой директории выполните следующий набор команд:
```bash
docker-compose up -d --build
docker-compose exec web python manage.py makemigrations api
docker-compose exec web python manage.py migrate --noinput
docker-compose exec web python manage.py collectstatic --no-input
```
### Создание суперпользователя
```bash
docker-compose exec web python manage.py createsuperuser
```
### Автор
Быковский Павел,
студент 12 когорты курса Python-разработчик от ЯндексПрактикум