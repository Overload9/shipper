"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = int(os.environ.get("DEBUG", default=0))
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(" ")

with open("version.txt") as v_file:
    SHIPPER_VERSION = v_file.read().rstrip()

MAIN_WEBSITE_URL = os.environ.get("MAIN_WEBSITE_URL", default="")
DOWNLOADS_PAGE_MAIN_BRANDING = os.environ.get("DOWNLOADS_PAGE_MAIN_BRANDING", default="Downloads")
DOWNLOADS_PAGE_DONATION_URL = os.environ.get("DOWNLOADS_PAGE_DONATION_URL", default="#")

SHIPPER_INTERNAL_PASSWORD = os.environ.get("SHIPPER_INTERNAL_PASSWORD")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'accounts',
    'shipper',
    'api',
    'drf_chunked_upload',
    'django_cleanup.apps.CleanupConfig',  # must be last in order for successful deletions
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.version_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get("SQL_ENGINE", default='django.db.backends.sqlite3'),
        'NAME': os.environ.get("SQL_DATABASE", default=os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.environ.get("SQL_USER", default="user"),
        'PASSWORD': os.environ.get("SQL_PASSWORD", default="password"),
        'HOST': os.environ.get("SQL_HOST", default="localhost"),
        'PORT': os.environ.get("SQL_PORT", default="5432"),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Media
MEDIA_URL = '/media/'
# noinspection PyUnresolvedReferences
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Login
LOGIN_REDIRECT_URL = '/maintainers/'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '50/hour',
        'user': '20/second'
    }
}

# drf-chunked-upload
DRF_CHUNKED_UPLOAD_COMPLETE_EXT = ''
DRF_CHUNKED_UPLOAD_ABSTRACT_MODEL = False
DRF_CHUNKED_UPLOAD_MAX_BYTES = 2_500_000_000   # 2.5GB


# Sentry SDK
def before_send(event, hint):
    if 'log_record' in hint:
        if hint['log_record'].name == 'django.security.DisallowedHost':
            return None
    return event


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_SDK_DSN", default=""),
    integrations=[DjangoIntegration()],
    release="{}".format(SHIPPER_VERSION),
    traces_sample_rate=1.0,
    send_default_pii=os.environ.get("SENTRY_SDK_PII", default=False),
    before_send=before_send,
)
