# Deployment

## Local Environment Steps

1. Install `dotenv` `gunicorn` and `psycopg2-binary`.

   ```shell
   pip install django-dotenv gunicorn psycopg2-binary
   ```

1. Update requirements.txt.

1. Create an `.env` file in the root directory of the project.
   ```shell
   touch .env
   ```
1. Enter the following into your env file for local production (windows users can ignore the export):
   ```
   export DJANGO_SECRET_KEY=examplesecrectkey
   export DEBUG=1
   export DJANGO_ALLOWED_HOST=127.0.0.1, localhost
   export DISABLE_COLLECTSTATIC=1
   export DEVELOPMENT=1
   ```
1. Update settings.py.

   ```python
   # settings.py
   from pathlib import Path
   import os

   SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-ci4ahx=rt$*sl5_a*79vu!)yo758x34_t8%*^o5!hpmm6)i-mc")

   DEBUG = str(os.environ.get("DEBUG")) == "1"

   ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOST", "127.0.0.1,localhost").split(",")

   POSTGRES_DB = os.environ.get('POSTGRES_DB')
   POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
   POSTGRES_USERNAME = os.environ.get('POSTGRES_USERNAME')
   POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
   POSTGRES_PORT = os.environ.get('POSTGRES_PORT')

   DEVELOPMENT = str(os.environ.get('DEVELOPMENT')) == '1'

   if DEVELOPMENT:
       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.sqlite3',
               'NAME': BASE_DIR / 'db.sqlite3',
           }
       }
   else:
       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.postgresql',
               'NAME': POSTGRES_DB,
               'USER': POSTGRES_USERNAME,
               'PASSWORD': POSTGRES_PASSWORD,
               'HOST': POSTGRES_HOST,
               'PORT':POSTGRES_PORT,
           }
       }

   STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
   STATIC_URL = "/static/"
   STATIC_ROOT = os.path.join(BASE_DIR, "static-cdn")
   MEDIA_URL = "/media/"
   MEDIA_ROOT = os.path.join(BASE_DIR, "media")
   ```

1. Add `.env` and `static-cdn/` to your `gitignore`.

   ```
   ...
   .env
   static-cdn/
   ```

1. Generate a `secret key` and assign it to `DJANGO_SECRET_KEY` in the `.env` file.

   ```shell
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

1. Update manage.py to access `.env` file.

   ```python
   # manage.py
   import os
   import sys
   import dotenv
   import pathlib

   def main():
      DOT_ENV_PATH = pathlib.Path() / '.env'
      if DOT_ENV_PATH.exists():
         dotenv.read_dotenv(str(DOT_ENV_PATH))
      ...
   ```

1. Commit and push your code to github.

## Digital Ocean - Deploying Django & Postgres

1. Go do [Digital Ocean](https://cloud.digitalocean.com/registrations/new) and register an account.
1. Create a new `App`.
1. Select `Github`.
1. Edit your `github permissions` to allow Digital Ocean access to your repos.
1. Select repository.
1. Select `main branch`.
1. Ensure `auto deploy` is selected.
1. Click on `edit plan`, then select `basic` and under size choose $5.
1. Click on `add resource` and `select database`. Then create and attach.
1. Before clicking next, click the `edit icon` next to the `django app`.
1. Edit run command to include the wsgi folder (add the foldername that contains the settings file).

   ```shell
   python manage.py migrate --noinput
   gunicorn --worker-tmp-dir /dev/shm <projectname>.wsgi
   ```

1. `Save`, go back and click next.

1. Click edit next to the django application to update environment variables (remove/replace the databse_url and add the following, leave postgres variables and allowed_hosts blank):

   ```
   DISABLE_COLLECTSTATIC=1
   DEBUG = 0
   DEVELOPMENT=0
   DJANGO_SECRET_KEY=<anewsecret>
   DJANGO_ALLOWED_HOST
   POSTGRES_DB
   POSTGRES_HOST
   POSTGRES_USERNAME
   POSTGRES_PASSWORD
   POSTGRES_PORT
   ```

1. Select `Bangalore` as the `region`.
1. Wait for the resource to be created.
1. Under components, click on your `database`.
1. Click on `connection details`.
1. Copy the key value pairs (preferably into a notepad).
1. Under components, click on your django application.
1. Scroll down to the django environment variables and click edit. Update the postgres variables with the values of the keys you copied.

   ```
   DISABLE_COLLECTSTATIC=1
   DEBUG = 0
   DEVELOPMENT=0
   DJANGO_SECRET_KEY=<anewsecret>
   DJANGO_ALLOWED_HOST = <appname>.ondigitalocean.app
   POSTGRES_DB=db
   POSTGRES_HOST=host
   POSTGRES_USERNAME=dbusername
   POSTGRES_PASSWORD=dbpassword
   POSTGRES_PORT=dbport
   ```

1. Encrypt both the `secretkey` and all `passwords`, then click save.
1. Allow the build to complete. Then find and click on console to run the commands to make migrate and createsuperuser.

## Static and User Uploads

1. Navigate to the project where you django application is is being hosted.
1. Click on `start using spaces`.
1. Leave the default location and configuration for file listing (should be in Frankfurt, Germany).
1. Assign a unique name for the space.
1. Ensure that correct project is selected.
1. Copy the space url for later reference.
1. Click on spaces in the side bar.
1. Click on manage keys.
1. Scroll down to spaces access keys, and click on generate key.
1. Copy the key and enter it into both your `.env` and `app variables` as the following (also encrypt them on digital ocean), you should have a total:
   ```
   AWS_ACCESS_KEY_ID=yourvalues
   AWS_SECRECT_ACCESS_KEY=yourvalues
   AWS_STORAGE_BUCKET_NAME=static
   SPACE_NAME=<use the unique name for the space>
   AWS_S3_REGION_NAME=fra1
   ```
1. Install the following packages in your local environment and update your requirements.txt.
   ```shell
   pip install django-storages boto3
   ```
1. Within the directory containing your setting file, create a folder called cdn.
1. Create an empty **init**.py and backends.py
1. Add the following to your backends.py file:

   ```python
   # projectname.cdn.backends

   from django.conf import settings
   from storages.backends.s3boto3 import S3Boto3Storage

   class StaticStorage(S3Boto3Storage):
      location = 'static'
      default_acl = 'public-read'


   class MediaStorage(S3Boto3Storage):
      bucket_name = 'media'
      location = ''
   ```

1. Within the settings.py update and add the following:

   ```python
   # <project>.settings
   STATIC_ROOT = os.path.join(BASE_DIR, "static-cdn")
   STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
   MEDIA_ROOT = os.path.join(BASE_DIR, "media")

   if not DEVELOPMENT:
      AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
      AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
      AWS_STORAGE_BUCKET_NAME=os.environ.get('AWS_STORAGE_BUCKET_NAME')
      SPACE_NAME = os.environ.get('SPACE_NAME')
      AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
      AWS_S3_ENDPOINT_URL=f'https://{SPACE_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com'
      AWS_DEFAULT_ACL = 'public-read'
      AWS_STATIC_LOCATION = 'static'
      AWS_S3_OBJECT_PARAMETERS = {
         'CacheControl': 'max-age=86400'
      }
      AWS_MEDIA_LOCATION = 'media'
      PUBLIC_MEDIA_LOCATION = 'media'

      STATIC_URL = '%s/%s/%s' % (AWS_S3_ENDPOINT_URL, AWS_STATIC_LOCATION, '/')
      MEDIA_URL = '%s%s%s' % (AWS_S3_ENDPOINT_URL, AWS_MEDIA_LOCATION, '/')

      STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
      DEFAULT_FILE_STORAGE = 'core.cdn.backends.MediaStorage'
   else:
      STATIC_URL = "/static/"
      MEDIA_URL = "/media/"
   ```

1. Update the installed apps.

   ```python
   INSTALLED_APPS = [
       ...
       'storages',
   ]

   ...

   from <projectsname>.cdn.conf import *
   ```

1. Update your main urls.py in the project config.

   ```python
   # <projectname>.urls.py
   urlpatterns = [
      ...
   ]


   urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```

1. Create a .sampleenv to ensure others can use these configurations easily (should be allowed in the repo and should look like this for local development).

   ```
   DJANGO_SECRET_KEY=
   DEBUG=1
   DJANGO_ALLOWED_HOST=127.0.0.1, localhost
   DISABLE_COLLECTSTATIC=1
   DEVELOPMENT=1

   AWS_ACCESS_KEY_ID=
   AWS_SECRET_ACCESS_KEY=
   AWS_STORAGE_BUCKET_NAME=
   SPACE_NAME=
   AWS_S3_REGION_NAME=
   ```

1. Commit and push your code.
