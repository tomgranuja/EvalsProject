# EvalsProject

EvalsProject is a straightforward web application designed to simplify academic record-keeping by organizing student marks and attendance. Built specifically for teachers and school administrators of a free learning comunity, the platform provides a solution for managing daily classroom data and monitoring educational progress without unnecessary complexity.

## Getting started

Follow this steps in order to make a python virtual environment, install django, clone this repo and make an admin user.

### Django

This project use [Django](https://www.djangoproject.com/) web framework. It can be installed in a python virtual environment.

```bash
$ mkdir ~/.venv
$ python -m venv ~/.venv/dj
$ source ~/.venv/dj/bin/activate

# No need --user because on a virtual env.
(dj)$ pip install django==5.2
(dj)$ python -m django --version
```

The next time this environment is needed use the activation script and then deactivate it to restore the system environment:

```bash
$ source ~/.venv/dj/bin/activate
(dj)$ ...
(dj)$ ...
(dj)$ deactivate
$ 
```

### Github source code

Download the application source code.

```bash
# Clone repo, no need for virtual env
$ git clone https://github.com/tomgranuja/EvalsProject.git
```

### Admin user creation

Create the [django default database](https://docs.djangoproject.com/en/5.1/intro/tutorial02/#database-setup) and make an [admin user](https://docs.djangoproject.com/en/5.1/intro/tutorial02/#creating-an-admin-user):

```bash
# Activate python virtual environment
$ source ~/.venv/dj/bin/activate

# Make system database
(dj)$ cd EvalsProject
(dj) [EvalsProject]$ python manage.py migrate

# Create admin user
(dj) [EvalsProject]$ python manage.py createsuperuser
> Username: some-test-user
> Email address: admin@example.com
> Password: **********
> Password (again): *********
> Superuser created successfully.
```

### Ready to test

The application server now is ready to run, but only the admin user is registered.

To add new users run the server and go to the admin site [http://127.0.0.1:8000/admin]().

```bash
# Run the server
(dj) [EvalsProject]$ python manage.py runserver

# Go to http://127.0.0.1:8000/admin
```

Navigate to Users to add new users. Then populate some teachers, cycles, students and activities.

## Local vars and secrets

Some local vars can be customize in `config/.local_settings` file. This file should be created with chmod 600 filesystem permission to keep secrets.


``` bash
# Optional configuration vars
$ cd EvalsProject
[EvalsProject]$ touch config/.local_settings
[EvalsProject]$ chmod 600 config/.local_settings
```

### Secret key

The [secret key](https://docs.djangoproject.com/en/5.1/ref/settings/#secret-key) is used to provide cryptographic signing, and should be set to a unique, unpredictable value. In particular is used for sessions and messages.

The secret key must be a random 50 character minimum string. Use the following command to generate a secure string, see [generate-django-secret-key by Humberto Rocha](https://humberto.io/blog/tldr-generate-django-secret-key/).

```bash
# Print a random 50 char string
$ python -c "import secrets; print(secrets.token_urlsafe(38))"
```

### Time zone

See [Time zones](https://docs.djangoproject.com/en/5.1/topics/i18n/timezones/) for an explanation of the time zone settings needed. In brief when time zone support is enabled, django stores UTC datetime data in the database, use time zone aware objects internally and translate them to the end user time zone in templates and forms.

Available time zones can be consulted in python with `zoneinfo.available_timezones()`

### Local settings example

```bash
SECRET_KEY = ...some fifty chars random string...
TIME_ZONE = America/Santiago
ALLOWED_HOSTS = mysite.mydomain.com
DEBUG = False
```

This is an example of `config/.local_settings` with a secret key and a chilean time zone. Also the DEBUG flag can be turned off overiding django settings DEBUG configuration. This is handy for maintaining a production server (e.g., don't show server error tracebacks in the client browser).