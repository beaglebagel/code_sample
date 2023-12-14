.DEFAULT_GOAL := help
.PHONY: help dev


up: ## Run all the services, web (Django), Celery, RabbitMQ, Postgres, Redis
	docker compose up

sendemails-eager: ## Run the send_email Django management with CELERY_TASK_ALWAYS_EAGER=True which runs the worker_send_email task locally
	docker compose exec -e CELERY_TASK_ALWAYS_EAGER=True web python3 manage.py sendemails --count 4

sendemails: ## Run the send_email Django management command which queues the worker_send_email to run on the celery worker
	docker compose exec web python3 manage.py sendemails --count 4

sendemails_inputfile: ## Run the send_email Django management command which queues the worker_send_email to run on the celery worker
	docker compose exec web python3 manage.py sendemails_inputfile --inputfile $(INPUT_FILE)

clearcache: ## small command to clear django cache.
	docker compose exec web python3 manage.py clearcache

zsh: ## Open a shell with all dependencies
	docker compose run web zsh

psql: ## Open a Postgres shell
	docker compose run web python manage.py dbshell

build: ## Build the docker image used by the 'web' and 'celery' services in the docker-compose.yml
	docker compose build web

build-no-cache: ## Build the docker image, without the the docker build cache, used by the 'web' and 'celery' services in the docker-compose.yml
	docker compose build web --no-cache

createsuperuser: ## Create the root Django superuser with username=root password=root
	docker compose \
	    run \
	    -e DJANGO_SUPERUSER_PASSWORD=root \
	    -e DJANGO_SUPERUSER_USERNAME=root \
	    -e DJANGO_SUPERUSER_EMAIL=root@casestudy.com \
	    web \
	    python manage.py createsuperuser --noinput

migrate: ## Create and apply database migrations
	docker compose run web python manage.py makemigrations
	docker compose run web python manage.py migrate

admin: ## Open the Django admin page
	open http://localhost:8000/admin

submit: ## Dump the Postgres database and package your project into a solution.zip file you can submit
	docker compose exec db pg_dump -U postgres -d postgres > db.sql
	zip -r solution.zip .

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
