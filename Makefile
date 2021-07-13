BIN=venv/bin/

.PHONY: run makemigrations migrate rebuild

run:
	$(BIN)python manage.py runserver

makemigrations:
	$(BIN)python manage.py makemigrations

migrate:
	$(BIN)python manage.py migrate

rebuild:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc"  -delete
	rm -rf db.sqlite3
	pip install --upgrade --force-reinstall  django==3.0.5
	$(BIN)python manage.py makemigrations
	$(BIN)python manage.py migrate
	DJANGO_SUPERUSER_USERNAME=admin \
	DJANGO_SUPERUSER_PASSWORD=admin \
	$(BIN)python manage.py createsuperuser --email 'admin@localhost.ru' --noinput

