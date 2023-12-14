## Case study

### The project
- Process a .csv file that contains a list of contacts and send a "Hi {name}, Welcome!" email to each contact.
- Each contact should receive at most one email, including cases where the same contact is listed multiple times in a .csv or is included in 2 or more .csv files.
- Emails to contacts that are `bounced` should be treated as permanent failures and should not be retried.
- Emails to contacts that are `blocked` should be treated as temporary failures and should be retried by sending a new email.
- The .csv should be processed as quickly as possible, ideally in less than 1 minute.
- The .csv file format is listed below, and the full input file is available at `/input.csv`
```
David Smith, david.smith@example.com, 555-555-5555, 12345 Anywhere St, San Diego, CA, 92101
Sarah Smith, sarah.smith@example.com, 222-222-2222, 67890 Anywhere St, San Diego, CA, 92101
``

### Environment
We have set up a case study environment that includes a skeleton Django project with Celery using Docker to get you started and skip past the boilerplate project setup.
#### Docker services
`docker-compose.yml` has been setup to bring up the service containers for Django, Celery, RabbitMQ, and Redis.
  - `web` - Django service with Django REST Framework
  - `celery` - Celery worker configured to work with Django, this worker is configured to handle 25 concurrent tasks.
  - `db` - Postgres database used by Django.
  - `rabbitmq` - RabbitMQ message broker used by Celery.
  - `redis` - Redis results store used by Celery.

#### Makefile
`Makefile` has some useful commands to help you work with the Django and Celery services.
```angular2html
build                          Build the docker image used by the 'web' and 'celery' services in the docker-compose.yml
build-no-cache                 Build the docker image, without the the docker build cache, used by the 'web' and 'celery' services in the docker-compose.yml
up                             Run all the services, web (Django), Celery, RabbitMQ, Postgres, Redis
migrate                        Create and apply database migrations
createsuperuser                Create the root Django superuser with username=root password=root
admin                          Open the Django admin page
psql                           Open a Postgres shell
zsh                            Open a zsh shell with all dependencies
sendemails-eager               Run the send_email Django management with CELERY_TASK_ALWAYS_EAGER=True which runs the worker_send_email tasks synchronously
sendemails                     Run the send_email Django management command which queues the worker_send_emails to run on the celery worker
submit                         Dump the Postgres database and package your project into a solution.zip file you can submit
```

### Project skeleton
- `/casestudy/management/commands/send_email.py` - Django management command that will send an email using the `worker_send_email` Celery task.
- `/casestudy/migrations/0001_initial.py` - Django initial database migration that creates the Email table.
- `/casestudy/admin.py` - Django admin configuration for the Email table.
- `/casestudy/celery.py` - Celery configuration for the `casestudy` Django app.
- `/casestudy/emailclient.py` - Instead of sending emails to a real email service we have provided a mock email client that will simulate sending real emails and getting status updates emails that have been sent.
- `/casestudy/models.py` - Django model for the Email table, add any new fields you need to the Email model, or new models if needed. Once you have added new fields run `make migrate` to create the new migration files and apply them to the db.
- `/casestudy/settings.py` - Django settings file, with the default settings for the project. You can add any new settings you need to this file.
- `/casestudy/tasks.py` - Celery tasks. We have defined a `worker_send_email` task, you can add any new tasks you need to this file.
- `/casestudy/urls.py` - Django urls. We have setup the `/admin/` routes for the Django admin. 
- `/casestudy/wsgi.py` - Django wsgi (Web Server Gateway Interface) file, you should not need to touch this file, it is part of the Django framework.

### Getting started
You'll need to run a few `Makefile` commands to get started. Run these commands in single terminal.
- `make build` - this will build the Docker images required to run the Django and Celery services
- `make migrate` - this will create the database tables required by Django
- `make createsuperuser` - this will create a superuser for the Django admin page with username=root and password=root
- `make up` - this will bring all the services up

Once you have the services up, open a new terminal to test that all the services are running.

- `make sendemails-eager` - sets the `CELERY_TASK_ALWAYS_EAGER=True` environment variable and runs the Django management command `send_email` which executes the Celery task `worker_send_email` 4 times synchronously in the terminal. This is a great way to develop your solution, all the code runs in a single container and it's easy to debug.
```
➜ make sendemails-eager
docker compose exec -e CELERY_TASK_ALWAYS_EAGER=True web python3 manage.py sendemails --count 4
Email sent to user_0@example.com id=93407a62-0297-459e-bf33-8d1db76b0071
Email sent to user_1@example.com id=5d0138b2-51d6-4c9d-82ea-80724943f63c
Email sent to user_2@example.com id=892e607e-cf4f-4cdd-ab12-6313aa510943
Email sent to user_3@example.com id=ebfa39fc-7620-422c-b34a-59f9065761a6
```

- `make sendemail` - runs the Django management command `send_email` which queues the Celery task `worker_send_email` 4 times. 
The tasks execute asynchronously in the 'celery' service running in first terminal, where up to 25 tasks can execute concurrently.
Debugging the tasks asynchronously is much harder. You'll need to use this command when you are ready to test your final code and prove that it runs quickly.
```
rabbitmq           | 2023-07-16 20:33:06.850843+00:00 [info] <0.710.0> accepting AMQP connection <0.710.0> (172.19.0.5:48788 -> 172.19.0.4:5672)
rabbitmq           | 2023-07-16 20:33:06.853648+00:00 [info] <0.710.0> connection <0.710.0> (172.19.0.5:48788 -> 172.19.0.4:5672): user 'guest' authenticated and granted access to vhost '/'
platform-celery-1  | [2023-07-16 20:33:06,858: INFO/MainProcess] Received task: casestudy.tasks.worker_send_email[93d5a24d-0d0d-4b1a-94a9-ff6a52672a71]
platform-celery-1  | [2023-07-16 20:33:06,859: INFO/MainProcess] Received task: casestudy.tasks.worker_send_email[077b0567-5822-4d80-8b4c-125e37584c64]
platform-celery-1  | [2023-07-16 20:33:06,861: INFO/MainProcess] Received task: casestudy.tasks.worker_send_email[5c54be08-58e4-44ed-91fe-4aa60810f796]
platform-celery-1  | [2023-07-16 20:33:06,862: WARNING/ForkPoolWorker-8] Email sent to user_0@example.com id=5248cb25-016b-432b-821f-aad8ad990919
platform-celery-1  | [2023-07-16 20:33:06,862: WARNING/ForkPoolWorker-9] Email sent to user_2@example.com id=dfa7b578-6411-4d4a-b37f-9e7c5dbb2727
platform-celery-1  | [2023-07-16 20:33:06,862: WARNING/ForkPoolWorker-1] Email sent to user_1@example.com id=c121f08a-cbe7-49cf-96db-0095b9503fac
platform-celery-1  | [2023-07-16 20:33:06,864: INFO/MainProcess] Received task: casestudy.tasks.worker_send_email[b4dcb1b3-3a96-409c-8c6b-9694f46c26dc]
platform-celery-1  | [2023-07-16 20:33:06,865: INFO/ForkPoolWorker-9] Task casestudy.tasks.worker_send_email[5c54be08-58e4-44ed-91fe-4aa60810f796] succeeded in 0.002945458050817251s: None
platform-celery-1  | [2023-07-16 20:33:06,865: INFO/ForkPoolWorker-8] Task casestudy.tasks.worker_send_email[93d5a24d-0d0d-4b1a-94a9-ff6a52672a71] succeeded in 0.003069833153858781s: None
platform-celery-1  | [2023-07-16 20:33:06,866: WARNING/ForkPoolWorker-8] Email sent to user_3@example.com id=afb93aa9-bc57-4848-992f-e784387ed14e
platform-celery-1  | [2023-07-16 20:33:06,866: INFO/ForkPoolWorker-1] Task casestudy.tasks.worker_send_email[077b0567-5822-4d80-8b4c-125e37584c64] succeeded in 0.004076041979715228s: None
platform-celery-1  | [2023-07-16 20:33:06,867: INFO/ForkPoolWorker-8] Task casestudy.tasks.worker_send_email[b4dcb1b3-3a96-409c-8c6b-9694f46c26dc] succeeded in 0.0007652498316019773s: None
rabbitmq           | 2023-07-16 20:33:06.900596+00:00 [warning] <0.710.0> closing AMQP connection <0.710.0> (172.19.0.5:48788 -> 172.19.0.4:5672, vhost: '/', user: 'guest'):
rabbitmq           | 2023-07-16 20:33:06.900596+00:00 [warning] <0.710.0> client unexpectedly closed TCP connection```
```

- `make admin` - this will open the Django admin page in your browser, and provides a GUI for the database tables. You can login with username=root and password=root, and see your new email in the Email table.

### Developing
- The Django 'web' container is setup to hot reload any code changes you make will restart the service with the new code.
- The `make sendemails-eager` command executes the celery task in the 'web' container and code changes are immediate.
- Any changes to the Djanogo models can be applied by running `make migrate`, which will update the database schema. 
- The Celery 'celery' container doe not support hot reload and you will need to re-run `make up` to apply your changes when running `make sendemails`. 

### Useful documentation
- https://www.djangoproject.com/ 
- https://www.django-rest-framework.org/
- https://docs.celeryq.dev/en/stable/getting-started/introduction.html
- https://www.rabbitmq.com/

### Post Implementation Note ###
- Added `flower` to docker-compose & requirements.txt for easier celery task monitoring. - Accessible at: `localhost:5555`
- Added `sendemails_inputfile` task with `--inputfile <path to input file>` option. (i.e. `make sendemails_inputfile INPUT_FILE=input.csv`.
- Added Email Status `SKIPPED` to use as termination status for tasks handling duplicate email recipients.
- Added Django(`casestudy/clearcache.py`) / Make command `make clearcache` to reset shared cache between command runs. 
Cache reset is **mandatory** between commands as the key added into cache isn't configured to expire by design of my solution.
- For the exercise, each command run is accompanied by truncating data in `casestudy_emails` first, to not mix up the results across different command runs. This can be improved by adding identity control of emails on table level in in the future.
- The command saves both regularly terminated & skipped (duplicate recipient) email records for review.