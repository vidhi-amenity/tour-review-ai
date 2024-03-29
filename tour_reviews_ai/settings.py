"""
Django settings for tour_reviews_ai project.

Generated by 'django-admin startproject' using Django 3.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
from datetime import timedelta
from ._env import env
from celery.schedules import crontab
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG')
PRODUCTION = env.bool('PRODUCTION')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django_celery_results",
    "django_celery_beat",
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'django_filters',
    'authentication',
    'api',
    'streams',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'tour_reviews_ai.csrf_disable_middleware.DisableCsrfCheck',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tour_reviews_ai.urls'

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

WSGI_APPLICATION = 'tour_reviews_ai.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'toure_review',
#         'USER': 'postgres',
#         'PASSWORD': 'root',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("MYSQL_DATABASE", default="new_database"),
        "USER": env.str("MYSQL_USER", default="rarisenpai"),
        "PASSWORD": env.str("MYSQL_PASSWORD", default="9167raritheG"),
        "HOST": env.str("MYSQL_HOST", default="127.0.0.1"),
        "PORT": env.str("MYSQL_PORT", default="3306"),
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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")
MEDIA_URL = "/mediafiles/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets'),
    os.path.join(BASE_DIR, 'assets/fonts'),
]

SITE_URL = 'https://review.com'
SITE_NAME = 'Api.review'
CORS_ORIGIN_ALLOW_ALL = True


SCRAPER_PATH = os.path.join(BASE_DIR, 'gdo_scraper', 'scrapers')

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
# CELERYD_MAX_TASKS_PER_CHILD = 2

CELERY_IMPORTS = ("tour_reviews_ai.tasks", )

AUTH_USER_MODEL = 'authentication.User'
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "-------")


# Source Streams
VIATOR_API_KEY = os.environ.get("VIATOR_API_KEY", "-------")

# Civitatis
CIVITATIS_USERNAME = os.environ.get("CIVITATIS_USERNAME", "-------")
CIVITATIS_PASSWORD = os.environ.get("CIVITATIS_PASSWORD", "-------")

# Get your guide
GETYOURGUIDE_USERNAME = os.environ.get("GETYOURGUIDE_USERNAME", "-------")
GETYOURGUIDE_PASSWORD = os.environ.get("GETYOURGUIDE_PASSWORD", "-------")


FACEBOOK_TOKEN = os.environ.get("FACEBOOK_TOKEN", "-------")

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CELERY_BEAT_SCHEDULE = {
    # "scrapercivitatis": {
    #     "task": "tour_reviews_ai.tasks.scrapercivitatis",
    #     "schedule": crontab(minute="*/30"),
    # },
    # "scrapergetyourguide": {
    #     "task": "tour_reviews_ai.tasks.scrapergetyourguide",
    #     "schedule": crontab(minute="*/30"),
    # },
    # "scraperairbnb": {
    #     "task": "tour_reviews_ai.tasks.scraperairbnb",
    #     "schedule": crontab(minute="*/30"),
    # },
    # "scraperviator": {
    #     "task": "tour_reviews_ai.tasks.scraperviator",
    #     "schedule": crontab(minute="*/30"),
    # },
    # "scrapertripadvisor": {
    #     "task": "tour_reviews_ai.tasks.scrapertripadvisor",
    #     "schedule": crontab(minute="*/30"),
    # },
    # "scraperklook": {
    #     "task": "tour_reviews_ai.tasks.scraperklook",
    #     "schedule": crontab(minute="*/30"),
    # },
    # "scraperexpedia": {
    #     "task": "tour_reviews_ai.tasks.scraperexpedia",
    #     "schedule": crontab(minute="*/30"),
    # },
    # "getcommentsfromfacebook": {
    #     "task": "tour_reviews_ai.tasks.getcommentsfromfacebook",
    #     "schedule": crontab(minute="*/20"),
    # },
    # "getcommentsfrominstagram": {
    #     "task": "tour_reviews_ai.tasks.getcommentsfrominstagram",
    #     "schedule": crontab(minute="*/20"),
    # },
    "run_background_scrapers": {
        "task": "tour_reviews_ai.tasks.run_background_scrapers",
        "schedule": crontab(minute="*/3"),
    },
    "analise_reviews": {
        "task": "tour_reviews_ai.tasks.task_analise_reviews",
        "schedule": crontab(hour="*/10"),
    },
}


# Email configuration, used to send Error Alerts
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.tourreview.com'
EMAIL_USE_SSL = False
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "-------")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "-------")

SELENIUM_GRID_HOST = env.str('SELENIUM_GRID_HOST')

NONE = 0
SMALL = 1
MEDIUM = 2
LARGE = 3
PLAN_CHOICES = [
    (NONE, 'NONE'),
    (SMALL, 'SMALL'),
    (MEDIUM, 'MEDIUM'),
    (LARGE, 'LARGE')
]

STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "-------")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "-------")
STRIPE_ENDPOINT_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET", "-------")


STRIPE_SUCCESS_URL = os.environ.get("STRIPE_SUCCESS_URL", "-------")
STRIPE_CANCEL_URL = os.environ.get("STRIPE_CANCEL_URL", "-------")

STRIPE_SMALL_PRICE_ID = os.environ.get("STRIPE_SMALL_PRICE_ID", "-------")
STRIPE_MEDIUM_PRICE_ID = os.environ.get("STRIPE_MEDIUM_PRICE_ID", "-------")
STRIPE_LARGE_PRICE_ID = os.environ.get("STRIPE_LARGE_PRICE_ID", "-------")

STRIPE_PRICES = {
    STRIPE_SMALL_PRICE_ID: SMALL,
    STRIPE_MEDIUM_PRICE_ID: MEDIUM,
    STRIPE_LARGE_PRICE_ID: LARGE,
}


PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "-------")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET", "-------")
PAYPAL_WEBHOOK_ID = os.environ.get("PAYPAL_WEBHOOK_ID", "-------")

PAYPAL_SMALL_PRICE_ID = os.environ.get("PAYPAL_SMALL_PRICE_ID", "-------")
PAYPAL_MEDIUM_PRICE_ID = os.environ.get("PAYPAL_MEDIUM_PRICE_ID", "-------")
PAYPAL_LARGE_PRICE_ID = os.environ.get("PAYPAL_LARGE_PRICE_ID", "-------")

PAYPAL_PRICES = {
    PAYPAL_SMALL_PRICE_ID: SMALL,
    PAYPAL_MEDIUM_PRICE_ID: MEDIUM,
    PAYPAL_LARGE_PRICE_ID: LARGE,
}

