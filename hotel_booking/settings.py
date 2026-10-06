import os
from pathlib import Path

import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent


# Security
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-hotel-booking-system-development-key'
)

DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]

render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)


# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
    'rooms',
    'bookings',
    'accounts',
    'contact',
]


# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise must be directly after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'hotel_booking.urls'


# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'templates',
        ],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'core.context_processors.site_info',
            ],
        },
    },
]


WSGI_APPLICATION = 'hotel_booking.wsgi.application'


# Database
# Locally: SQLite
# Render: PostgreSQL through DATABASE_URL

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'

USE_I18N = True

USE_TZ = True


# Static files
STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },

    'staticfiles': {
        'BACKEND':
        'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


# Media
MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Authentication redirects
LOGIN_URL = 'accounts:login'

LOGIN_REDIRECT_URL = 'accounts:dashboard'

LOGOUT_REDIRECT_URL = 'core:home'