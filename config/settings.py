"""
Django settings for config project.
Generated by 'django-admin startproject' using Django 3.1.1.
For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
import django_heroku
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+4x3v5f2_=%ltehp^x1y_+(%fx-+v5^ak#n8kg)&9d-*ns-7rb'

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', 'srlpp.herokuapp.com']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'catalogue',
    'accounts',
    'mails'
]

MIDDLEWARE = [
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
            'custom_tags':'catalogue.template_tags.custom_tags'
            }
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases


# After updating the database from sqlite to MongoDB, we do not need ORM anymore,
# therefore we could just comment out the database settings.
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
"""

DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'srlpp.postgres',
        'USER': 'postgres',
        'PASSWORD': '950128950128',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Amazon s3 settings
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_URL = os.environ.get('AWS_URL')
AWS_DEFAULT_ACL = None
AWS_S3_REGION_NAME = 'eu-central-1'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_BUCKET = 'srlpfiles'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_URL = AWS_URL + 'static/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

# CATALOGUE_DIR = os.path.join(BASE_DIR, 'static').join('catalogue_data')
CATALOGUE_DIR = AWS_URL + 'static/catalogue_data/'
PUBLISHED_CATALOGUE_DIR = os.path.join(CATALOGUE_DIR, 'published')
SUBMITTED_CATALOGUE_DIR = os.path.join(CATALOGUE_DIR, 'submitted')
GRAPH_DIR = AWS_URL + 'static/graphs/'
MEDIA_URL = AWS_URL + 'media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

TEMP_DIR = os.path.join(BASE_DIR, 'static').join('temp')

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

#DataFlair
EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_PORT = 587
EMAIL_HOST_USER = 'srl.plusplus@gmail.com'
EMAIL_HOST_PASSWORD = 'srlpp2022'
# EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = os.path.join(BASE_DIR, "sent_emails")


"""
db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)
"""
django_heroku.settings(locals())
