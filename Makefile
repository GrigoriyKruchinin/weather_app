mig:
	python manage.py makemigrations & python manage.py migrate

start:
	docker-compose up --build

up:
	docker-compose up
