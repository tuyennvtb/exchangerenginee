"""
Django settings for BitmoonExchanger project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import dj_database_url
import environ
import sys
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration



env = environ.Env()
environ.Env.read_env()



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'g=rq)jih&=8wm4+=fsx6z6tzuy4g@wbc2$mi*63_+bmbnf8pfb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'BitmoonExchanger.Api',
    'BitmoonExchanger.BMUtils',
    'BitmoonExchanger.BMBrokers',
    'BitmoonExchanger.BMExchanger',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BitmoonExchanger.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BitmoonExchanger.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(default=env('DATABASE_URL'))
}
# DATABASES['default']['OPTIONS'] = {'charset': "utf8mb4"}

# print(DATABASES)

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL'),
        "KEY_PREFIX": "BitmoonExchangerCaching"
    }
}


REDIS_URL =  env('REDIS_URL')


CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

CELERYD_MAX_TASKS_PER_CHILD=120
CELERYD_MAX_MEMORY_PER_CHILD=900000
CELERYD_CONCURRENCY = 1
CELERYD_TASK_SOFT_TIME_LIMIT=600

BACKEND_JWT_SECRET_KEY=env('BACKEND_JWT_SECRET_KEY')
BACKEND_EXCHANGER_SECRET_KEY=env('BACKEND_EXCHANGER_SECRET_KEY')
EXCHANGER_WALLET_SECRET_KEY=env('EXCHANGER_WALLET_SECRET_KEY')

WALLET_URL  = env('WALLET_API_URL')
WITHDRAW_API_URL  = env('WITHDRAW_API_URL')
#WALLET_URL = 'http://wallet-api-uat.uat.svc.cluster.local/'
MINIMUM_TRANSACTION_VALUE = 200000

# LOGGING = {
#     'version': 1,
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         }
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         }
#     }
# }

sentry_sdk.init(
    environment=env('ENVIRONMENT'),
   
    # dsn="https://fa30e948f1bc46c6bc58942edba06052@o607501.ingest.sentry.io/5745261", #BM-Tuyen
    # dsn = "https://038a274a7e5e470696a7b2af70ae8aac@o673569.ingest.sentry.io/5768273", #BM-Tuyen-backup
        # dsn="https://5a71f107159e49c9b16780bf2810a350@o976671.ingest.sentry.io/5933017", #BM-0826
        dsn="https://0dc12dfe12f9420281ef4e7d2cd63dfd@o1052595.ingest.sentry.io/6036362", #BM-1026



    integrations=[DjangoIntegration(),CeleryIntegration(),RedisIntegration()],
    traces_sample_rate=0.2,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

